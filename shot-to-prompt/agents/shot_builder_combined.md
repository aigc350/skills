# Shot Builder Combined Agent v1.0

> 合并 Agent：IR Builder + Canonical Builder + Enhancer + Load Assets + Asset Builder + Temporal Enforcer
> 单次遍历所有镜头，输出构建产物 `prompt_built.yaml`

---

## 1. 概述

本 Agent 将 6 个构建阶段合并为单次执行，避免重复读取输入文件（从 6 次降为 1 次）。

### 合并的阶段

| # | 原始阶段 | 职责 | 在本 Agent 中的位置 |
|---|---------|------|-------------------|
| 1 | IR Builder | 编译 shot_spec → 统一语义 IR | Phase A |
| 2 | Canonical Builder | IR → 语义块（semantic blocks） | Phase B |
| 3 | Enhancer | 注入爆点策略 + 风格增强 | Phase C |
| 4 | Load Assets | 从 registry 提取可复用资产 | Phase D |
| 5 | Asset Builder | 构建资产 prompt（支持复用） | Phase E |
| 6 | Temporal Enforcer | 时序连续性 + 身份继承 | Phase F |

---

## 2. 输入

```yaml
inputs:
  # 原始输入（只读一次）
  - path: "{shot_dir}/shot_spec.yaml"
    desc: "镜头规格"
  - path: "{shot_dir}/characters.yaml"
    desc: "角色定义"
  - path: "{shot_dir}/scenes.yaml"
    desc: "场景定义"
  # 资产库
  - path: "{memory_dir}/asset_registry.yaml"
    desc: "全局资产注册表"
    required: false  # 第一章可能不存在
  # 翻译层 + 风格层
  - path: "{runtime_dir}/mappings.yaml"
    desc: "翻译映射"
    required: false
  - path: "{runtime_dir}/styles.yaml"
    desc: "风格配置"
    required: false
  - path: "references/strategies/hook_engine.yaml"
    desc: "Hook 策略引擎"
    required: false
```

---

## 3. 输出

```yaml
output: "{runtime_dir}/prompt_built.yaml"
```

`prompt_built.yaml` 结构：

```yaml
meta:
  stage: built
  version: "1.0"
  chapter_id: "{chapter_id}"
  combined_from:
    - ir_builder
    - canonical_builder
    - enhancer
    - load_assets
    - asset_builder
    - temporal_enforcer
  generated_at: "{timestamp}"
  total_shots: N

# Phase A: IR 层
ir:
  chapter_id: "..."
  shots:
    - shot_id: "C1-S1-shot1"
      subject: { character_id, variant_id, face_id, appearance, subject_state }
      location: { location_id, variant_id }
      props: [...]
      objects: [{ object_id, object_state, role }]
      intent: { type, description }
      visual_intent: { ... }
      emotion: "..."
      dialogue: "..."
      # ... 完整 IR 字段

# Phase B: Canonical 层（语义块）
canonical:
  shots:
    - shot_id: "C1-S1-shot1"
      semantic_blocks:
        subject: { semantic: {...} }
        action: { semantic: {...} }
        environment: { semantic: {...} }
        camera: { semantic: {...} }
        style: { semantic: {...} }
        quality: { semantic: {}, text: "" }
        negative: { semantic: {}, text: "" }
        final: { semantic: {}, text: "" }

# Phase C: Enhanced 层
enhanced:
  shots:
    - shot_id: "C1-S1-shot1"
      enhanced_prompt:
        text: "..."
        hooks_applied: [...]
        boost_applied: [...]

# Phase D: 可复用资产
reusable_assets:
  reusable:
    characters: [...]
    locations: [...]
    objects: [...]
  new_needed:
    characters: [...]
    locations: [...]
    objects: [...]

# Phase E: 资产层
assets:
  characters:
    - character_id: "..."
      asset_id: "..."
      source: "generated|reused|derived"
      base_prompt: "..."
      variant_prompt: "..."
      final_prompt: "..."
      appearance_fingerprint: [...]
      reference: { face_image, seed }
  locations:
    - location_id: "..."
      asset_id: "..."
      final_prompt: "..."
      anchors: [...]
  objects:
    - object_id: "..."
      asset_id: "..."
      state: "..."
      final_prompt: "..."

# Phase F: 时序层
temporal:
  shots:
    - shot_id: "C1-S1-shot1"
      previous_shot_id: null | "C1-S1-shot0"
      temporal_tags: [...]
      temporal_prompt: "..."
      identity_continuity:
        inherited_seed: N | null
        seed_source: "..." | null
        seed_locked: bool
        drift_check: { facial_features, body_proportions, clothing }
        continuity_anchors: [...]
        continuity_verified: bool
      object_state_updates: [...]
      continuity_score: 0.0-1.0
```

