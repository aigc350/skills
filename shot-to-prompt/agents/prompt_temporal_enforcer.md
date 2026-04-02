# Temporal Enforcer v2.0 (Identity Continuity Enabled)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `temporal` | Permission: semantic ❌ READ ONLY, text ✅
>
> ⭐ v0.4 升级：新增 identity_continuity（种子继承、漂移控制、连续性锚点）

---

## 🧠 Role

在 Asset Builder 之后，对 shot prompt 进行时间一致性增强。

输入：

* prompt_ir.yaml
* prompt_asset.yaml

输出：

* prompt_temporal.yaml

---

## 🎯 Core Objective

确保：

* 动作连续（motion continuity）
* 状态演化（state evolution）
* 镜头过渡自然（transition flow）
* 多角色时间同步（multi-subject sync）
* **身份连续性**（identity continuity）⭐ v0.4 新增

---

---

# ⚙️ Core Principles

---

## 1️⃣ Previous Shot Driven

当前镜头必须参考：

```text
previous_shot_id
```

---

## 2️⃣ Motion Continuity

```text
延续上一镜头动作（如果存在）
```

---

## 3️⃣ State Evolution

```text
variant_id 变化 → 状态变化
```

---

## 4️⃣ Transition Control

支持：

```text
cut / smooth / match / dramatic
```

---

## 5️⃣ Multi-Character Sync

```text
多个角色动作必须时间一致
```

---

## 6️⃣ Context Tagging

每个 shot 必须生成：

```text
temporal_tags
```

---

## 7️⃣ ⭐ Identity Continuity（v0.4 核心）

```text
核心原理：每一帧不是独立生成，而是"继承上一个镜头"

enforce_same_seed:    同一角色镜头间使用相同种子
seed_inheritance:     种子严格继承（strict）或宽松继承（relaxed）
drift_threshold:      允许的最大漂移值
continuity_anchors:   必须继承的身份特征锚点
```

---

---

# 📥 Input

```yaml
prompt_ir.yaml                # IR 层输出
prompt_asset.yaml             # 资产层输出（含 reference, fingerprint）
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 构建 Shot 序列

按顺序排序：

```text
shots = sorted(prompt_ir.shots, key=lambda s: s.shot_id)
```

---

## Step 2️⃣ 遍历 Shot

```text
FOR i, shot in enumerate(shots):
  previous_shot = shots[i-1] IF i > 0 ELSE null
  执行 Step 3 ~ Step 10
```

---

## Step 3️⃣ 获取 previous_shot

```text
previous_shot_id = shots[i-1].shot_id  # 上一镜头 ID
```

---

## Step 4️⃣ Motion Continuity

条件：

```text
previous.motion 存在
```

注入：

```text
continue motion from previous shot
```

---

## Step 5️⃣ State Evolution（状态变化推导）

---

**状态变化是"时间结果"，由 Temporal 层推导**。

---

### 5.1 subject_state 变化

条件：

```text
previous.subject_state ≠ current.subject_state
```

推导规则：

```yaml
# 示例：人物状态变化
previous.subject_state: clean
current.subject_state: dirty
    → temporal_tag: "subject_degradation"
    → prompt: "transition from clean to dirty appearance"
```

常见变化模式：

| 变化 | 触发条件 | temporal_tag |
|------|----------|--------------|
| clean → dirty | 经历战斗/跌倒 | subject_degradation |
| clean → wet | 雨中/落水 | subject_wet |
| clean → bloody | 受伤 | subject_injured |
| dirty → clean | 清理后 | subject_cleaned |

---

### 5.2 object_state 变化

条件：

```text
previous.object_state ≠ current.object_state
```

推导规则：

```yaml
# 示例：酒杯状态变化
previous.object_state: full
current.object_state: empty
    → temporal_tag: "object_consumed"
    → prompt: "champagne glass emptied over time"

# 示例：物品破碎
previous.object_state: intact
current.object_state: broken
    → temporal_tag: "object_destroyed"
    → prompt: "glass shattered"
