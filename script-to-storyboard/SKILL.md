---
name: script-to-storyboard
description: "Convert screenplay to storyboard with shot-by-shot breakdown. Use when user wants to create storyboards from scripts, design shots, plan camera movements, or generate visual shooting guides. Commands: run/status/export."
---

# Script-to-Storyboard

将剧本转换为分镜脚本，支持镜头设计、景别规划和可视化拍摄指导。

## 快速开始

```
/script-to-storyboard run    # 执行转换（首次运行自动初始化）
```

---

## run 命令

执行 `/script-to-storyboard run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- 剧本源目录：`novels/{novel_id}/output/script/`

### Step 2: 初始化目录

确保以下目录存在：

```
novels/{novel_id}/
├── storyboard/
│   ├── memory/
│   │   ├── scene_states.yaml
│   │   └── review_log.yaml
│   └── runtime/
└── output/storyboard/
    └── {chapter_id}/
```

### Step 3: 初始化记忆文件

从 `templates/memory/` 复制模板文件（如果不存在）：
- `scene_states.yaml` → `storyboard/memory/`
- `review_log.yaml` → `storyboard/memory/`

### Step 4: 检测新剧本

扫描 `script_source_dir` 中的 `.yaml` 文件，与 `output/storyboard/` 中已处理的对比，找出未处理的剧本。

### Step 5: 执行转换 Pipeline

对每个待处理剧本执行：

1. **analyze_script** - 调用 director agent 分析剧本，确定视觉风格
2. **break_scenes** - 调用 scene_breakdown agent 拆解场景
3. **generate_storyboard** - 调用 storyboarder agent 设计分镜
4. **review** - 调用 reviewer agent 质量审查
5. **check_score** - 分支判断
6. **rewrite** - 如需要，调用 storyboarder agent 重写
7. **export** - 导出分镜到 output 目录
8. **update_memory** - 更新场景状态记忆
9. **save_output** - 合并完整分镜

### Step 6: 输出结果

显示处理统计信息。

---

## 架构概览

### Agents

| Agent | 类型 | 职责 |
|-------|------|------|
| director | Inversion | 分析剧本，确定视觉风格、节奏、重点 |
| scene_breakdown | Generator | 拆解场景为可拍摄单元 |
| storyboarder | Generator | 设计每个镜头（景别、角度、运动） |
| reviewer | Reviewer | 检查分镜可行性、逻辑连贯性 |

---

## 项目目录结构

```
novels/{novel_id}/
├── script/                     # 剧本工作目录（来自 novel-to-script）
│   ├── memory/
│   └── runtime/
├── output/
│   ├── script/                 # 剧本输出
│   └── storyboard/             # 分镜输出
│       ├── {chapter_id}/
│       │   ├── directors_notes.md
│       │   ├── scene_breakdown.yaml
│       │   ├── storyboard.md
│       │   └── overview.md
│       └── full_storyboard.md
└── storyboard/                 # 分镜工作目录
    ├── memory/
    │   ├── scene_states.yaml
    │   └── review_log.yaml
    └── runtime/
```

> **novel_id** 从 `novel.config.md` 的 `current_novel_id` 字段读取。

---

## 设计原则

1. **导演视角优先** - 先理解整体视觉风格再拆解
2. **镜头可拍摄** - 每个镜头都应可直接执行
3. **连续性追踪** - 保持场景间的逻辑连贯
4. **Review 闭环** - 质量不达标必须重写
5. **记忆递增** - 不全量重跑，增量处理

---

## Pipeline 步骤

| Step | 名称 | Agent | 说明 |
|------|------|-------|------|
| 0 | check_config | - | 检查配置文件 |
| 0 | ensure_directories | - | 创建目录结构 |
| 0 | init_memory_files | - | 初始化记忆文件 |
| 1 | detect_new | - | 检测新剧本 |
| 2 | analyze_script | director | 分析剧本，确定视觉风格 |
| 3 | break_scenes | scene_breakdown | 拆解场景为可拍摄单元 |
| 4 | generate_storyboard | storyboarder | 设计每个镜头 |
| 5 | review | reviewer | 审查质量 |
| 6 | check_score | - | 分支判断 |
| 7 | rewrite | storyboarder | 重写（如需） |
| 8 | export | - | 导出分镜文件 |
| 9 | finalize | - | 输出最终版本 |
| 10 | update_memory | - | 更新场景状态记忆 |
| 11 | save_output | - | 合并完整分镜 |

---

## 参考文档

| 文档 | 用途 |
|------|------|
| [agents/](agents/) | Agent 完整定义 |
| [pipelines/run.yaml](pipelines/run.yaml) | Pipeline 流程定义 |
| [references/](references/) | 景别、运镜领域知识 |
| [templates/](templates/) | 输出格式模板 |
| [schemas/](schemas/) | 可选校验 |
