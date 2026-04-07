---
name: script-to-shot
description: "Convert structured scene data and screenplay to shot specifications. Use when user wants to generate shot_spec, shot character/scene definitions from novel-to-script output. Commands: run/status/export."
---

# script-to-shot v0.1

将 novel-to-script 输出的结构化场景数据（scenes.yaml）和对白数据（script.yaml）直接转换为标准化 Shot Spec（shot_spec + characters + scenes）。

**合并自 script-to-storyboard + storyboard-to-shot**，消除冗余中间产物 storyboard.md。

## 快速开始

```
/script-to-shot run             # 执行转换（首次运行自动初始化）
/script-to-shot run 1           # 指定处理第1章
/script-to-shot status          # 查看处理状态
```

---

## run 命令

执行 `/script-to-shot run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- 场景数据源目录：`novels/{novel_id}/output/script/`

### Step 2: 初始化目录

确保以下目录存在：

```
novels/{novel_id}/
├── shot/
│   ├── memory/
│   │   ├── character_states.yaml
│   │   └── review_log.yaml
│   └── runtime/
└── output/shot/
    └── {chapter_id}/
        ├── shot_spec.yaml      # 镜头规格
        ├── characters.yaml     # 角色视觉定义
        ├── scenes.yaml         # 场景视觉定义
        └── meta/
            └── consistency.yaml
```

### Step 3: 初始化记忆文件

从 `templates/memory/` 复制模板文件（如果不存在）：
- `character_states.yaml` → `shot/memory/`
- `review_log.yaml` → `shot/memory/`

### Step 4: 检测待处理章节

扫描 `output/script/` 中的 `scenes_*.yaml` 文件，与 `output/shot/` 中已处理的对比，找出未处理的章节。

### Step 5: 执行转换 Pipeline

对每个待处理章节执行（详见 [pipelines/run.yaml](pipelines/run.yaml)）：

1. **build_shots** - 调用 shot_builder agent：Beat 切分 + 镜头编译 + 对白注入
2. **resolve_characters** - 调用 character_resolver agent 解析角色视觉定义
3. **resolve_scenes** - 调用 scene_resolver agent 解析场景视觉定义
4. **check_consistency** - 调用 continuity_engine 检查跨镜头一致性
5. **review** - 质量审查
6. **check_score** - 分支判断（≥0.85 通过）
7. **revise** - 如需要，调用 shot_builder 重写
8. **export** - 导出到 output 目录
9. **update_memory** - 更新状态记忆

### Step 6: 输出结果

显示处理统计信息（总 shots、总分、处理时间）。

---

## 架构概览

### 核心数据流

```
novel-to-script 输出:
  scenes_*.yaml  ──主输入──→ ┐
  script_*.yaml  ──辅输入──→ [shot_builder] ──→ shot_spec.yaml
                                                    ↓
                              [character_resolver] → characters.yaml
                                                    ↓
                              [scene_resolver] ──→ scenes.yaml
                                                    ↓
                              [continuity_engine] → consistency.yaml
                                                    ↓
                              [review + export] → output/shot/{chapter_id}/
