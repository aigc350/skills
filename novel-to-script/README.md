# Novel-to-Script

将小说章节转换为剧本，支持连载、三层记忆系统和质量闭环。

## 快速开始

```
/novel-to-script run    # 执行转换（首次运行自动初始化）
```

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

## 调用链关系图

```
CHAPTER INPUT
     │
     ▼
[detect_new] ─── no new ──→ exit
     │
     ▼
[extract_scenes] ── Agent: scene_extractor ── Schema: scenes.yaml
     │
     ▼
[update_novel_memory] ── Agent: memory_updater
     │
     ▼
[write_script] ── Agent: script_writer ── Schema: script.yaml
     │
     ▼
[review] ── Agent: reviewer ── Schema: review.yaml
     │
     ├── score < 0.85 ──→ [rewrite] ──→ [review_v2]
     │                              │
     │                              ├── score < 0.85 → finalize_with_warning
     │                              └── score >= 0.85 → finalize_v2
     │
     └── score >= 0.85 ──→ [finalize]
     │
     ▼
[update_script_memory] ── Agent: memory_updater
     │
     ▼
[update_reviewer_memory] ── Agent: memory_updater
     │
     ▼
[save_output]
     │
     ▼
COMPLETE
```

---

## Pipeline 步骤

| Step | 名称 | Agent | 说明 |
|------|------|-------|------|
| 0 | check_config | - | 检查配置文件 |
| 0 | create_config | - | 创建默认配置（如不存在） |
| 0 | ensure_directories | - | 创建目录结构 |
| 0 | init_memory_files | - | 初始化记忆文件 |
| 0 | init_meta | - | 初始化 meta.yaml |
| 1 | detect_new | - | 检测新章节 |
| 2 | extract_scenes | scene_extractor | **先分析章节内容** |
| 3 | update_novel_memory | memory_updater | **基于场景提取更新记忆** |
| 4 | write_script | script_writer | 使用更新后的记忆写剧本 |
| 5 | review | reviewer | 审查质量 |
| 6 | check_score | - | 分支判断 |
| 7 | rewrite | rewriter | 重写（如需） |
| 8 | finalize | - | 输出最终版本 |
| 9 | update_script_memory | memory_updater | 更新场景层记忆 |
| 10 | update_reviewer_memory | memory_updater | 更新质量层记忆 |
| 11 | update_meta | - | 更新 meta.yaml |
| 12 | save_output | - | 保存输出 |

> **Step 0** 为初始化步骤，首次运行时自动执行。

---

## 目录结构

```
novel-to-script/
├── SKILL.md                    # 入口文件
├── README.md                   # 本文档
│
├── agents/                     # Agent 完整定义（自包含）
│   ├── scene_extractor.md      # 角色 + 指令 + 输出格式
│   ├── script_writer.md
│   ├── reviewer.md
│   ├── rewriter.md
│   └── memory_updater.md
│
├── pipelines/                  # 流程定义
│   └── run.yaml
│
├── templates/                  # 输出格式模板（强约束）
│   ├── scene.yaml
│   ├── script.yaml
│   └── memory/
│       ├── characters.yaml
│       ├── plot_state.yaml
│       ├── script_state.yaml
│       └── review_log.yaml
│
├── references/                 # 领域知识（LLM 学习用）
│   └── (暂无)
│
└── schemas/                    # 可选校验（程序用）
    ├── scenes.yaml
    ├── script.yaml
    ├── review.yaml
    └── meta.yaml
```

---

## 项目目录结构（运行时）

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

> **novel_id** 和 **novel_source_dir** 从 `novel.config.md` 读取。

---

## 职责划分

| 目录 | 角色 | 用途 |
|------|------|------|
| **agents/** | 执行者 | 完整定义（角色 + 指令 + 输出格式） |
| **templates/** | 输出约束 | LLM 必须遵守的输出格式 |
| **references/** | 知识输入 | 领域规范、格式指南、套路库 |
| **schemas/** | 程序校验 | 可选，Pipeline 自动化验证 |

---

## Memory 访问矩阵

| Memory 层 | 文件 | 读步骤 | 写步骤 |
|-----------|------|--------|--------|
| Novel Memory | characters.yaml | 2, 3, 4, 5, 7 | 3 |
| Novel Memory | plot_state.yaml | 2, 3, 4, 5, 7 | 3 |
| Script Memory | script_state.yaml | 4, 5 | 9 |
| Reviewer Memory | review_log.yaml | 5, 7 | 10 |

---

## 输出结构

```
output/script/
├── 001.md              # 章节剧本（文件名与输入一致）
├── 002.md
├── meta.yaml           # 章节元数据
└── full_script.md      # 合并的完整剧本
```

### meta.yaml 格式

```yaml
chapters:
  - chapter_id: "001"
    chapter_name: "逃离"
    create_time: "2026-03-23T18:00:00Z"
    hash: "a1b2c3d4e5f6..."
  - chapter_id: "002"
    chapter_name: "城市"
    create_time: "2026-03-23T18:30:00Z"
    hash: "f6e5d4c3b2a1..."
```

---

## 设计原则

1. **不直接生成剧本** - 必须先提取场景
2. **Memory 持续更新** - 不可重建
3. **输出必须结构化** - Markdown + YAML
4. **Reviewer 可回写** - 闭环质量控制
5. **连载增量处理** - 不全量重跑
6. **记忆更新后置** - 先分析章节，再更新记忆

---

## 扩展方向

- `pipelines/movie.yaml` - 电影剧本流程
- `pipelines/animation.yaml` - 动漫剧本流程
- 新增 agent 只需定义文件，复用现有 pipeline