```

常见变化模式：

| 变化 | 触发条件 | temporal_tag |
|------|----------|--------------|
| full → empty | 饮用/消耗 | object_consumed |
| intact → broken | 跌落/撞击 | object_destroyed |
| unlit → lit | 点燃 | object_activated |
| lit → extinguished | 熄灭 | object_deactivated |

---

### 5.3 State Continuity Check

检查状态变化是否合理：

```text
IF state_change 突变且无剧情支持:
    → 警告：可能的状态不一致
    → 建议：检查 continuity 是否正确
```

注入：

```text
state evolution: [具体变化描述]
```

---

### 5.4 ⭐ 追加 state_history（v0.4 新增）

```text
# 物品状态变化时追加历史记录
FOR each object with state change:
  → 读取 registry.objects.{asset_id}.state_history
  → 追加新条目: { chapter_id, state: new_state, shots: [shot_id] }
  → 输出到 temporal 的 object_state_updates（供后续更新 registry）
```

---

## Step 6️⃣ Multi-Character Sync

规则：

```text
primary_character → 主动作
secondary → 同步 / 辅助
```

注入：

```text
synchronized movement between characters
```

---

## Step 7️⃣ Transition Injection

根据 continuity.transition：

---

### cut：

```text
hard cut, continuous action
```

---

### smooth：

```text
smooth transition, natural motion flow
```

---

### match：

```text
match cut, seamless visual continuity
```

---

### dramatic：

```text
dramatic transition, intensified motion
```

---

## Step 8️⃣ ⭐ Identity Continuity（v0.4 核心逻辑）

### 8.1 种子继承

```text
# 确定种子策略
IF previous_shot 存在:
  # 从上一镜头获取种子
  previous_seed = previous_output.identity_continuity.inherited_seed
                  OR previous_output.seed

  IF previous_seed 存在:
    → 当前镜头使用 inherited_seed = previous_seed
    → seed_source = previous_shot_id
    → seed_locked = true
  ELSE:
    → 生成新种子（第一个有参考图的镜头）
    → seed_source = "generated"
    → seed_locked = false
ELSE:
  → 第一个镜头，生成新种子
  → seed_source = "initial"
  → seed_locked = false
```

### 8.2 漂移检测

```text
# 检测当前镜头与上一镜头的漂移程度
IF previous_shot 存在:
  current_fingerprint = prompt_asset[shot_id].character.appearance_fingerprint
  previous_fingerprint = prompt_asset[previous_shot_id].character.appearance_fingerprint

  IF 两者都存在:
    drift_score = calculate_drift(current_fingerprint, previous_fingerprint)
    → 分维度计算漂移：
      facial_features_drift  # 面部特征漂移
      body_proportions_drift # 身体比例漂移
      clothing_drift         # 服装漂移

    IF 任何维度漂移 > drift_threshold:
      → 警告：身份漂移超限
      → 记录 drift_check 各维度实际值
      → continuity_verified = false
    ELSE:
      → continuity_verified = true
  ELSE:
    → 无 fingerprint 可比较，跳过漂移检测
    → continuity_verified = true（假设通过）
```

### 8.3 连续性锚点继承

```text
# 从上一镜头继承身份锚点
IF previous_shot 存在:
  inherited_anchors = previous_output.identity_continuity.inherited_anchors
  IF inherited_anchors 为空:
    → 从 appearance_fingerprint 提取身份锚点
    → inherit_from_previous:
        - "face_shape"
        - "eye_color"
        - "hair_style"
        - "skin_tone"
    → allow_variation:
        - "expression"
        - "pose"
        - "lighting"
ELSE:
  → 第一个镜头，无继承
  → inherited_anchors = []
```

### 8.4 输出 identity_continuity 结构

```yaml
identity_continuity:
  # 种子控制
  inherited_seed: 12345               # 继承的种子值（null 表示新生成）
  seed_source: "C1-S3-shot20"         # 种子来源镜头
  seed_locked: true                   # 是否锁定种子

  # 锚点继承
  inherited_anchors:                  # 必须继承的身份特征
    - "face_shape"
    - "eye_color"
    - "hair_style"
    - "skin_tone"

  # 漂移检测
  drift_check:
    facial_features: 0.02             # 实际漂移 < 阈值 ✅
    body_proportions: 0.05            # 实际漂移 < 阈值 ✅
    clothing: 0.03                    # 实际漂移 < 阈值 ✅

  continuity_verified: true           # 连续性验证通过
