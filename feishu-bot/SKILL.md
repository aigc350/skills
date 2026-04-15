---
name: feishu-bot
description: 飞书 Claude Code 远程控制机器人。通过飞书消息远程调用 Claude Code 进行编程操作。支持两种启动方式：Claude Code 内部启动和 CMD 命令行启动。当用户提到"飞书机器人"、"feishu-bot"、"飞书远程编程"等相关内容时触发此技能。
---

# Feishu Claude Code Bot

通过飞书消息远程控制 Claude Code 进行编程操作。

## 文件分布

```
用户目录 ~/.claude/
├── feishu.config.md         ← 共享配置（多个工程共用）
├── .feishu-bot.pid          ← 全局 PID（只有一个监听进程）
└── .feishu-bot.log          ← 全局日志

工程目录 D:/project1/
├── .feishu-bot-pending.json ← 任务文件（各工程独立）
└── .feishu-bot-reply.json   ← 回复文件
```

## 启动方式

### 方式 1: Claude Code 内部启动

在 Claude Code 会话中启动，任务由当前会话处理：

| 命令 | 说明 |
|------|------|
| `/feishu-bot run` | 启动监听并处理任务 |
| `/feishu-bot stop` | 停止监听 |
| `/feishu-bot status` | 查看运行状态 |
| `/feishu-bot logs [N]` | 查看最近 N 行日志 |

特点：
- 任务在当前会话处理，有完整上下文（memory、对话历史）
- 需要保持会话活跃

### 方式 2: CMD 命令行启动

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
- 任务文件写入工程目录，等待 Claude Code 会话处理
- 适合"先收消息，等用户启动 Claude Code 后处理"的场景

## 工作原理

```
飞书消息 → listener.py → 任务文件 → Claude Code 会话 → 回复文件 → listener.py → 飞书
```

listener.py 双线程：
- 线程1: WebSocket 接收飞书消息 → 写入 `.feishu-bot-pending.json`
- 线程2: 监听 `.feishu-bot-reply.json` → 发送到飞书

## 内部模式实现 (run 命令)

当用户执行 `/feishu-bot run` 时，会自动完成以下步骤：

### Step 1: 启动 Listener

```bash
python .claude/skills/feishu-bot/scripts/manager.py start
```

### Step 2: 自动创建定时轮询（CronCreate）

自动调用 CronCreate 创建定时任务：
- **cron**: `*/10 * * * *` (每10分钟，cron最小粒度)
- **prompt**: 检查飞书任务文件
- **recurring**: true

实际轮询使用 ScheduleWakeup，间隔 60-120 秒，保持 prompt cache 有效。

### Step 3: 检查任务文件

任务文件: `{工程目录}/.feishu-bot-pending.json`

格式:
```json
{
    "chat_id": "oc_xxx",
    "sender_id": "ou_xxx",
    "text": "用户消息内容",
    "project": "D:/project1",
    "timestamp": 1234567890
}
```

### Step 3: 处理流程

每次唤醒时：

1. 检查 `.feishu-bot-pending.json` 是否存在
2. 读取任务，解析 `chat_id` 和 `text`
3. 删除任务文件（防止重复处理）
4. 执行任务（根据用户消息内容）
5. 写入回复文件 `.feishu-bot-reply.json`：
   ```json
   {"chat_id": "oc_xxx", "text": "处理结果"}
   ```
6. listener.py 检测到回复文件后自动发送到飞书
7. 使用 ScheduleWakeup 设置下次唤醒（60秒）

### Step 4: 循环监听

```
delaySeconds: 60
reason: 检查飞书任务文件
prompt: <<继续执行 feishu-bot 内部模式监听>>
```

---

## 配置文件

在用户目录创建配置文件 `~/.claude/feishu.config.md`：

```markdown
## APP_ID
cli_xxx

## APP_SECRET
xxx
```

配置文件全局共享，多个工程可共用同一个飞书机器人。

---

## 注意事项

- **单进程限制**: 全局只有一个监听进程（PID 文件在用户目录）
- **工程隔离**: 每个工程有独立的任务/回复文件
- **启动顺序**: 先启动监听，再启动 Claude Code 会话处理任务
- **消息前缀**: 如果要指定工程，可以在消息中包含工程名称

---

## 错误处理

如果启动失败，检查：
1. `~/.claude/feishu.config.md` 是否存在且格式正确
2. `lark_oapi` 是否已安装：`pip install lark_oapi`
3. 飞书应用是否有消息接收权限