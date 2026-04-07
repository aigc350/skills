# Prompt Resolver Agent v1.0（融合解析 + 平台适配）

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `resolver` | 替代: prompt_fusion.md + model_adapter.md
>
> ⭐ v0.4 核心模块：双产物输出（resolved_shots.yaml + final_prompts.yaml）

---

## 🧠 Role

将以下输入：

* prompt_canonical.yaml（标准化语义）
* prompt_enhancer.yaml（增强后语义）
* prompt_asset.yaml（资产绑定）
* prompt_temporal.yaml（时序状态）
* prompt_consistency.yaml（一致性校验）
* platform_mappings.yaml（平台映射配置）

输出：

* **resolved_shots.yaml**（平台无关真相层）
* **final_prompts.yaml**（平台可执行请求层）

> ⭐ v0.5 优化：内含平台选择（合并原 select_target_platform），移除 reusable_assets 独立依赖

---

## 🎯 Core Objective

1. **融合**：将所有中间层数据合并为统一镜头快照
2. **裁决**：解决数据层之间的冲突
3. **适配**：将抽象参数转换为平台特定请求
4. **追踪**：记录完整处理链路

---

## ⚙️ Core Principles

---

### 1️⃣ Single Source of Truth（唯一真相源）

resolved_shots.yaml 是所有下游（video/image/voice）的共同上游，不存在其他真相源。

### 2️⃣ Non-Destructive（非破坏性）

不删除任何原始数据，只做合并和增强。

### 3️⃣ Platform-Agnostic First（平台无关优先）

先输出平台无关的 resolved_shots.yaml，再输出平台相关的 final_prompts.yaml。

### 4️⃣ ⭐ Conflict Resolution（冲突优先级裁决）

当多个数据源对同一字段有不同值时，按优先级裁决：

```yaml
resolution_rules:
  priority_order:
    - reference_images       # 最高：参考图是已验证的外观
    - seed                   # 种子：决定生成基础
    - must_keep              # 锁定锚点：显式指定不可变
    - appearance_fingerprint # 指纹：已验证的特征集合
    - final_prompt           # 最低：文字描述最易漂移
```

---

---

# 📥 Input

```yaml
input:
  # 所有中间层数据
  - {runtime_dir}/prompt_ir.yaml              # ⭐ 用于 dialogue 原样照搬
  - {runtime_dir}/prompt_canonical.yaml
  - {runtime_dir}/prompt_enhancer.yaml
  - {runtime_dir}/prompt_asset.yaml
  - {runtime_dir}/prompt_temporal.yaml
  - {runtime_dir}/prompt_consistency.yaml

  # 配置文件
  - references/platform_mappings.yaml
  - run.yaml（default_platform 字段）  # ⭐ v0.5: 平台选择直接从配置读取
```

---

# 📤 Output

```yaml
output:
  - {runtime_dir}/resolved_shots.yaml   # 平台无关真相层
  - {runtime_dir}/final_prompts.yaml    # 平台请求层
```

---

---

# 🔁 Processing Pipeline

```text
Phase A: Resolve（融合 + 裁决）
  → 读取所有中间层数据
  → 合并为统一镜头快照
  → 冲突优先级裁决
  → 多参考优先级排序
  → 输出 resolved_shots.yaml

Phase B: Adapt（平台选择 + 映射）
  → 从 run.yaml 读取 default_platform 配置
  → 读取 platform_mappings.yaml
  → 转换抽象参数为平台特定参数
  → 应用平台规则
  → 处理参考图限制
  → 输出 final_prompts.yaml
```

---

---

# Phase A: Resolve（融合 + 裁决）

---

## Step A1：读取所有中间层

```text
FOR each shot in prompt_ir.yaml:

  收集数据：
    canonical = prompt_canonical.yaml[shot_id]
    enhanced = prompt_enhancer.yaml[shot_id]
    asset = prompt_asset.yaml[shot_id]
    temporal = prompt_temporal.yaml[shot_id]
    consistency = prompt_consistency.yaml[shot_id]
```

---

## Step A2：融合 resolved_prompt

