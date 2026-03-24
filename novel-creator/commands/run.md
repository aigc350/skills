# run 命令

核心运行命令，用于生成小说章节。

## 命令格式

```
/novel-creator run [n] [--continuous] [--dry-run] [--skip-plotter]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `n` | 1 | 本次生成的章节数量 |
| `--continuous` | false | 持续运行直到目标章节完成 |
| `--dry-run` | false | 预览操作，不实际生成 |
| `--skip-plotter` | false | 跳过规划检查 |

---

## 执行流程

**采用"一章节一循环"模式：每写完一章，立即更新所有状态文件，再开始下一章。**

```
run n 的执行流程：

Step 0: 初始化检查
├── 检查/创建目录结构
└── 刷新上下文文件

循环 n 次：
├── Step 1: Plotter Agent（按需触发）
├── Step 2: Writer Agent（生成章节）
├── Step 3: Editor Agent（质量检查）
├── Step 4: Recorder Agent（状态更新）
├── Step 5: Archivist Agent（按需归档）
└── Step 6: 循环检查

优点：
- 写下一章时能参考最新状态
- 避免一次性更新过多文件导致截断
- 中途失败可从上一章恢复
```

---

## Step 0: 初始化检查

### 0.1 检查并创建目录结构

如果首次运行，创建以下目录结构：
```
novels/{novel_id}/novel/
├── state/
│   ├── state.md
│   ├── memory.md
│   ├── summary.md
│   ├── arcs.md
│   ├── canon_ext.md
│   └── checkpoint.md
├── chapters/
│   └── .backup/
└── system/
    ├── run_log.md
    └── error_log.md
```

> **说明**：state 文件使用 templates/state/ 下的模板初始化。

### 0.2 刷新上下文文件

**重要**：每次执行 run 前，必须重新读取以下文件，确保获取最新内容：

```
canon/
├── meta.md        ← 用户可能手动修改
├── world.md       ← 用户可能手动修改
├── roles.md       ← 用户可能手动修改
└── outline.md     ← 用户可能手动修改

state/
└── chapter_plan.md  ← plan 命令可能已创建/修改
```

> **原因**：用户可能在 run 之间手动修改了 canon 文件，或执行了 plan 命令。刷新确保 Agent 使用最新设定。

---

## Step 1: Plotter Agent（编剧）

**触发条件**：
- `state/chapter_plan.md` 不存在（首次运行）
- `chapter_plan.md` 中剩余未写章节 ≤ 2 章
- 或用户使用了 `--skip-plotter=false`

**执行前刷新**：重新读取 `canon/outline.md`、`canon/meta.md`，确保使用最新设定。

**执行**：调用 `agents/plotter.md`

**输入**：
- `canon/outline.md` - 故事主线
- `canon/meta.md` - 节奏类型
- `state/state.md` - 当前状态
- `state/arcs.md` - 剧情弧线
- `state/chapter_plan.md` - 当前规划

**输出**：更新 `state/chapter_plan.md`

---

## Step 2: Writer Agent（作者）

**执行前刷新**：重新读取 `state/chapter_plan.md`，确保使用最新规划。

**执行**：调用 `agents/writer.md`

**输入**：
- `canon/meta.md` - 小说配置
- `canon/roles.md` - 角色设定
- `canon/outline.md` - 故事主线
- `state/state.md` - 当前状态
- `state/chapter_plan.md` - 当前章节规划

**输出**：创建 `chapters/第{N}章_{标题}.md`

---

## Step 3: Editor Agent（编辑）

**执行**：调用 `agents/editor.md`，**使用 opus 模型**

**模型说明**：质量检查是最关键环节，opus 对设定一致性、逻辑漏洞检测能力更强。

**检查内容**：
- 设定一致性检查（角色行为、世界规则、状态连续）
- 剧情逻辑检查（剧情推进、目标完成、伏笔处理）
- 风格检查（AI痕迹、句式多样、字数达标）

**评分系统**：总分 120 分，≥90 分通过

**处理结果**：
- 通过 → 进入 Step 4
- 不通过 → 返回 Writer 重写（最多 2 次）
- 超过 2 次仍不通过 → 记录错误，暂停

---

## Step 4: Recorder Agent（记录员）

**执行**：调用 `agents/recorder.md`

**输入**：
- Editor 评分报告（从 Editor 输出中获取）

**更新文件**（分批执行）：

第一批（核心状态）：
- `state/state.md` - 当前剧情快照
- `state/memory.md` - 剧情记忆

第二批（进度状态）：
- `state/arcs.md` - 弧线进度、伏笔管理
- `state/checkpoint.md` - 检查点

第三批（扩展设定与日志）：
- `state/canon_ext.md` - 如有新增角色/势力/地点
- `system/run_log.md` - 运行日志（**包含 Editor 评分详情**）

---

## Step 5: Archivist Agent（归档员）

**触发条件**：`state/memory.md` 超过 3000 字

**执行**：调用 `agents/archivist.md`

**操作**：
- 将最早的章节压缩写入 `state/summary.md`
- 从 `state/memory.md` 中删除已压缩章节

---

## Step 6: 循环检查

```
- 未达到 n 章 → 继续下一章（从 Step 1 开始）
- 已完成 n 章 → 停止，输出总结
- 达到目标章节 → 停止并提示完成
- 异常中断 → 记录断点到 checkpoint.md，等待恢复
```

---

## 调用的 Agents

| Agent | 角色 | 文档 | 职责 |
|-------|------|------|------|
| Plotter | 编剧 | [plotter.md](../agents/plotter.md) | 章节规划、节奏控制 |
| Writer | 作者 | [writer.md](../agents/writer.md) | 章节写作、内容生成 |
| Editor | 编辑 | [editor.md](../agents/editor.md) **opus** | 质量检查、润色 |
| Recorder | 记录员 | [recorder.md](../agents/recorder.md) | 状态更新、记录剧情 |
| Archivist | 归档员 | [archivist.md](../agents/archivist.md) | 记忆压缩、归档 |

> **注**：Editor 使用 opus 模型以获得更强的检查能力，其他 Agent 使用默认模型。

---

## 错误处理

| 异常场景 | 处理方式 |
|----------|----------|
| 质量检查不通过 | 返回 Writer 重写（最多 2 次） |
| 重写超过 2 次仍不通过 | 暂停，记录 error_log.md |
| 系统崩溃/中断 | 从 checkpoint.md 恢复 |