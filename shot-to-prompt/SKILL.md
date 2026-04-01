---
name: shot-to-prompt
description: "Convert shot_spec to AI video generation prompts. Use when user wants to generate video prompts for Sora, Runway, Pika, Kling, etc. Commands: run/status/export."
---

# shot-to-prompt

将 shot_spec 转换为 AI 视频生成模型的 Prompt，建立机器可执行语言到人类可读 Prompt 的桥梁。

## 快速开始

```
/shot-to-prompt run    # 执行转换（首次运行自动初始化）
```

---

## run 命令

执行 `/shot-to-prompt run` 时，按以下步骤执行：

### Step 1: 读取配置

读取 `novel.config.md` 获取：
- `current_novel_id` - 当前小说ID
- shot_spec 源目录：`novels/{novel_id}/output/shot/`

### Step 2: 初始化目录

确保以下目录存在：

```
novels/{novel_id}/
├── output/
│   └── prompt/
│       └── {chapter_id}/
│           ├── shot_prompt.yaml      # 镜头级 Prompt
│           └── full_prompt.yaml     # 章节级联 Prompt
└── prompt/
    └── memory/
```

### Step 3: 加载平台模板

根据目标平台加载对应的 Prompt 模板：
- `sora` - OpenAI Sora
- `runway` - Runway Gen-3
- `pika` - Pika Labs
- `kling` - 快手可灵

### Step 4: 执行转换 Pipeline

**执行前必读**：`pipelines/run.yaml` - 定义了完整的 steps 顺序

**执行原则**：
1. 按 `run.yaml` 中 `steps` 的顺序依次执行
2. 每个 step 完成后，将其输出文件写入 `runtime_dir`
3. 当前 step 的输出作为下一个 step 的输入
4. 跳过已存在的输出文件（除非源文件更新）

**执行步骤**：

#### 阶段 0：初始化