```

### 核心模块

| Module | 类型 | 职责 |
|--------|------|------|
| **shot_builder** ⭐ | Builder | Beat 切分 + 镜头编译 + 对白注入（替代 Director + Storyboarder + shot_compiler） |
| character_resolver | Resolver | 建立角色视觉身份（复用 storyboard-to-shot） |
| scene_resolver | Resolver | 建立场景视觉定义（复用 storyboard-to-shot） |
| continuity_engine | Engine | 控制跨镜头一致性（复用 storyboard-to-shot） |

> ⭐ = 新设计核心模块

### 设计原则

1. **Scene-First** — 以 scenes.yaml 的 production 层为主数据源
2. **Dialogue-Supplement** — 仅从 script.yaml 提取对白
3. **Beat-Driven Split** — 以 production.beats 为镜头切分依据
4. **Schema First** — 输出格式与 storyboard-to-shot 完全兼容
5. **Model-Agnostic** — 不绑定具体视频生成模型
6. **Consistency First** — 角色/场景跨镜头必须一致

---

## Pipeline 步骤

| Step | 名称 | Agent | 说明 |
|------|------|-------|------|
| 0 | check_config | - | 检查配置文件 |
| 0 | ensure_directories | - | 创建目录结构 |
| 0 | init_memory_files | - | 初始化记忆文件 |
| 0 | load_standards | - | 加载标准库 |
| 1 | detect_chapters | - | 检测待处理章节 |
| 2 | build_shots ⭐ | shot_builder | Beat 切分 + 镜头编译 + 对白注入 |
| 3 | resolve_characters | character_resolver | 角色视觉解析 |
| 4 | resolve_scenes | scene_resolver | 场景视觉解析 |
| 5 | check_consistency | continuity_engine | 连续性检查 |
| 6 | review | - | 质量审查 |
| 7 | check_score | - | 分支判断 |
| 8 | revise (if needed) | shot_builder | 重写 |
| 9 | export | - | 导出文件 |
| 10 | update_memory | - | 更新记忆 |

---

## 项目目录结构

```
.claude/skills/script-to-shot/
├── skill.md                    # 本文件
├── pipelines/
│   └── run.yaml               # Pipeline 定义
├── agents/
│   ├── shot_builder.md        # ⭐ 核心 Agent
│   ├── character_resolver.md  # 复用 storyboard-to-shot
│   ├── scene_resolver.md      # 复用 storyboard-to-shot
│   └── continuity_engine.md   # 复用 storyboard-to-shot
├── standard/                   # 标准库（复用 storyboard-to-shot）
│   ├── expression_map.yaml
│   ├── motion_map.yaml
│   ├── visual_intent.yaml
│   ├── emotion_map.yaml
│   ├── enum.yaml
│   ├── character.yaml
│   └── scene.yaml
├── schemas/                    # 输出校验（复用 storyboard-to-shot）
│   ├── shot_spec.yaml
│   ├── character_shot.yaml
│   ├── scene_shot.yaml
│   └── consistency.yaml
└── templates/
    └── memory/
        ├── character_states.yaml
        └── review_log.yaml
```

### 运行时目录

```
novels/{novel_id}/
├── output/
│   ├── script/                        # ← 输入源（novel-to-script 输出）
│   │   ├── scenes_{chapter_name}.yaml # ⭐ 主输入
│   │   └── script_{chapter_name}.yaml # 辅输入
│   └── shot/                          # → 最终输出
│       └── {chapter_id}/
│           ├── shot_spec.yaml
│           ├── characters.yaml
│           ├── scenes.yaml
│           └── meta/
│               └── consistency.yaml
├── shot/
│   ├── memory/                        # 跨章节记忆
│   │   ├── character_states.yaml
│   │   └── review_log.yaml
│   └── runtime/{chapter_id}/          # 中间产物
```

---

## 标准库

| 标准库 | 用途 |
|--------|------|
| expression_map.yaml | 表情标准定义（约 30 个表情） |
| motion_map.yaml | 动作标准定义（约 25 个动作） |
| visual_intent.yaml | 视觉意图标准定义（9 大类约 70 个枚举） |
| emotion_map.yaml | 情绪标准定义（约 20 个情绪 + expression_hints） |
| enum.yaml | 通用枚举（shot_size, pose, continuity 等） |
| character.yaml | 角色模板标准（face_id, outfits, traits） |
| scene.yaml | 场景模板标准（lighting, props, atmosphere） |

---

## 与上下游 Skill 的关系

```
novel-to-script → script-to-shot → shot-to-prompt
                   (本 Skill)       (无需修改)

已替代：
  script-to-storyboard  ← 废弃
  storyboard-to-shot    ← 废弃
```

| Skill | 关系 | 说明 |
|-------|------|------|
| novel-to-script | 上游 | 提供 scenes.yaml + script.yaml |
| script-to-storyboard | **替代** | 功能合并进 shot_builder |
| storyboard-to-shot | **替代** | shot_builder + 复用 resolvers |
| shot-to-prompt | 下游 | 输入格式完全兼容，无需修改 |

---

## 参考文档

| 文档 | 用途 |
|------|------|
| [agents/shot_builder.md](agents/shot_builder.md) | 核心 Agent 完整定义 |
| [agents/](agents/) | 其他 Agent 定义 |
| [pipelines/run.yaml](pipelines/run.yaml) | Pipeline 流程定义 |
| [standard/](standard/) | 标准库 |
| [schemas/](schemas/) | 输出校验 Schema |
