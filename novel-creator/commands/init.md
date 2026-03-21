# init 命令

项目初始化命令，用于创建小说项目结构和核心设定。

## 命令格式

```
/novel-creator init [--quick] [--template <name>]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--quick` | false | 快速模式，使用智能默认值 |
| `--template` | - | 使用指定模板初始化 |

## 执行流程

### Step 1: 检查配置文件

- 检查 `novel.config.md` 是否存在
- 如果不存在，进入"首部小说初始化"流程
- 如果存在，进入"新增小说初始化"流程

### Step 2: 首部小说初始化

a. **创建目录结构**
```
novels/
└── {小说ID}/
    └── canon/              ← init 只创建核心设定
        ├── meta.md
        ├── world.md
        ├── roles.md
        └── outline.md
```

> **说明**：state/、chapters/、system/ 目录在 run 首次执行时按需创建，避免空文件。

b. **创建配置文件** `novel.config.md`

### Step 3: 新增小说初始化

a. **生成小说ID**
- 读取 `novel.config.md` 中已有的小说数量
- 自动生成：`{题材缩写}_{三位序号}`
- 询问用户是否使用自动生成的 ID，或自定义

b. **验证 ID 唯一性**
- 检查 `novels/` 目录下是否已存在该 ID
- 如存在，提示用户重新输入

c. **创建目录结构**（同上）

d. **更新配置文件**
- 在 `novel.config.md` 的小说列表中添加新条目
- 更新 `当前小说` 为新创建的小说 ID

### Step 4: 收集核心要素

使用 AskUserQuestion 工具，**最多 2-3 轮完成所有信息收集**：

**第 1 轮：基础信息（必填）**

一次询问 3-4 个问题：
- 小说名：文本输入
- 题材：选择（玄幻/科幻/都市/历史/悬疑/其他）
- 目标规模：选择（短篇 50-100章 / 中篇 200-300章 / 长篇 500-1000章 / 自定义）

**第 2 轮：风格与设定**

根据用户选择决定问题：

| 场景 | 问题 |
|------|------|
| 选择"短篇/中篇/长篇" | 快速预设：爽文流/正剧流/轻松流（自动填充风格参数） |
| 选择"自定义" | 展开详细选项：节奏类型、叙事视角、约束级别 |

**第 3 轮（可选）：主角与主线**

提供两种模式：
- **快速模式**：AI 根据题材+风格自动生成主角和主线，用户确认
- **详细模式**：用户选择主角原型 → AI 生成主线变体 → 用户选择

```
快速模式流程：
┌─────────────────────────────────────┐
│ 是否使用 AI 推荐的主角和主线？      │
│ ○ 使用推荐（最快）                  │
│ ○ 我来选择主角原型                  │
│ ○ 我来手动输入所有设定              │
└─────────────────────────────────────┘

选择"使用推荐" → AI 生成 1 套完整设定，用户确认
选择"选择原型" → AI 生成 3 个主角原型 → 用户选择 → AI 生成主线
选择"手动输入" → 展开传统逐项收集
```

**交互优化原则**：
- 每轮最多显示 4 个问题
- 大量使用默认值，减少必填项
- 后续可通过 `plan` 或直接编辑文件调整设定
- 支持"跳过"选项，用智能默认值填充

**AskUserQuestion 调用示例**：

```markdown
# 第 1 轮：基础信息
questions:
  - question: "小说名称是什么？"
    header: "小说名"
    options: [用户手动输入]

  - question: "选择小说题材"
    header: "题材"
    options: [玄幻, 科幻, 都市, 历史, 悬疑, 其他]

  - question: "目标篇幅规模"
    header: "规模"
    options:
      - label: "长篇 (500-1000章)"
        description: "适合网文连载，百万字以上"
      - label: "中篇 (200-300章)"
        description: "中篇连载，30-60万字"
      - label: "短篇 (50-100章)"
        description: "短篇故事，10-20万字"
      - label: "自定义"
        description: "自行指定章节数和字数"

# 第 2 轮：风格选择（仅当选择预设规模时）
questions:
  - question: "选择整体风格基调"
    header: "风格"
    options:
      - label: "爽文流"
        description: "快节奏、强冲突、主角无敌"
      - label: "正剧流"
        description: "中速、有深度、成长向"
      - label: "轻松流"
        description: "慢节奏、日常向、治愈系"

# 第 3 轮：主角与主线
questions:
  - question: "如何设定主角和主线？"
    header: "设定方式"
    options:
      - label: "AI 推荐 (推荐)"
        description: "AI 根据题材和风格自动生成完整设定"
      - label: "选择原型"
        description: "从 AI 生成的原型中选择主角，再生成主线"
      - label: "手动输入"
        description: "逐步输入主角和主线设定"
```

### Step 5: 写入文件

使用模板文件初始化小说目录：

#### 5.1 调用 Creator Agent

调用 `agents/creator.md`，传入收集的信息，生成完整设定。

#### 5.2 基于模板创建文件

读取 `templates/` 目录下的模板文件，替换变量后写入目标目录：

**canon/ 目录**（使用 Creator Agent 输出填充）：
```
templates/canon/meta.md    → novels/{id}/canon/meta.md
templates/canon/world.md   → novels/{id}/canon/world.md
templates/canon/roles.md   → novels/{id}/canon/roles.md
templates/canon/outline.md → novels/{id}/canon/outline.md
```

> **说明**：state/、chapters/、system/ 目录及文件在 run 首次执行时按需创建，chapter_plan.md 在 plan 命令时创建。

#### 5.3 模板处理规则

**删除内容**：
- HTML 注释 `<!-- -->`：给 AI 的参考说明，不写入实际文件

**保留内容**：
- 文件结构（标题、分区）
- 规则部分（如"写作规则"、"约束优先级"等）
- 变量占位符 `{{variable}}`

#### 5.4 变量替换规则

模板中的 `{{variable}}` 替换为实际值：

| 模板变量 | 来源 |
|----------|------|
| `{{novel_name}}` | 用户输入 |
| `{{genre}}` | 用户选择 |
| `{{target_chapters}}` | 用户选择/计算 |
| `{{protagonist_name}}` | Creator Agent 输出 |
| `{{main_plot}}` | Creator Agent 输出 |
| `{{act1_title}}` | Creator Agent 输出 |
| ... | ... |

**处理方式**：
1. 对于 Creator Agent 输出的变量：Agent 返回时已包含具体值
2. 对于 state 初始变量：使用合理的默认值
3. 未填充的变量保留占位符，后续由用户/Agent 补充

**调用的 Agent**：
- `agents/creator.md` - 生成主角/主线/世界观设定

### Step 6: 输出初始化结果

- 显示创建的文件列表
- 显示核心设定摘要
- 显示小说 ID 和路径

## 完成标志

- `{小说ID}/canon/` 下 4 个文件已创建且有内容
- `novel.config.md` 已创建/更新
- 用户确认设定无误

## 题材缩写对照表

| 题材 | 缩写建议 |
|------|----------|
| 玄幻 | xuanhuan |
| 科幻 | scifi |
| 都市 | urban |
| 历史 | history |
| 悬疑 | mystery |
| 其他 | other |

## 小说ID命名规范

```
- 仅使用小写字母、数字、下划线
- 建议格式：{题材缩写}_{三位序号}
- 示例：xuanhuan_001, scifi_002, urban_003
```