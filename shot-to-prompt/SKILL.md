---
name: shot-to-prompt
description: "Convert shot_spec to AI video generation prompts. Use when user wants to generate video prompts for Sora, Runway, Pika, Kling, etc. Commands: run/status/export."
---

# shot-to-prompt v0.4

将 shot_spec 转换为 AI 视频生成模型的 Prompt，建立机器可执行语言到人类可读 Prompt 的桥梁。

## 快速开始

```
/shot-to-prompt run            # 执行转换（首次运行自动初始化）
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
│   ├── shot/{chapter_id}/       # 输入源
│   └── prompt/{chapter_id}/     # 最终输出
│       ├── video_prompts.yaml
│       ├── image_prompts.yaml
│       ├── voice_prompts.yaml
│       └── asset_manifest.yaml
└── prompt/
    ├── memory/
    │   └── asset_registry.yaml   # 全局资产库
    └── runtime/{chapter_id}/     # 中间产物
```

### Step 3: 加载平台模板

根据目标平台加载对应的 Prompt 模板：
- `sora` - OpenAI Sora
- `runway` - Runway Gen-3
- `pika` - Pika Labs
- `kling` - 快手可灵
- `hailuo` - 海螺（默认）

### Step 4: 执行转换 Pipeline

**执行前必读**：
- `pipelines/run.yaml` - 定义了完整的 steps 顺序
- `references/rules/common.rule.md` - **统一规则（所有 Agent 必须遵守）**

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
| detect_shot_specs | 检查 output_dir 是否存在最终输出，未处理则处理全部 shot | {memory_dir}/pending_shot_specs.yaml |

#### 阶段 1：IR 构建

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| ir_builder | prompt_ir_builder | shot_spec + characters + scenes | prompt_ir.yaml |

#### 阶段 2-8：Prompt 处理链

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| prompt_canonical | prompt_canonical_builder | prompt_ir.yaml + mappings | prompt_canonical.yaml |
| prompt_enhancer | prompt_enhancer | prompt_ir + prompt_canonical + styles + hook_engine | prompt_enhancer.yaml |
| load_assets ⭐ | load_assets | asset_registry + prompt_ir | reusable_assets.yaml |
| prompt_asset | prompt_asset_builder | prompt_ir + reusable_assets + asset_registry | prompt_asset.yaml |
| prompt_temporal | prompt_temporal_enforcer | prompt_ir + prompt_asset | prompt_temporal.yaml |
| prompt_consistency | prompt_consistency_enforcer | prompt_ir + prompt_asset + prompt_canonical + prompt_temporal + asset_registry | prompt_consistency.yaml |
| prompt_resolver ⭐ | prompt_resolver | canonical + enhanced + asset + temporal + consistency + reusable_assets + platform_mappings | resolved_shots.yaml + final_prompts.yaml |

#### 阶段 9：多模态输出

| Step ID | Agent | 输入 | 输出文件 |
|---------|-------|------|---------|
| output_splitter ⭐ | output_splitter | resolved_shots + final_prompts + asset_registry | video_prompts.yaml + image_prompts.yaml + voice_prompts.yaml + asset_manifest.yaml |

#### 阶段 10：校验

| Step ID | Agent | 输入 | 输出 |
|---------|-------|------|------|
| validate_prompts | - | final_prompts.yaml | - |

**Agent 文件映射**：

```
ir_builder                  → agents/prompt_ir_builder.md
prompt_canonical_builder    → agents/prompt_canonical_builder.md
prompt_enhancer             → agents/prompt_enhancer.md
load_assets                 → agents/load_assets.md                     ⭐ v0.4
prompt_asset_builder        → agents/prompt_asset_builder.md
prompt_temporal_enforcer    → agents/prompt_temporal_enforcer.md
prompt_consistency_enforcer → agents/prompt_consistency_enforcer.md
prompt_resolver             → agents/prompt_resolver.md                 ⭐ v0.4 核心
output_splitter             → agents/output_splitter.md                 ⭐ v0.4
```

> ⭐ = v0.4 新增/重写模块
> ❌ 废弃：prompt_fusion.md、model_adapter.md（已合并进 prompt_resolver）

---

## Pipeline 步骤

详细执行流程见 [pipelines/run.yaml](pipelines/run.yaml)。

| Step | ID | Agent | 输入 | 输出 | 说明 |
|------|----|----|----|---|------|
| 0 | check_config | - | novel.config.md | - | 检查配置 |
| 0 | ensure_directories | - | - | - | 创建目录结构 |
| 0 | detect_shot_specs | - | output_dir | pending_shot_specs.yaml | 检测章节是否已处理（全部 shot 一起处理） |
| 1 | ir_builder | prompt_ir_builder | shot_spec + characters + scenes | prompt_ir.yaml | 编译为统一语义 IR |
| 2 | prompt_canonical | prompt_canonical_builder | prompt_ir.yaml | prompt_canonical.yaml | 规范化 IR |
| 3 | prompt_enhancer | prompt_enhancer | prompt_ir + prompt_canonical + hook_engine | prompt_enhancer.yaml | 策略增强 |
| 4 | load_assets ⭐ | load_assets | asset_registry + prompt_ir | reusable_assets.yaml | 跨章节资产加载 |
| 5 | prompt_asset | prompt_asset_builder | prompt_ir + reusable_assets + asset_registry | prompt_asset.yaml | 资产构建（支持复用） |
| 6 | prompt_temporal | prompt_temporal_enforcer | prompt_ir + prompt_asset | prompt_temporal.yaml | 时序 + 身份连续性 |
| 7 | prompt_consistency | prompt_consistency_enforcer | prompt_ir + prompt_asset + canonical + temporal + asset_registry | prompt_consistency.yaml | 一致性校验 + 自动修复 |
| 8 | prompt_resolver ⭐ | prompt_resolver | canonical + enhanced + asset + temporal + consistency + reusable_assets + platform_mappings | resolved_shots.yaml + final_prompts.yaml | 融合解析 + 平台适配 |
| 9 | output_splitter ⭐ | output_splitter | resolved_shots + final_prompts + asset_registry | video/image/voice_prompts.yaml + asset_manifest.yaml | 多模态输出拆分 |
| 10 | validate_prompts | - | final_prompts.yaml | - | 校验格式 |