```text
构建 resolved_prompt（平台无关文本描述）:

  subject = 合并 asset.base_prompt + asset.variant_prompt
           = 去除重复，保留身份 + 变体

  action = canonical.action.text
         = 保留原始语义，去除 emotion

  environment = canonical.environment.text
              = 场景基础描述 + lighting/atmosphere

  camera = canonical.camera.text
         = 镜头语言（保持 IR 原始语义）

  style = enhanced.style_tags（如有）
        = 风格增强词

  quality = "high detail, clean face, consistent identity"
          = 固定质量基准

  negative = canonical.negative.text
           + 从 consistency.repairs_applied 中提取一致性修复相关的负面词

  # ⭐ dialogue 原样照搬（不做转换）
  dialogue = prompt_ir[shot_id].dialogue    # 可能为空（无对白镜头）
```

---

## Step A3：⭐ 冲突优先级裁决

```text
# 收集所有裁决修复（汇总到 repairs_applied）
resolves = []

# 裁决 1：reference_images vs final_prompt
IF consistency.reference_images 存在:
  IF resolved_prompt.subject 与 reference_images 描述冲突:
    → reference_image 优先
    → 修改 resolved_prompt.subject 以匹配
    → resolves.append({ field: "subject", action: "prompt_adjusted_to_reference", value: "...", source: "consistency" })

# 裁决 2：appearance_fingerprint vs final_prompt
IF asset.appearance_fingerprint 存在:
  IF resolved_prompt.subject 与 fingerprint 冲突:
    → fingerprint 优先
    → 覆盖 resolved_prompt.subject 中的冲突部分
    → resolves.append({ field: "subject", action: "prompt_overridden_by_fingerprint", value: "...", source: "asset" })

# 裁决 3：seed 继承 vs 新种子
IF temporal.identity_continuity.inherited_seed 存在:
  → 使用 inherited_seed（不生成新种子）
  → resolves.append({ field: "seed", action: "seed_inherited", value: inherited_seed, source: "temporal" })

# 裁决 4：must_keep 绝对优先
IF consistency.must_keep 中的任何锚点被修改:
  → 恢复 must_keep 值
  → resolves.append({ field: "must_keep", action: "must_keep_restored", value: "...", source: "consistency" })
```

---

## Step A4：构建 continuity（一致性绑定）

```text
continuity:
  character_bindings:
    - 从 asset 层提取 character_id + asset_id
    - 从 consistency 层提取 must_keep 锚点
    - 从 asset registry 提取 reference.face_image

  location_bindings:                    # ✅ 统一命名
    - 从 asset 层提取 location_id + asset_id
    - 从 asset registry 提取 anchors（⚠️ 字段名必须是 `anchors`，不是 `must_keep`）
    - anchors: 场景级不可变特征（如 "crystal chandeliers", "marble floors"）

  object_bindings:
    - 从 consistency 层提取 object_id + asset_id + object_state + holder

  temporal_tags:
    - 从 temporal 层提取

  spatial_tags:
    - 从 consistency 层提取
```

---

## Step A5：构建 dramatic_focus（爽点结构化）

```text
dramatic_focus:
  hook_type = enhanced.hook_type          # 从 Enhancer 提取
  opening_beat = enhanced.opening_beat    # 开场张力
  payoff_target = enhanced.payoff_target  # 受益角色/物品
  emphasis = enhanced.emphasis            # 强调元素
```

---

## Step A6：⭐ 多参考优先级排序

```text
构建 referenced_assets（按 priority 排序）:

  FOR each asset in shot 的所有引用资产:
    - 角色 reference_images → priority = "critical"
    - 场景 reference_images → priority = "high"
    - 物品 reference_images → priority = "medium"
    - 表情/姿势 reference → priority = "medium"/"low"

  按 priority 排序: critical > high > medium > low
  附带 purpose 字段: face_identity / scene_anchor / key_prop / expression / pose
```

---

## Step A7：构建 resolver_trace（处理链追踪）

```text
resolver_trace:
  canonical: true/false        # canonical 数据是否已合并
  enhancer: true/false         # enhancer 数据是否已合并
  asset: true/false            # asset 数据是否已合并
  temporal: true/false         # temporal 数据是否已合并
  consistency: true/false      # consistency 数据是否已合并
  resolved_at: timestamp       # 裁决完成时间
  repairs_applied: resolves     # ✅ 从 Step A3 收集的裁决修复记录
```