---

## 4. 执行流程

### 全局初始化

```
1. 读取所有输入文件（一次性）
2. 加载 asset_registry（如不存在则视为空）
3. 加载 mappings / styles / hook_engine（如不存在则使用默认）
4. 初始化上下文：
   - asset_map: {}（asset_id → 资产数据）
   - seed_registry: {}（character_id → seed）
   - prev_shot: null
```

### Phase A: IR Builder

遍历每个 shot，构建统一语义 IR：

```
FOR EACH shot IN shot_spec.shots:
  1. 提取 subject
     - character_id ← shot.actor（必填）
     - variant_id ← 从 shot_spec 或 characters.yaml 推导
     - face_id ← "{character_id}_male_v1" / "{character_id}_female_v1"
     - appearance ← 从 characters.yaml 提取服装/发型/配饰
     - subject_state ← shot.subject_state 或 "clean"

  2. 提取 location
     - location_id ← shot.location
     - variant_id ← "{location_id}_{time}_{lighting}_v1"

  3. 分类 props vs objects
     - props: 背景道具，弱一致性，无 asset_id
     - objects: 关键物品，强一致性，需要 asset_id + object_state + role

  4. 透传 intent + visual_intent + emotion + dialogue

  5. 输出 ir.shots[]
```

### Phase B: Canonical Builder

遍历每个 IR shot，构建语义块：

```
FOR EACH ir_shot IN ir.shots:
  1. 提取核心元素（actor, target）
  2. 从 intent.type 推导 action.type（查 mappings 表）
  3. 从 visual_intent + emotion 推导运动动态
  4. 构建 7 个 PromptBlock：
     - subject: { actor, target, emotion, expression }
     - action: { type, speed, intensity }
     - environment: { location, props, atmosphere }
     - camera: { shot_type, angle, movement, composition, lens, aperture, focus }
     - style: { lighting, style, atmosphere, atmosphere_intensity }
     - quality: { text: "" }  // 空壳，由 Enhancer 填充
     - negative: { text: "" }  // 空壳，由 Enhancer 填充
     - final: { text: "" }    // 空壳，由 Resolver 填充

  5. 约束：
     - semantic 只用枚举值，无自由文本
     - action.type 必须单一
     - semantic 必须完整（不依赖 IR 可独立生成 prompt）

  6. 输出 canonical.shots[]
```

### Phase C: Enhancer

遍历每个 canonical shot，注入策略和风格：

```
FOR EACH canon_shot IN canonical.shots:
  1. 从 IR 提取 genre + intensity → 计算 boost_factor
     - high → 1.3, medium → 1.0, low → 0.8

  2. 结构化增强（不拼接字符串）：
     - Emotion: 基于 subject.emotion + intensity
     - Camera: 基于 shot_type + movement
     - Lighting: 基于 environment.lighting + genre
     - Environment: 空间/氛围关键词

  3. Hook Engine 注入：
     - 确定位置（opening/middle/climax）
     - 从 hook_engine 选择匹配的 hook
     - 去重后附加为 prefix/suffix

  4. 组装 enhanced_prompt.text：
     hook.prefix + base_prompt + enhancement_keywords + hook.suffix

  5. 输出 enhanced.shots[]
```

### Phase D: Load Assets

从 asset_registry 提取可复用资产：

```
1. IF asset_registry 不存在:
     → 所有资产标记为 new_needed
     → reusable 全空
     → 跳到 Phase E

2. 遍历 IR 中出现的所有 character_id / location_id / object_id：
   - Characters: 查找 image=approved AND locked=true 的条目
     → 精确匹配 (character_id + variant_id) → reused
     → 身份匹配 (character_id only) → derived
     → 无匹配 → new
   - Locations: 查找 image=approved 的条目
     → 匹配 → reused
     → 无匹配 → new
   - Objects: 查找匹配条目
     → 匹配且 state 一致 → reused
     → 匹配但 state 不同 → derived
     → 无匹配 → new

3. 输出 reusable_assets
```

### Phase E: Asset Builder

构建资产 Prompt：

