---
name: storyboard-to-shot
description: "Convert storyboard to shot specifications and shot assets. Use when user wants to generate shot_spec, shot character/scene definitions, or shot packages from storyboards. Commands: run/status/export."
---

# storyboard-to-shot

将分镜脚本转换为标准化 Shot Spec（shot_spec + characters + scenes），建立 AI 可执行的 Shot 标准层。

## 快速开始

```
/storyboard-to-shot run    # 执行转换（首次运行自动初始化）
```

---

## run 命令

执行 `/storyboard-to-shot run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- 分镜源目录：`novels/{novel_id}/output/storyboard/`

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
        ├── scenes.yaml        # 场景视觉定义
        └── meta/
            └── consistency.yaml
```

### Step 3: 初始化记忆文件

从 `templates/memory/` 复制模板文件（如果不存在）：
- `character_states.yaml` → `shot/memory/`
- `review_log.yaml` → `shot/memory/`

### Step 4: 检测新分镜

扫描 `storyboard_source_dir` 中的 `.yaml` 文件，与 `output/shot/` 中已处理的对比，找出未处理的分镜。

### Step 5: 执行转换 Pipeline

对每个待处理分镜执行：

1. **compile_shots** - 调用 shot_compiler agent 将镜头转换为结构化 shot_spec
2. **resolve_characters** - 调用 character_resolver agent 解析角色视觉定义
3. **resolve_scenes** - 调用 scene_resolver agent 解析场景视觉定义
4. **check_consistency** - 调用 continuity_engine 检查跨镜头一致性
5. **review** - 调用 reviewer agent 质量审查
6. **check_score** - 分支判断
7. **revise** - 如需要，调用相应 agent 重写
8. **export** - 导出到 output 目录
9. **update_memory** - 更新状态记忆
10. **save_output** - 合并完整 Shot 包

### Step 6: 输出结果

显示处理统计信息。

---

## 架构概览

### 核心模块

| Module | 类型 | 职责 |
|--------|------|------|
| shot_compiler | Compiler | 将镜头转换为结构化 shot_spec |
| character_resolver | Resolver | 建立角色视觉身份 |
| scene_resolver | Resolver | 建立场景视觉定义 |
| continuity_engine | Engine | 控制跨镜头一致性 |

### 设计原则

1. **Schema First** - 所有输出必须符合结构化格式
2. **Model-Agnostic** - 不绑定具体视频生成模型
3. **Consistency First** - 角色/场景跨镜头必须一致
4. **Deterministic Output** - 相同输入必须产生相同输出

---

## 项目目录结构

```
novels/{novel_id}/
├── storyboard/                   # 分镜工作目录（来自 script-to-storyboard）
│   ├── memory/
│   └── runtime/
├── output/
│   ├── storyboard/              # 分镜输出
│   └── shot/                  # Shot 输出
│       ├── {chapter_id}/
│       │   ├── shot_spec.yaml
│       │   ├── characters.yaml
│       │   ├── scenes.yaml
│       │   └── meta/
│       │       └── consistency.yaml
│       └── full_shot.yaml
└── shot/                      # Shot 工作目录
    ├── memory/
    │   ├── character_states.yaml
    │   └── review_log.yaml
    └── runtime/
```

---

## 标准库

| 标准库 | 用途 |
|--------|------|
| expression_map.yaml | 表情标准定义 |
| character.yaml | 角色模板标准 |
| scene.yaml | 场景模板标准 |

---

## Pipeline 步骤

| Step | 名称 | Agent/Module | 说明 |
|------|------|--------------|------|
| 0 | check_config | - | 检查配置文件 |
| 0 | ensure_directories | - | 创建目录结构 |
| 0 | init_memory_files | - | 初始化记忆文件 |
| 0 | init_standard_library | - | 加载标准库 |
| 1 | detect_new | - | 检测新分镜 |
| 2 | compile_shots | shot_compiler | 镜头编译 |
| 3 | resolve_characters | character_resolver | 角色解析 |
| 4 | resolve_scenes | scene_resolver | 场景解析 |
| 5 | check_consistency | continuity_engine | 连续性检查 |
| 6 | review | reviewer | 质量审查 |
| 7 | check_score | - | 分支判断 |
| 8 | revise | (any) | 重写（如需） |
| 9 | export | - | 导出文件 |
| 10 | finalize | - | 输出最终版本 |
| 11 | update_memory | - | 更新记忆 |
| 12 | save_output | - | 合并完整输出 |

---

## 参考文档

| 文档 | 用途 |
|------|------|
| [agents/](agents/) | Agent 完整定义 |
| [pipelines/run.yaml](pipelines/run.yaml) | Pipeline 流程定义 |
| [references/](references/) | 表情、角色、场景标准库 |
| [schemas/](schemas/) | 输出校验 Schema |
| [standard/](standard/) | 行业标准模板 |