| Step ID | 操作 | 输出文件 |
|---------|------|---------|
| check_config | 读取 novel.config.md | - |
| ensure_directories | 创建目录结构 | - |
| load_mappings | 加载 references/mappings/*.yaml | {runtime_dir}/mappings.yaml |
| load_styles | 加载 references/styles/*.yaml | {runtime_dir}/styles.yaml |
| load_platform_templates | 加载 platform_templates/*.md | {runtime_dir}/platform_templates.yaml |
| detect_shot_specs | 检测 output/shot/{id}/ | {runtime_dir}/pending_shot_specs.yaml |

#### 阶段 1：IR 构建

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| ir_builder ⭐ | prompt_ir_builder | shot_spec + characters + scenes | prompt_ir.yaml |

#### 阶段 2-7：Prompt 处理链

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| prompt_canonical | prompt_canonical_builder | prompt_ir.yaml + mappings | prompt_canonical.yaml |
| prompt_enhancer | prompt_enhancer | prompt_ir + prompt_canonical + styles + hook_engine | prompt_enhanced.yaml |
| prompt_asset | prompt_asset_builder | prompt_ir + asset_registry | prompt_asset.yaml |
| prompt_consistency | prompt_consistency_enforcer | prompt_ir + prompt_asset + prompt_canonical + asset_registry | prompt_consistency.yaml |
| prompt_temporal | prompt_temporal_enforcer | prompt_ir + prompt_consistency | prompt_temporal.yaml |
| prompt_fusion | prompt_fusion | canonical + enhanced + asset + consistency + temporal | prompt_fusion.yaml |

#### 阶段 8-9：平台适配与校验

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| select_target_platform | - | - | target_platform.yaml |
| model_adapter ⭐ | model_adapter | prompt_fusion + platform_template | final_prompts.yaml |
| validate_prompts | - | final_prompts.yaml | - |

**Agent 文件映射**：

```
ir_builder              → agents/prompt_ir_builder.md
prompt_canonical_builder → agents/prompt_canonical_builder.md
prompt_enhancer         → agents/prompt_enhancer.md
prompt_asset_builder    → agents/prompt_asset_builder.md
prompt_consistency_enforcer → agents/prompt_consistency_enforcer.md
prompt_temporal_enforcer → agents/prompt_temporal_enforcer.md
prompt_fusion           → agents/prompt_fusion.md
model_adapter           → agents/model_adapter.md
```

执行每个 step 时：
1. 读取对应 agent 的 .md 文件
2. 按照其定义的输入/输出规范处理数据
3. 应用其中定义的 transformation rules
4. 输出结果到指定文件

---

## Pipeline 步骤

详细执行流程见 [pipelines/run.yaml](pipelines/run.yaml)。

| Step | ID | Agent | 输入 | 输出 | 说明 |
|------|----|----|----|---|---|
| 0 | check_config | - | novel.config.md | - | 检查配置 |
| 0 | ensure_directories | - | - | - | 创建目录结构 |
| 0 | load_mappings | - | references/mappings/*.yaml | mappings.yaml | 加载翻译层 |
| 0 | load_styles | - | references/styles/*.yaml | styles.yaml | 加载风格层 |
| 0 | load_platform_templates | - | platform_templates/*.md | platform_templates.yaml | 加载平台模板 |
| 0 | detect_shot_specs | - | output/shot/{id}/ | pending_shot_specs.yaml | 检测待处理文件 |
| 1 | ir_builder | ir_builder ⭐ | shot_spec + characters + scenes | prompt_ir.yaml | 编译为统一语义 IR |
| 2 | prompt_canonical | prompt_canonical_builder | prompt_ir.yaml + mappings | prompt_canonical.yaml | 规范化 IR + 翻译 |
| 3 | prompt_enhancer | prompt_enhancer | prompt_ir + prompt_canonical + styles + hook_engine | prompt_enhanced.yaml | 策略增强 + 风格 |
| 4 | prompt_asset | prompt_asset_builder | prompt_ir + asset_registry | prompt_asset.yaml | 资产构建 |
| 5 | prompt_consistency | prompt_consistency_enforcer | prompt_ir + prompt_asset + prompt_canonical + asset_registry | prompt_consistency.yaml | 一致性强制 |
| 6 | prompt_temporal | prompt_temporal_enforcer | prompt_ir + prompt_consistency | prompt_temporal.yaml | 时序处理 |
| 7 | prompt_fusion | prompt_fusion | canonical + enhanced + asset + consistency + temporal | prompt_fusion.yaml | 融合各层 IR |
| 8 | model_adapter | model_adapter ⭐ | prompt_fusion + platform_template | final_prompts.yaml | 平台适配 |
| 9 | validate_prompts | - | final_prompts.yaml | - | 校验格式 |

> ⭐ = 核心模块

---

## 目录结构

```
novels/{novel_id}/
├── output/
│   └── shot/
│       └── {chapter_id}/           # shot_spec 源目录
│           ├── shot_spec.yaml
│           ├── characters.yaml
│           └── scenes.yaml
│   └── prompt/                    # 最终输出
│       └── {chapter_id}/
│           ├── shot_prompt.yaml   # 镜头级 Prompt
│           └── full_prompt.yaml  # 章节级联 Prompt
└── prompt/
    ├── memory/                    # 记忆目录
    │   └── asset_registry.yaml    # 资产注册表
    └── runtime/{chapter_id}/       # 中间产物
        ├── mappings.yaml           # 翻译层加载结果
        ├── styles.yaml            # 风格层加载结果
        ├── platform_templates.yaml
        ├── pending_shot_specs.yaml
        ├── prompt_ir.yaml          # IR 层
        ├── prompt_canonical.yaml   # 规范化层（应用 mappings）
        ├── prompt_enhanced.yaml    # 增强层
        ├── prompt_asset.yaml       # 资产层
        ├── prompt_consistency.yaml # 一致性层
        ├── prompt_temporal.yaml    # 时序层
        ├── prompt_fusion.yaml      # 融合层
        ├── target_platform.yaml
        ├── final_prompts.yaml      # 最终输出
        ├── chapter_prompts.yaml
        └── video_task_list.yaml
```

> **runtime_dir**: `novels/{novel_id}/prompt/runtime/{chapter_id}/`
> **output_dir**: `novels/{novel_id}/output/prompt/`

---

## 架构概览

### 三层架构（翻译 → 风格 → 策略）

| 层 | 作用 | 应用阶段 | 文件 |
|----|------|---------|------|
| **Mappings（翻译层）** | 让 AI "听懂" shot_spec 字段 | Canonical | `references/mappings/*.yaml` |
| **Styles（风格层）** | 让内容有统一风格/辨识度 | Enhancer | `references/styles/*.yaml` |
| **Strategies（策略层）** | 让内容能爆（hook/爽点） | Enhancer | `references/strategies/*.yaml` |

### 核心模块（⭐）

| Module | 类型 | 职责 |
|--------|------|------|
| ir_builder ⭐ | Builder | 将 shot_spec + characters + scenes 编译为统一语义 IR |
| prompt_canonical_builder | Builder | 将 IR 规范化为结构化 Prompt（应用 mappings） |
| prompt_enhancer | Enhancer | 注入爆点策略增强 |
| prompt_asset_builder | Builder | 构建 prompt 资产库 |
| prompt_consistency_enforcer | Enforcer | 确保跨镜头一致性 |
| prompt_temporal_enforcer | Enforcer | 时序一致性处理 |
| prompt_fusion | Fusion | 融合各层 IR |
| model_adapter ⭐ | Adapter | 针对目标平台优化 Prompt |

### 架构流程

```
shot_spec + characters + scenes
    ↓
IR Builder
    ↓
prompt_ir.yaml（统一语义层）
    ↓
┌───────────────────────────────────────────────┐
│  Canonical（规范化 + Mappings 翻译）           │
└───────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────┐
│  Enhancer（策略增强 + Styles 风格层）          │
│  - hook 爆点策略                              │
│  - short_drama / cinematic 风格               │
└───────────────────────────────────────────────┘
    ↓
Asset（资产构建：角色/场景/道具）
    ↓
Consistency（跨镜头一致性）
    ↓
Temporal（时序连续性）
    ↓
Fusion（融合所有层）
    ↓
Model Adapter（平台适配：Sora/Runway/Pika/Kling/Hailuo）
    ↓
final_prompts.yaml
    ↓
validate_prompts
```

### 设计原则

1. **Platform-Agnostic Core** - 核心逻辑平台无关
2. **Platform-Specific Output** - 输出适配目标平台
3. **Deterministic** - 相同输入产生相同输出
4. **Composable** - 支持镜头级和章节级 Prompt
