# Novel Creator

AI 自动小说创作系统 - 支持长篇小说（1000+ 章节）持续创作。

## 特性

- **稳定长篇写作** - 通过多级记忆机制避免 AI 遗忘剧情
- **角色一致性** - 角色行为约束，防止角色崩坏
- **世界观一致** - 严格遵守 canon 设定，避免设定冲突
- **自动剧情管理** - 伏笔追踪、支线管理、节奏控制
- **质量保证** - 多轮检查润色，减少 AI 写作痕迹
- **异常恢复** - 支持从断点恢复，不丢失进度
- **多小说管理** - 支持同一项目下管理多部小说

## 安装

将整个 `novel-creator` 目录复制到项目的 `.claude/skills/` 下：

```
your-project/
└── .claude/
    └── skills/
        └── novel-creator/    ← 复制到这里
            ├── skill.md       # 入口文件
            ├── commands/      # 命令处理器
            ├── agents/        # AI 执行器
            └── templates/     # 文件模板
```

## 快速开始

### 1. 初始化项目

```
/novel-creator init
```

系统会通过 **2-3 轮交互** 完成设置（优化后）：
- **第1轮**：小说名称 + 题材 + 目标规模
- **第2轮**：风格选择（爽文流/正剧流/轻松流）
- **第3轮**：主角与主线（可选 AI 推荐）

> init 只创建 canon/ 核心设定，轻量化初始化。

### 2. 规划章节（可选）

```
/novel-creator plan
```

手动规划章节，创建 `state/chapter_plan.md`。也可直接 run，系统会自动规划。

### 3. 生成章节

```
/novel-creator run        # 生成 1 章
/novel-creator run 5      # 生成 5 章
/novel-creator run --continuous  # 持续运行直到完成
```

> run 首次执行时会自动创建 state/、chapters/、system/ 目录。

### 4. 查看状态

```
/novel-creator status
```

## 命令列表

| 命令 | 说明 | 详细文档 |
|------|------|----------|
| `init` | 初始化项目 | [commands/init.md](commands/init.md) |
| `list` | 列出所有小说 | [commands/list.md](commands/list.md) |
| `switch <ID>` | 切换当前小说 | [commands/switch.md](commands/switch.md) |
| `run [n]` | 生成 n 章小说 | [commands/run.md](commands/run.md) |
| `status` | 查看项目状态 | [commands/status.md](commands/status.md) |
| `plan` | 手动规划章节 | [commands/plan.md](commands/plan.md) |
| `revise <章节号>` | 修订指定章节 | [commands/revise.md](commands/revise.md) |
| `export` | 导出小说文件 | [commands/export.md](commands/export.md) |
| `validate` | 校验一致性 | [commands/validate.md](commands/validate.md) |

## 架构设计

### 模块化结构

```
novel-creator/
├── skill.md                    # 入口文件（命令路由）
│
├── commands/                   # 命令处理器（流程编排）
│   ├── init.md                # 初始化流程
│   ├── run.md                 # 写作流程
│   ├── list.md                # 列表查询
│   ├── switch.md              # 切换小说
│   ├── status.md              # 状态查询
│   ├── plan.md                # 手动规划
│   ├── revise.md              # 章节修订
│   ├── export.md              # 导出功能
│   └── validate.md            # 一致性校验
│
├── agents/                     # AI 执行器（创造性任务）
│   ├── creator.md             # 创作者 - 设定生成
│   ├── plotter.md             # 编剧 - 章节规划
│   ├── writer.md              # 作者 - 章节写作
│   ├── editor.md              # 编辑 - 质量检查
│   ├── recorder.md            # 记录员 - 状态记录
│   └── archivist.md           # 归档员 - 记忆归档
│
├── templates/                  # 文件模板
│   ├── canon/                 # 固定设定模板
│   ├── state/                 # 运行状态模板
│   ├── chapters/              # 章节目录模板
│   └── system/                # 系统文件模板
│
└── README.md                   # 本说明文件
```

### Commands vs Agents

