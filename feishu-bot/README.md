# Feishu Claude Code Bot

通过飞书消息远程控制 Claude Code 进行编程操作。

## 功能

- 📱 飞书发送消息 → Claude Code 处理 → 结果返回飞书
- 🔄 支持两种启动模式：内部模式（会话处理）和脚本模式（独立进程）
- 📂 多工程支持：配置共享，任务隔离
- ⚡ WebSocket 长连接，实时接收消息

## 安装

```bash
pip install lark_oapi
```

## 配置

在用户目录创建配置文件 `~/.claude/feishu.config.md`：

```markdown
## APP_ID
cli_xxx

## APP_SECRET
xxx
```

配置文件全局共享，多个工程可共用同一个飞书机器人。

## 启动方式

### 方式 1: 内部模式（推荐）

在 Claude Code 会话中执行：

```
/feishu-bot run
```

特点：
- 任务在当前会话处理，有完整上下文（memory、对话历史）
- 自动创建定时轮询（每10分钟检查任务文件）
- 需要保持会话活跃

其他命令：

| 命令 | 说明 |
|------|------|
| `/feishu-bot stop` | 停止监听 |
| `/feishu-bot status` | 查看运行状态 |
| `/feishu-bot logs [N]` | 查看最近 N 行日志 |

### 方式 2: 脚本模式

在没有启动 Claude Code 时，直接运行脚本：

```bash
# 启动监听（指定工程目录）
python .claude/skills/feishu-bot/scripts/manager.py start D:/project1

# 启动监听（使用当前目录）
python .claude/skills/feishu-bot/scripts/manager.py start

# 其他命令
python .claude/skills/feishu-bot/scripts/manager.py stop
python .claude/skills/feishu-bot/scripts/manager.py status
python .claude/skills/feishu-bot/scripts/manager.py logs 100
```

特点：
- 独立进程运行，不需要 Claude Code
- 消息接收后写入任务文件，等待 Claude Code 会话处理
- 适合"先收消息，等用户启动 Claude Code 后处理"的场景

## 工作原理

```
飞书消息 → listener.py → 任务文件 → Claude Code 会话 → 回复文件 → listener.py → 飞书
```

### 文件分布

```
用户目录 ~/.claude/
├── feishu.config.md         ← 共享配置（多个工程共用）
├── .feishu-bot.pid          ← 全局 PID（只有一个监听进程）
└── .feishu-bot.log          ← 全局日志

工程目录 D:/project1/
├── .feishu-bot-pending.json ← 任务文件（各工程独立）
└── .feishu-bot-reply.json   ← 回复文件
```

### listener.py 双线程

- **线程1**: WebSocket 接收飞书消息 → 写入 `.feishu-bot-pending.json`
- **线程2**: 监听 `.feishu-bot-reply.json` → 发送到飞书

### 任务文件格式

```json
{
    "chat_id": "oc_xxx",
    "sender_id": "ou_xxx",
    "text": "用户消息内容",
    "project": "D:/project1",
    "timestamp": 1234567890
}
```

## 飞书应用配置

1. 创建飞书企业自建应用
2. 开通以下权限：
   - `im:message` - 获取与发送单聊、群聊消息
   - `im:message:receive_as_bot` - 以应用身份接收用户消息
3. 配置事件订阅：
   - 添加事件 `im.message.receive_v1`
   - WebSocket 长连接模式

## 注意事项

- **单进程限制**: 全局只有一个监听进程（PID 文件在用户目录）
- **工程隔离**: 每个工程有独立的任务/回复文件
- **启动顺序**: 先启动监听，再启动 Claude Code 会话处理任务
- **代理问题**: 脚本会自动禁用代理，直连 `open.feishu.cn`

## 错误排查

如果启动失败，检查：

1. `~/.claude/feishu.config.md` 是否存在且格式正确
2. `lark_oapi` 是否已安装：`pip install lark_oapi`
3. 飞书应用是否有消息接收权限
4. 查看日志：`python manager.py logs 100`

## 文件结构

```
.claude/skills/feishu-bot/
├── SKILL.md           # Skill 定义（Claude Code 入口）
├── README.md          # 本文档
└── scripts/
    ├── listener.py    # WebSocket 监听脚本
    ├── manager.py     # 管理脚本（start/stop/status/logs）
    └── check-task.sh  # 任务检查脚本（轻量级轮询）
```