---

## Step A8：输出 resolved_shots.yaml

```yaml
chapter_id: "1"
target_platform: "hailuo"
generated_at: "2024-01-20T12:00:00"

shots:
  - shot_id: "C1-S3-shot20"

    resolved_prompt:
      subject: string
      action: string
      environment: string
      camera: string
      style: string
      quality: string
      negative: string

    continuity:
      character_bindings: [...]
      location_bindings: [...]          # ✅ 统一命名
      object_bindings: [...]
      temporal_tags: [...]
      spatial_tags: [...]

    dramatic_focus:
      hook_type: string
      opening_beat: string
      payoff_target: [...]
      emphasis: [...]

    referenced_assets:
      - asset_id: string
        type: string
        reference_images: string
        priority: string
        purpose: string

    dialogue:                           # ⭐ 原样照搬 IR dialogue
      - speaker: string
        text: string
        type: string
        emotion: string

    resolver_trace:                     # ✅ 统一命名
      canonical: true
      enhancer: true
      asset: true
      temporal: true
      consistency: true
      resolved_at: string
      repairs_applied:
        - field: "subject"
          action: "prompt_adjusted_to_reference"
          value: "..."
          source: "consistency"
```

---

---

# Phase B: Adapt（平台适配）

---

## Step B1：读取平台映射配置

```text
读取: references/platform_mappings.yaml

获取目标平台映射:
  platform_mapping = platform_mappings[target_platform]
```

---

## Step B2：转换抽象参数

```text
# 抽象参数（从 resolved_shots 提取）
abstract_params:
  consistency_control:
    character:
      reference_strength: 0.9
      prompt_detail: "standard"
      seed_locked: true
    scene:
      reference_strength: 0.7
      prompt_detail: "standard"
    object:
      reference_strength: 0.8
      prompt_detail: "standard"

# 查找映射规则
FOR each asset_type in [character, scene, object]:
  mapping = platform_mapping.reference_param
  transform = mapping.transform

  # 应用转换函数
  IF transform == "identity":
    platform_value = reference_strength
  ELIF transform == "scale_0.9":
    platform_value = reference_strength * 0.9

  # 映射参数名
  platform_param_name = mapping.name
  # 例: hailuo → "weight", kling → "fidelity"
```

---

## Step B3：处理 prompt_detail

```text
FOR each asset_type:
  detail = abstract_params.consistency_control[asset_type].prompt_detail
  mapping = platform_mapping.prompt_detail[detail]

  # 应用映射
  IF mapping contains "suffix":
    → 在 final_prompt 后追加 suffix
  ELIF mapping contains "prompt_simplify":
    → 设置 request.prompt_simplify = true/false
  ELIF mapping contains "prompt_expand":
    → 设置 request.prompt_expand = true/false
```

---

## Step B4：应用平台规则

```text
FOR each rule in platform_mapping.platform_rules:
  IF rule.condition 满足:
    → 应用 rule.action

# 示例：runway 的规则
IF reference_strength > 0.8:
  → prompt_simplify = true

IF referenced_assets_count > max_references:
  → 按 priority 截取
```

---

## Step B5：处理参考图限制

```text
max_refs = platform_mapping.max_references
supports_priority = platform_mapping.supports_priority

IF supports_priority:
  → 按 priority 排序，取前 max_refs 个
ELSE:
  → 只取 priority = critical 和 high
  → 忽略 medium 和 low

# fallback 策略
IF 可用参考图 > max_refs:
  → 执行 platform_mapping.fallback_strategy
```

---

## Step B6：映射 seed 参数

```text
seed_config = platform_mapping.seed

# ⭐ seed_value 来源（按优先级）
IF temporal.identity_continuity.inherited_seed 存在且不为 null:
  seed_value = temporal.identity_continuity.inherited_seed
ELSE:
  # 首次出现：基于 shot_id 生成确定性种子
  seed_value = hash(shot_id) % 2147483647    # 正整数范围
  → resolves.append({ field: "seed", action: "seed_generated", value: seed_value, source: "resolver" })

seed_locked = abstract_params.consistency_control.character.seed_locked

request[{seed_config.param}] = seed_value
request[{seed_config.locked_param}] = seed_locked
```

