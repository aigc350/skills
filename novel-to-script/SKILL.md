---
name: novel-to-script
description: "Convert novel chapters to screenplays with three-layer memory system. Use when user wants to adapt novels to scripts, create screenplays from fiction, transform story content to drama format, or use commands like run/status/export."
---

# Novel-to-Script

将小说章节转换为剧本，支持连载、三层记忆系统和质量闭环。

## 快速开始

```
/novel-to-script run    # 执行转换（首次运行自动初始化）
/novel-to-script run 3  # 处理指定数量章节
```

---

## 参数说明

Pipeline 执行时自动从文件名解析以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `chapter_id` | 章节序号，从文件名提取的数字 | `"1"`, `"2"`, `"10"` |
| `chapter_name` | 章节文件名（不含扩展名），用于文件路径 | `"第1章_逃离"`, `"第2章_我不会变成他们"` |

**解析逻辑**（在 `detect_new` 步骤中执行）：

使用正则 `第(\d+)章_(.+)\.md` 从文件名提取：
- `$1` → `chapter_id`（章节序号）
- 文件名去掉扩展名 → `chapter_name`

**用途说明**：

| 参数 | 用途 |
|------|------|
| `chapter_id` | 场景ID生成（`C1-S1`）、排序索引、跨章节引用 |
| `chapter_name` | 定位源文件、生成输出文件名、日志显示 |

**提取示例**：

| 文件名 | chapter_id | chapter_name |
|--------|------------|--------------|
| `第1章_逃离.md` | `"1"` | `"第1章_逃离"` |
| `第2章_我不会变成他们.md` | `"2"` | `"第2章_我不会变成他们"` |
| `第10章_沸腾.md` | `"10"` | `"第10章_沸腾"` |

**生成的文件路径**：

```
runtime/scenes_第1章_逃离.md
runtime/script_v1_第1章_逃离.md
output/script_第1章_逃离.md

# 场景ID
C1-S1, C1-S2, C1-S3...
```

---

## run 命令

执行 `/novel-to-script run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- `novel_source_dir` - 小说源目录（默认：`novels/{novel_id}/novel/chapters`）

### Step 2: 初始化目录

确保以下目录存在：

```
novels/{novel_id}/
├── script/
│   ├── memory/
│   │   ├── novel/
│   │   ├── script/
│   │   └── reviewer/
│   └── runtime/
└── output/script/
```

### Step 3: 初始化记忆文件

从 `templates/memory/` 复制模板文件（如果不存在）：
- `characters.yaml` → `script/memory/novel/`
- `plot_state.yaml` → `script/memory/novel/`
- `script_state.yaml` → `script/memory/script/`
- `review_log.yaml` → `script/memory/reviewer/`

### Step 4: 检测新章节

扫描 `novel_source_dir` 中的 `.md` 文件，与 `output/script/` 中已处理的章节对比，找出未处理的章节。

### Step 5: 执行转换 Pipeline

对每个待处理章节执行：

1. **extract_scenes** - 调用 scene_extractor agent 提取场景
2. **update_novel_memory** - 调用 memory_updater 更新小说记忆
3. **write_script** - 调用 script_writer agent 生成剧本
4. **review** - 调用 reviewer agent 质量审查
5. **rewrite** - 如需要，调用 rewriter agent 重写
6. **export_scenes** - 导出场景文件到 output 目录
7. **finalize** - 复制最终版本到 output 目录
8. **update_script_memory** - 调用 memory_updater 更新剧本记忆
9. **update_reviewer_memory** - 调用 memory_updater 更新审查记忆
10. **update_meta** - 更新 meta.yaml（包含 script_hash 和 scenes_hash）
11. **save_output** - 合并完整剧本

### Step 6: 输出结果

显示处理统计信息。

---

## 架构概览

### 三层记忆系统

```
┌─────────────────────────────────────────────────────┐
│                  MEMORY ARCHITECTURE                 │
├─────────────────────────────────────────────────────┤
│  Novel Memory    → 故事层（人物、剧情、谜题）        │
│  Script Memory   → 场景层（连续性、位置、状态）      │
│  Reviewer Memory → 质量层（评分历史、问题模式）      │
└─────────────────────────────────────────────────────┘
```

### Agents

| Agent | 类型 | 职责 |
|-------|------|------|
| scene_extractor | Generator | 提取场景，输出结构化数据 |
| script_writer | Generator | 生成剧本，保持连续性 |
| reviewer | Reviewer | 质量检查，四维度评分 |
| rewriter | Generator | 修正问题，不改变剧情 |
| memory_updater | Tool Wrapper | 更新三层记忆 |

> **注**: `planner` (Inversion) 预留用于未来多风格支持（电影/动漫/短剧）。

---

## 项目目录结构

```
novels/{novel_id}/
├── script/                     # 工作目录
│   ├── memory/
│   │   ├── novel/              # 小说记忆
│   │   ├── script/             # 剧本记忆
│   │   └── reviewer/           # 审查记忆
│   └── runtime/                # 中间产物
└── output/script/              # 最终剧本输出
```

> **novel_id** 从 `novel.config.md` 的 `current_novel_id` 字段读取。

---

## 设计原则

1. **不直接生成剧本** - 必须先提取场景
2. **Memory 持续更新** - 不可重建
3. **输出必须结构化** - Markdown + YAML
4. **Reviewer 可回写** - 闭环质量控制
5. **连载增量处理** - 不全量重跑
6. **记忆更新后置** - 先分析章节，再更新记忆

---

## Pipeline 步骤

| Step | 名称 | Agent | 说明 |
|------|------|-------|------|
| 0 | check_config | - | 检查配置文件 |
| 0 | ensure_directories | - | 创建目录结构 |
| 0 | init_memory_files | - | 初始化记忆文件 |
| 1 | detect_new | - | 检测新章节 |
| 2 | extract_scenes | scene_extractor | 先分析章节内容 |
| 3 | update_novel_memory | memory_updater | 基于场景提取更新记忆 |
| 4 | write_script | script_writer | 使用更新后的记忆写剧本 |
| 5 | review | reviewer | 审查质量 |
| 6 | check_score | - | 分支判断 |
| 7 | rewrite | rewriter | 重写（如需） |
| 8 | export_scenes | - | 导出场景文件到 output |
| 9 | finalize | - | 输出最终版本（script_${chapter_name}.md） |
| 10 | update_script_memory | memory_updater | 更新场景层记忆 |
| 11 | update_reviewer_memory | memory_updater | 更新质量层记忆 |
| 12 | update_meta | - | 更新 meta.yaml（含 chapter_id/chapter_name） |
| 13 | save_output | - | 合并完整剧本 |

---

## 参考文档

| 文档 | 用途 |
|------|------|
| [agents/](agents/) | Agent 完整定义 |
| [pipelines/run.yaml](pipelines/run.yaml) | Pipeline 流程定义 |
| [templates/](templates/) | 输出格式模板 |
| [references/](references/) | 领域知识 |
| [schemas/](schemas/) | 可选校验 |
