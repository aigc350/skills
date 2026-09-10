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
└── {novel_id}/
    └── novel/              ← 小说内容目录
        └── canon/          ← init 只创建核心设定
            ├── meta.md
            ├── world.md
            ├── roles.md
            └── outline.md
```

> **说明**：state/、chapters/、system/、output/ 目录在 run 首次执行时按需创建，避免空文件。

b. **创建配置文件** `novel.config.md`

### Step 3: 新增小说初始化

a. **生成 novel_id**
- 读取 `novel.config.md` 中已有的小说数量
- 自动生成：`{题材缩写}_{三位序号}`
- 询问用户是否使用自动生成的 ID，或自定义

b. **验证 ID 唯一性**
- 检查 `novels/` 目录下是否已存在该 novel_id
- 如存在，提示用户重新输入

c. **创建目录结构**（同上）

d. **更新配置文件**
- 在 `novel.config.md` 的小说列表中添加新条目
- 更新 `current_novel_id` 为新创建的 novel_id

### Step 4: 收集核心要素

分两步完成信息收集：

#### 4.1 文本输入（直接询问）

**小说名称**：直接在对话中询问用户，等待文本输入回复。

```
AI: 请输入小说名称：
用户: 星际迷航
```

#### 4.2 选择类（使用 AskUserQuestion）

收集题材、规模、设定方式等选择题：

| 问题 | header | 选项 |
|------|--------|------|
| 题材 | 题材 | 玄幻/科幻/都市/历史/悬疑/其他 |
| 规模 | 规模 | 长篇/中篇/短篇/自定义 |
| 设定方式 | 设定 | AI推荐/选择原型/手动输入 |

**AskUserQuestion 调用示例**：

```markdown
questions:
  - question: "选择小说题材"
    header: "题材"
    options:
      - label: "玄幻"
        description: "玄幻奇幻类"
      - label: "科幻"
        description: "科幻未来类"
      - label: "都市"
        description: "都市生活类"
      - label: "历史"
        description: "历史穿越类"
      - label: "悬疑"
        description: "悬疑推理类"
      - label: "其他"
        description: "其他题材"

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
templates/canon/meta.md    → novels/{novel_id}/novel/canon/meta.md
templates/canon/world.md   → novels/{novel_id}/novel/canon/world.md
templates/canon/roles.md   → novels/{novel_id}/novel/canon/roles.md
templates/canon/outline.md → novels/{novel_id}/novel/canon/outline.md
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
- 显示 novel_id 和路径

## 完成标志

- `novels/{novel_id}/novel/canon/` 下 4 个文件已创建且有内容
- `novel.config.md` 已创建/更新
- 用户确认设定无误

## novel_id 命名规范

```
- 仅使用小写字母、数字、下划线
- 建议格式：{题材缩写}_{三位序号}
- 示例：xuanhuan_001, scifi_002, urban_003
```

## 题材缩写对照表

| 题材 | 缩写建议 |
|------|----------|
| 玄幻 | xuanhuan |
| 科幻 | scifi |
| 都市 | urban |
| 历史 | history |
| 悬疑 | mystery |
| 其他 | other |