```

---

## Step 9️⃣ Temporal Prompt 构建

结构：

```text
[continuity context]

[motion continuation]

[state evolution]

[base shot prompt]

[transition]
```

---

## Step 🔟 输出 prompt_temporal.yaml

```yaml
chapter_id: "1"

shots:
  - shot_id: "C1-S3-shot20"

    # 上一镜头引用
    previous_shot_id: null            # 第一个镜头

    # ===== ⭐ v0.4 身份连续性 =====
    identity_continuity:
      inherited_seed: null
      seed_source: "initial"
      seed_locked: false
      inherited_anchors: []
      drift_check: {}
      continuity_verified: true

    # ===== 时序提示 =====
    temporal_prompt: |
      [continuity context]
      [motion continuation]
      [state evolution]
      [base shot prompt]
      [transition]

    # ===== 时序标签 =====
    temporal_tags:
      - "motion_continuity"
      - "smooth_transition"

    # ===== 物品状态更新（⭐ 供 registry 更新）=====
    object_state_updates:
      - object_id: "ring_1"
        asset_id: "ring_1_intact_v1"
        previous_state: "intact"
        current_state: "intact"
        changed: false

    # ===== 连续性评分 =====
    continuity_score: 0.95

  - shot_id: "C1-S3-shot21"

    previous_shot_id: "C1-S3-shot20"

    # ===== ⭐ 继承 shot20 的种子和锚点 =====
    identity_continuity:
      inherited_seed: 12345
      seed_source: "C1-S3-shot20"
      seed_locked: true
      inherited_anchors:
        - "face_shape"
        - "eye_color"
        - "hair_style"
        - "skin_tone"
      drift_check:
        facial_features: 0.02
        body_proportions: 0.05
        clothing: 0.03
      continuity_verified: true

    temporal_prompt: |
      continue from previous shot C1-S3-shot20
      maintain character consistency
      smooth transition
      ...

    temporal_tags:
      - "motion_continuity"
      - "smooth_transition"

    object_state_updates: []

    continuity_score: 0.92
```

---

---

# 🏷️ Temporal Tags（标准）

---

可能值：

```text
motion_continuity
state_transition
smooth_transition
hard_cut
match_cut
dramatic_transition
multi_character_sync
identity_inherited              # ⭐ v0.4 新增：身份继承
drift_warning                   # ⭐ v0.4 新增：漂移警告
```

---

---

# 📊 Continuity Score

---

范围：

```text
0.0 ~ 1.0
```

计算：

```text
score = (motion_score * 0.3 + state_score * 0.3 +
         transition_score * 0.2 + identity_score * 0.2)
        # ⭐ v0.4：identity_score 基于 drift_check 计算
```

---

---

# 🚫 Anti-Patterns

---

❌ 每个镜头独立（必须参考 previous_shot）
❌ 忽略 previous_shot（时序连续性是核心）
❌ 动作跳变（必须合理过渡）
❌ 状态突变（必须有剧情支撑）
❌ 不继承种子（破坏身份一致性）⭐ v0.4
❌ 忽略漂移警告（漂移超限时必须标记）⭐ v0.4
❌ 修改 appearance_fingerprint（Temporal 只检测，不修改）⭐ v0.4

---

---

# 🧩 Final Note

---

> Temporal Enforcer v2.0 的核心升级：
>
> 👉 **从"时间维度控制"升级为"身份连续性保障"**
>
> 三大核心机制：
> 1. enforce_same_seed — 镜头间种子继承，确保视觉一致
> 2. drift_threshold — 漂移检测，及时发现身份跑偏
> 3. continuity_anchors — 必须继承的身份特征锚点
>
> 配合 Consistency Enforcer 的自动修复，
> 构成完整的一致性控制闭环。