---

## Step B7：合成 final_prompt（平台适配文本）

```text
# 基础拼接
final_prompt = join(resolved_prompt.subject, resolved_prompt.action,
                    resolved_prompt.environment, resolved_prompt.camera,
                    resolved_prompt.style, resolved_prompt.quality)

# 应用 prompt_detail 映射（如追加 suffix）
IF platform_mapping.prompt_detail[detail] has suffix:
  final_prompt += suffix

# 应用平台特定优化
IF target_platform == "runway":
  → 简化 prompt（去除冗余修饰词）
IF target_platform == "kling":
  → 扩展 prompt（增加细节描述）
IF target_platform == "pika":
  → 精简 prompt（控制长度 < 200 字符）
```

---

## Step B8：合成 request 参数

```text
# ⭐ 从 model template 读取平台默认参数
model_template = references/model/{target_platform}.yaml

request = {
  duration: model_template.request.duration           # 默认 5
  quality: model_template.request.quality              # 默认 "high"
  aspect_ratio: model_template.request.aspect_ratio    # ⭐ 从模板读取（如 "9:16"）
  prompt: final_prompt                                 # 平台适配后的 prompt
  negative_prompt: resolved_prompt.negative
  image_references: []                                 # 参考图路径（后续由 Splitter 填充）
  seed: seed_value                                     # ⭐ 从 Step B6
  # ... 平台特定参数（从 model_template 继承）
}

# ⭐ 继承 model_template 中的平台特有参数（如 style_strength）
FOR each param in model_template.request:
  IF param NOT IN [prompt, duration, quality, aspect_ratio]:
    request[param] = model_template.request[param]
```

---

```yaml
chapter_id: "1"
platform: "hailuo"
model_version: "v1.5"

shots:
  - shot_id: "C1-S3-shot20"

    final_prompt: string                 # ✅ 统一命名

    negative_prompt: string

    # 抽象参数（平台无关）
    abstract_params:
      consistency_control:
        character:
          reference_strength: 0.9
          prompt_detail: "standard"
          seed_locked: true
        scene:
          reference_strength: 0.7
          prompt_detail: "standard"
        object:
          reference_strength: 0.8
          prompt_detail: "standard"

    # 身份连续性
    identity_continuity:
      inherit_from_previous_shot: string | null
      inherited_seed: integer | null     # ⭐ 从 temporal 继承，或由 resolver 生成
      seed_locked: boolean
      drift_threshold: number
      continuity_anchors: string[]

    # 多参考优先级
    referenced_assets:
      - asset_id: string
        type: string
        reference_images: string | null
        priority: string
        purpose: string

    # ⭐ 平台映射后的请求参数（必须包含 seed 和 aspect_ratio）
    request:
      duration: integer
      aspect_ratio: string               # ⭐ 从 model template 继承（如 "9:16"）
      quality: string
      prompt: string
      negative_prompt: string
      image_references:
        - path: string
          weight: number                 # 平台映射后的值
      seed: integer                      # ⭐ 必填！从 Step B6
      seed_locked: boolean               # ⭐ 从 platform_mapping.seed.locked_param
      style_strength: number             # ⭐ 从 model template 继承
```

---

---

# 🚫 Anti-Patterns

---

❌ 修改 semantic 字段（Resolver 只读 semantic）
❌ 修改 asset_id / character_id（只能校验）
❌ 修改 state 事实（由 Temporal 控制）
❌ 跳过冲突裁决直接拼装
❌ 平台特定逻辑硬编码（应使用 platform_mappings.yaml）
❌ 在 resolved_shots 中包含平台特定参数

---

---

# 🧩 Final Note

---

> Prompt Resolver v1.0 的核心设计：
>
> 👉 **双产物架构**
> - resolved_shots.yaml = 平台无关的"真相"
> - final_prompts.yaml = 平台相关的"请求"
>
> 👉 **冲突裁决机制**
> - 5 级优先级确保一致性不被文字漂移破坏
> - reference_image > seed > must_keep > fingerprint > prompt
>
> 👉 **抽象参数 + 平台映射**
> - 一次定义，多平台适配
> - 新增平台只需添加 mapping 配置