```
FOR EACH unique asset IN reusable_assets:
  1. 复用判断：
     - reused → 直接使用 registry 中的 final_prompt，不重新生成
     - derived → 继承 base_prompt，新建 variant_prompt
     - generated → 全新创建

  2. 构建 base_prompt（身份描述）：
     - 面部特征、发型、体型
     - 不含情绪、不含动作

  3. 构建 variant_prompt（变体描述）：
     - 服装、配饰、发型变化

  4. 合成 final_prompt：
     base_prompt + variant_prompt + "cinematic lighting, high detail, photorealistic, 8K resolution, consistent character design, film still quality."

  5. 构建 appearance_fingerprint（身份指纹）

  6. 分配 seed（character_id → seed 映射）：
     - 首次出现：分配新 seed（基于 character_id hash）
     - 复用：继承 registry 中的 seed

  7. 更新 asset_registry（仅 new/derived 条目）

  8. 输出 assets.characters / assets.locations / assets.objects
```

### Phase F: Temporal Enforcer

时序连续性 + 身份继承：

```
prev_shot = null

FOR EACH shot IN ir.shots (按 shot_id 排序):
  1. 获取 previous_shot_id
  2. 运动连续性：
     - IF prev_shot 存在且 motion 相关 → 注入 "continue motion from previous shot"

  3. 状态演化检测：
     - subject_state 变化（clean → dirty = subject_degradation）
     - object_state 变化（full → empty = object_consumed, intact → broken = object_destroyed）

  4. 多角色同步：
     - 主角色 → 主要动作
     - 次要角色 → 同步动作

  5. 转场注入：
     - cut / smooth / match / dramatic（基于 continuity.transition）

  6. 身份连续性（v0.4 核心）：
     - Seed 继承：从 prev_shot 继承 seed
     - 漂移检测：比较 appearance_fingerprint 维度
     - 连续锚点：继承 face_shape, eye_color, hair_style, skin_tone

  7. 构建 temporal_prompt：
     "[continuity context] [motion continuation] [state evolution] [base shot prompt] [transition]"

  8. 计算 continuity_score：
     motion*0.3 + state*0.3 + transition*0.2 + identity*0.2

  9. prev_shot = current_shot

  10. 输出 temporal.shots[]
```

### 最终输出

```
将所有 Phase 结果写入 prompt_built.yaml
```

---

## 5. 权限模型

| 字段 | 权限 |
|------|------|
| semantic | Phase B FULL, Phase C LIMITED, Phase D-F READ ONLY |
| text | Phase B placeholder, Phase C 允许增强, Phase F 允许时序 |
| quality | Phase C FULL |
| negative | Phase C FULL |
| final | Phase B-F 只创建空壳 |
| asset_registry | Phase E 可写入新条目 |

---

## 6. 性能优化

### 相比原始 Pipeline 的优势

| 维度 | 原始 Pipeline | Combined Builder |
|------|-------------|-----------------|
| 文件读取次数 | 6 次 × 200K = 1.2M | 1 次 × 200K |
| Agent 启动开销 | 6 次 | 1 次 |
| 内存传递 | 无（文件中转） | 全程内存 |
| 上下文切换 | 6 次 | 0 次 |

### 执行建议

- 单次遍历所有 shot，维护 `prev_shot` 引用用于时序
- 使用 `asset_map` 字典避免重复构建同一资产
- seed_registry 在 Phase E 初始化，Phase F 消费

---

## 7. 错误处理

| 情况 | 处理 |
|------|------|
| asset_registry 不存在 | Phase D 输出空 reusable，Phase E 全部 generated |
| mappings 不存在 | Phase B 使用内置默认映射 |
| styles 不存在 | Phase C 跳过风格增强 |
| hook_engine 不存在 | Phase C 跳过 hook 注入 |
| characters.yaml 缺少字段 | Phase A 使用 shot_spec 中的信息填充 |
| variant_id 无法推导 | 默认 `character_id + "_default_v1"` |

---

## 8. 约束

1. **单次遍历**：每个 shot 只遍历一次，所有 Phase 的处理在同一遍历中完成
2. **无文件中转**：Phase 之间通过内存传递，不写中间文件
3. **向后兼容**：输出的 `prompt_built.yaml` 包含所有原始阶段的完整数据
4. **确定性**：相同输入必须产生相同输出
5. **字段所有权不变**：各 Phase 的字段权限与独立 Agent 一致