| 组件 | 职责 | 说明 |
|------|------|------|
| **commands/** | 流程编排 | 参数解析、文件操作、状态管理、调用 agents |
| **agents/** | AI 推理 | 创造性任务、内容生成、质量评估 |

**调用关系**：
```
用户命令 → skill.md → commands/*.md → agents/*.md
```

## 项目目录结构

初始化后的项目结构：

```
novels/
├── xuanhuan_001/               # 小说 ID
│   ├── canon/                  # 固定设定（人工维护）
│   │   ├── meta.md             # 小说元数据（信息、配置、写作规则）
│   │   ├── world.md            # 世界观设定
│   │   ├── roles.md            # 角色设定
│   │   └── outline.md          # 故事主线
│   │
│   ├── state/                  # 运行状态（AI 自动维护）
│   │   ├── state.md            # 当前剧情快照
│   │   ├── memory.md           # 剧情记忆（最近 20 章）
│   │   ├── summary.md          # 长期剧情总结
│   │   ├── arcs.md             # 剧情弧线
│   │   ├── chapter_plan.md     # 未来章节规划
│   │   ├── canon_ext.md        # 扩展设定
│   │   └── checkpoint.md       # 运行检查点
│   │
│   ├── chapters/               # 小说正文
│   │   ├── chapter_001_xxx.md
│   │   └── .backup/            # 章节备份
│   │
│   └── system/                 # 系统文件
│       ├── run_log.md          # 运行日志
│       └── error_log.md        # 异常日志
│
└── novel.config.md             # 小说项目配置
```

## 核心概念

### canon（固定设定）

人工维护的核心设定，AI 只能读取，不能修改：

- **meta.md** - 小说元数据（基本信息、写作配置、写作规则）
- **world.md** - 世界观规则
- **roles.md** - 角色设定和行为约束
- **outline.md** - 故事主线结构

### state（运行状态）

AI 自动维护的运行时状态：

- **state.md** - 当前剧情快照，确保连续性
- **memory.md** - 短期记忆，保留最近 20 章
- **summary.md** - 长期记忆，历史剧情压缩总结
- **arcs.md** - 管理主线阶段、支线、伏笔
- **canon_ext.md** - 动态扩展的角色、势力、地点

### Agents（AI 角色）

六个协作的 AI Agent，模拟真实小说创作团队：

| Agent | 角色 | 职责 | 调用场景 |
|-------|------|------|----------|
| **Creator** | 创作者 | 生成主角、主线、世界观设定 | init 命令 |
| **Plotter** | 编剧 | 规划未来 5-10 章剧情 | run/plan 命令 |
| **Writer** | 作者 | 根据规划生成章节内容 | run/revise 命令 |
| **Editor** **opus** | 编辑 | 质量检查、润色、打回重写 | run/revise 命令 |
| **Recorder** | 记录员 | 更新剧情记录、维护状态文件 | run/revise 命令 |
| **Archivist** | 归档员 | 压缩历史剧情、归档记忆 | 按需触发 |

> **注**：Editor 使用 opus 模型以获得更强的检查能力，其他 Agent 使用默认模型。

### 角色协作图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          初始化阶段 (init)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    用户输入 ──→ Creator ──→ 生成 canon/ 设定文件                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        写作阶段 (run/revise)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐                   │
│    │ Plotter │ ───→ │ Writer  │ ───→ │ Editor  │                   │
│    │  编剧   │      │  作者   │      │  编辑   │                   │
│    └─────────┘      └─────────┘      └────┬────┘                   │
│         ↑                                │                         │
│         │         ┌──────────────────────┼──────────────────┐      │
│         │         ↓                      ↓                  ↓      │
│         │    ┌─────────┐           ┌─────────┐        ┌─────────┐  │
│         └────│ Recorder│           │  通过   │        │ 不通过  │  │
│              │ 记录员  │           └────┬────┘        └────┬────┘  │
│              └────┬────┘                │                  │       │
│                   │                     ↓                  ↓       │
│                   │              进入下一章          返回 Writer   │
│                   │                                (最多2次)       │
│                   ↓                                                │
│              ┌─────────┐                                           │
│              │Archivist│  ← memory.md 超过 3000 字时触发           │
│              │ 归档员  │                                           │
│              └─────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

数据流向：

  canon/          ──→  只读，所有 Agent 参考
  state/          ←──  Recorder 写入，Archivist 压缩
  chapters/       ←──  Writer 写入，Editor 润色
```

## 约束优先级

当设定出现冲突时，按以下优先级处理：

```
canon/*              ← 最高优先级
canon_ext.md
arcs.md
state.md
meta.md              ← 最低优先级
```

## 常见问题

### Q: 如何修改已生成的章节？

使用 `revise` 命令：
```
/novel-creator revise 21
```

系统会备份原章节并重新生成。

### Q: 如何添加新角色？

两种方式：
1. 直接编辑 `canon/roles.md`（推荐）
2. 在写作中自然引入，AI 会自动追加到 `canon_ext.md`

### Q: 如何查看伏笔状态？

查看 `state/arcs.md` 中的伏笔管理部分，或使用：
```
/novel-creator status
```

### Q: 生成中断了怎么办？

使用 `validate` 检查状态，或直接运行 `run` 继续：
```
/novel-creator validate
/novel-creator run
```

### Q: 如何管理多部小说？

```
/novel-creator list              # 列出所有小说
/novel-creator switch scifi_002  # 切换到指定小说
/novel-creator init              # 创建新小说
```

## 注意事项

1. **canon 文件需人工维护** - AI 不会修改 `canon/` 目录下的文件
2. **定期备份** - 重要修改前建议备份整个 `novels/` 目录
3. **检查伏笔** - 使用 `status` 或 `validate` 检查是否有伏笔长期未推进
4. **上下文限制** - 超长小说会自动压缩历史剧情到 `summary.md`

## 模板变量

模板文件中使用 `{{variable_name}}` 格式的变量。

### init 时填充（canon/ 目录）

| 变量 | 说明 |
|------|------|
| `{{novel_name}}` | 小说名称 |
| `{{genre}}` | 题材类型 |
| `{{target_chapters}}` | 目标章节数 |
| `{{target_words}}` | 目标字数 |
| `{{chapter_words}}` | 每章字数 |
| `{{pace_type}}` | 节奏类型（快/中/慢） |
| `{{narrative_perspective}}` | 叙事视角（第一人称/第三人称） |
| `{{writing_style}}` | 写作风格描述 |
| `{{constraint_level}}` | 约束级别（强/中/弱） |
| `{{protagonist_name}}` | 主角名称 |
| `{{protagonist_identity}}` | 主角身份 |
| `{{protagonist_personality}}` | 主角性格 |
| `{{protagonist_goal}}` | 主角目标 |
| `{{main_plot}}` | 故事主线 |
| `{{volume_structure}}` | 分卷结构（可选，长篇小说使用） |

### 运行时动态生成（state/ 目录）

state/ 目录下的文件由 AI 在运行过程中自动维护，模板只提供结构和格式指引：
- `state.md` - 由 Recorder Agent 更新
- `memory.md` - 由 Recorder Agent 追加
- `summary.md` - 由 Archivist Agent 压缩
- `arcs.md` - 由 Recorder Agent 更新
- `chapter_plan.md` - 由 Plotter Agent 生成
- `canon_ext.md` - 由 Recorder Agent 追加

## 版本

- 版本：1.2.6
- 适用于：Claude Code
- 支持的小说长度：1000+ 章节

## 更新日志

### v1.2.6
- 优化 init 命令：只创建 canon/ 目录，轻量化初始化
- 优化 plan 命令：负责创建 state/ 目录和 chapter_plan.md
- 优化 run 命令：首次运行时创建 state/chapters/system 目录
- 添加文件刷新机制：run 前重新读取 canon 和 chapter_plan.md，确保使用最新内容
- 实现双模型检查策略：Writer 使用 sonnet，Editor 使用 opus
- 添加模型策略说明和推荐模型文档
- 优化质量检查环节，使用 opus 提升检测能力
- 合并 config.md 和 writing_rules.md 为 meta.md（小说元数据）
- meta.md 统一管理基本信息、写作配置和写作规则
- 简化模板结构，减少文件数量
- 更新所有 Agent 和 Command 中的文件引用
- 优化 templates 模板，移除题材相关固定属性
- world.md 简化为核心框架 + 题材扩展块
- roles.md "能力系统"改为更通用的"个人特质"
- Creator Agent 输出格式与模板对齐，提供各题材扩展示例
- 简化 state 模板：减少模板变量，AI 动态维护内容更清晰
- arcs.md 引用 outline.md 避免重复存储
- chapter_plan.md 简化为格式模板，由 Plotter 动态规划

### v1.2.2
- 明确 templates 目录使用流程
- 更新 init.md 模板处理步骤
- 更新 Creator Agent 输出格式与模板对齐

### v1.2.1
- 重命名 Agent：chronicler → recorder（记录员）、librarian → archivist（归档员）
- 新增角色协作图，清晰展示 Agent 间调用关系

### v1.2.0
- 拆分 quality.md 为三个独立 Agent：editor、recorder、archivist
- 重命名 planner → plotter，职责更清晰
- 使用小说创作团队角色命名（创作者/编剧/作者/编辑/记录员/归档员）
- 更新所有命令的 Agent 调用链

### v1.1.0
- 重构为模块化架构（commands/agents 分离）
- 优化 init 命令交互流程（6 轮 → 2-3 轮）
- 新增 Creator Agent 用于设定生成
- 新增多小说管理命令（list/switch）
- 精简 skill.md 入口文件

### v1.0.0
- 初始版本

## License

MIT License