> ⭐ = v0.4 新增/重写模块

---

## 目录结构

```
novels/{novel_id}/
├── output/
│   ├── shot/
│   │   └── {chapter_id}/           # shot_spec 源目录
│   │       ├── shot_spec.yaml
│   │       ├── characters.yaml
│   │       └── scenes.yaml
│   └── prompt/                     # 最终输出
│       └── {chapter_id}/
│           ├── video_prompts.yaml   # 视频生成请求
│           ├── image_prompts.yaml   # 参考图生成请求
│           ├── voice_prompts.yaml   # 配音生成请求
│           └── asset_manifest.yaml  # 资产状态汇总
└── prompt/
    ├── memory/                      # 记忆目录（跨章节持久化）
    │   ├── asset_registry.yaml      # 全局资产注册表
    │   └── pending_shot_specs.yaml  # 待处理章节记录
    └── runtime/{chapter_id}/        # 中间产物
        ├── prompt_ir.yaml            # IR 层
        ├── prompt_canonical.yaml     # 规范化层
        ├── prompt_enhancer.yaml      # 增强层
        ├── reusable_assets.yaml      # ⭐ 可复用资产清单
        ├── prompt_asset.yaml         # 资产层
        ├── prompt_temporal.yaml      # 时序层
        ├── prompt_consistency.yaml   # 一致性层
        ├── resolved_shots.yaml       # ⭐ 平台无关真相层
        ├── final_prompts.yaml        # ⭐ 平台请求层
        └── target_platform.yaml
```

> **runtime_dir**: `novels/{novel_id}/prompt/runtime/{chapter_id}/`
> **output_dir**: `novels/{novel_id}/output/prompt/{chapter_id}/`
> **memory_dir**: `novels/{novel_id}/prompt/memory/`

---

## 架构概览

### 三层架构（翻译 → 风格 → 策略）

| 层 | 作用 | 应用阶段 | 文件 |
|----|------|---------|------|
| **Mappings（翻译层）** | 让 AI "听懂" shot_spec 字段 | Canonical | `references/mappings/*.yaml` |
| **Styles（风格层）** | 让内容有统一风格/辨识度 | Enhancer | `references/styles/*.yaml` |
| **Strategies（策略层）** | 让内容能爆（hook/爽点） | Enhancer | `references/strategies/*.yaml` |

### v0.4 核心模块

| Module | 类型 | 职责 |
|--------|------|------|
| prompt_ir_builder | Builder | 将 shot_spec + characters + scenes 编译为统一语义 IR |
| prompt_canonical_builder | Builder | 将 IR 规范化为结构化 Prompt（应用 mappings） |
| prompt_enhancer | Enhancer | 注入爆点策略增强 |
| load_assets ⭐ | Loader | 跨章节资产加载（必须先于 Asset Builder） |
| prompt_asset_builder | Builder | 资产构建（支持跨章节复用：reused/derived/generated） |
| prompt_temporal_enforcer | Enforcer | 时序一致性 + 身份连续性（种子继承、漂移检测） |
| prompt_consistency_enforcer | Enforcer | 一致性校验 + 自动修复（fingerprint/reference 注入） |
| prompt_resolver ⭐ | Resolver | 融合解析 + 冲突裁决 + 平台适配（双产物输出） |
| output_splitter ⭐ | Splitter | 多模态输出拆分 + 资产使用追踪更新 |

> ⭐ = v0.4 核心模块

### v0.4 架构流程

```
shot_spec + characters + scenes
    ↓
IR Builder ────────────────────→ prompt_ir.yaml
    ↓
Canonical Builder ─────────────→ prompt_canonical.yaml
    ↓
Enhancer ──────────────────────→ prompt_enhancer.yaml
    ↓
Load Assets ⭐ ────────────────→ reusable_assets.yaml
    ↓
Asset Builder ─────────────────→ prompt_asset.yaml
    ↓
Temporal Enforcer ─────────────→ prompt_temporal.yaml
    ↓
Consistency Enforcer ──────────→ prompt_consistency.yaml
    ↓
Prompt Resolver ⭐ ───────────→ resolved_shots.yaml (平台无关)
                               → final_prompts.yaml (平台请求)
    ↓
Output Splitter ⭐ ───────────→ video_prompts.yaml
                               → image_prompts.yaml
                               → voice_prompts.yaml
                               → asset_manifest.yaml
    ↓
validate_prompts
```

### 设计原则

1. **Platform-Agnostic Core** - 核心逻辑平台无关（resolved_shots.yaml）
2. **Platform-Specific Output** - 输出适配目标平台（final_prompts.yaml）
3. **Deterministic** - 相同输入产生相同输出
4. **Composable** - 支持镜头级和章节级 Prompt
5. **Cross-Chapter Reuse** - 跨章节资产复用（asset_registry + reusable_assets）
6. **Identity Continuity** - 身份连续性保障（种子继承 + 漂移检测）
7. **Auto-Repair** - 自动修复一致性问题（fingerprint + reference 注入）

