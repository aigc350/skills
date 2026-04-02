# Consistency Enforcer v2.0 (Auto-Repair Enabled)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `consistency` | Permission: semantic ❌ READ ONLY, text ⚠️ 可修复
>
> ⭐ v0.4 升级：新增自动修复能力（fingerprint 补充、冲突覆盖、reference 注入、ID 纠正）

---

## 🧠 Role

将以下输入：

* prompt_ir.yaml（语义层）
* prompt_asset.yaml（资产层）
* prompt_canonical.yaml（标准化层）
* prompt_temporal.yaml（时序层）
* asset_registry.yaml（全局资产库）

转化为：

* prompt_consistency.yaml（一致性校验 + 自动修复结果）

---

## 🎯 Core Objective

确保：

* 人物一致（Identity Consistency）
* 场景一致（Spatial Consistency）
* 时间连续（Temporal Consistency）
* **自动修复**（Auto-Repair）⭐ v0.4 新增

---

---

# ⚙️ Core Principles

---

## 1️⃣ Reference First（最重要）

所有角色 / 场景必须绑定：

```text
asset_id → reference prompt（或 image）
```

---

## 2️⃣ Identity Lock（身份锁定）

```text
同一 character_id：
→ 必须使用同一 base_prompt
→ appearance_fingerprint 必须一致
```

---

## 3️⃣ Variant Control（状态控制）

```text
variant_id → 控制服装 / 状态变化
→ 变体只影响 appearance，不影响 identity
```

---

## 4️⃣ Auto-Repair（⭐ v0.4 核心）

```text
检测到不一致时：
→ 尝试自动修复（fingerprint 补充、reference 注入等）
→ 记录修复操作到 repairs_applied
→ 无法自动修复的记入 issues
→ 修复不修改 semantic 层（READ ONLY）
```

---

## 5️⃣ Fingerprint Priority（指纹优先）

```text
当 prompt 描述与 appearance_fingerprint 冲突时：
→ fingerprint 优先（指纹是已验证的外观事实）
→ 强制覆盖 prompt 中的冲突部分
```

---

---

# 📥 Input

```yaml
input:
  # 语义层（READ ONLY）
  - {runtime_dir}/prompt_ir.yaml

  # 资产层
  - {runtime_dir}/prompt_asset.yaml

  # 标准化层（用于 text 级修复）
  - {runtime_dir}/prompt_canonical.yaml

  # 时序层（用于状态校验）
  - {runtime_dir}/prompt_temporal.yaml

  # 全局资产库（用于 fingerprint/reference 查询）
  - {memory_dir}/asset_registry.yaml
```

---

---

# 📤 Output

```yaml
output:
  - {runtime_dir}/prompt_consistency.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 构建 Asset Map

从 prompt_asset.yaml 构建：

```text
FOR each asset in prompt_asset.yaml:

  收集映射：
    characters:
      character_id → { asset_id, variant_id, source, reference, appearance_fingerprint }

    locations:                            # ✅ 统一命名
      location_id → { asset_id, variant_id, source, anchors }

    objects:
      object_id → { asset_id, state, holder, source }
```

---

## Step 2️⃣ 构建 Registry Cache

从 asset_registry.yaml 构建查询缓存：

```text
registry_cache:

  characters:
    {asset_id} → { base_prompt, variant_prompt, reference, appearance_fingerprint, locked, generation_status }

  locations:
    {asset_id} → { final_prompt, reference.scene_image, anchors, locked }

  objects:
    {asset_id} → { final_prompt, reference.object_image, state_history, holder, locked }
```

---

## Step 3️⃣ 遍历每个 Shot

```text
FOR each shot in prompt_ir.yaml:
  执行 Step 4 ~ Step 9
```

---

## Step 4️⃣ ⭐ 自动修复：fingerprint 缺失检测

```text
# 情况 1：角色 fingerprint 缺失
FOR each character in shot:

  IF prompt_asset 中该角色的 appearance_fingerprint 为空:
    → 从 registry_cache 查询该 asset_id 的 fingerprint
    IF registry 中存在 fingerprint:
      → 自动补充到 prompt_asset 记录
      → 标记 repair_action = "fingerprint_added"
      → 记录 source = "asset_registry.{asset_id}"
    ELSE:
      → 从 base_prompt 提取关键特征生成 fingerprint
      → 标记 repair_action = "fingerprint_generated"
      → 记录 source = "base_prompt_extraction"

# 情况 2：场景 anchors 缺失
FOR each location in shot:

  IF prompt_asset 中该场景的 anchors 为空:
    → 从 registry_cache 查询该 asset_id 的 anchors
    IF registry 中存在 anchors:
      → 自动补充
      → 标记 repair_action = "anchors_added"
```

---

## Step 5️⃣ ⭐ 自动修复：prompt 与 fingerprint 冲突

```text
# 冲突检测：prompt 文本描述 vs fingerprint 锚点
FOR each character in shot:

  fingerprint = character.appearance_fingerprint
  prompt_text = prompt_canonical[shot_id].subject.text

  # 检测冲突（指纹优先原则）
  FOR each fp_item in fingerprint:
    IF prompt_text 包含与 fp_item 矛盾的描述:
      → fingerprint 优先
      → 覆盖 prompt_text 中的冲突部分
      → 标记 repair_action = "prompt_overridden_by_fingerprint"
      → 记录冲突详情: { fingerprint_value, original_value, field }

  # 示例：
  # fingerprint: ["short_black_hair"]
  # prompt_text: "young man with long brown hair..."
  # → 冲突！hair 长度和颜色矛盾
  # → 修复：改为 "young man with short black hair..."
```

---

## Step 6️⃣ ⭐ 自动修复：reference 注入

```text
# 情况 3：角色有 asset 但缺失 reference.face_image
FOR each character in shot:

  IF character 有 asset_id 但 reference.face_image 为空:
    → 从 registry_cache 查询该 asset_id 的 reference.face_image
    IF registry 中存在 reference.face_image:
      → 自动注入到 character.reference.face_image
      → 标记 repair_action = "reference_injected"
      → 记录 value = face_image_path
    ELSE:
      → 标记 issue = "missing_reference_image"
      → 该 asset 需要先生成参考图（pending 状态）

# 情况 4：场景缺失 reference.scene_image
FOR each location in shot:

  IF location 有 asset_id 但 reference.scene_image 为空:
    → 从 registry_cache 查询
    IF 存在:
      → 自动注入
      → 标记 repair_action = "scene_reference_injected"
```

---

## Step 7️⃣ ⭐ 自动修复：ID 匹配校验

```text
# 情况 4：character_id 与 asset_id 不匹配
FOR each character in shot:

  registry_entry = registry_cache.characters[character.asset_id]

  IF registry_entry 存在:
    IF registry_entry.character_id ≠ character.character_id:
      → 优先使用 registry 中的锁定资产
      → 更新 character.asset_id 为 registry 中的 asset_id
      → 标记 repair_action = "asset_id_corrected"
      → 记录 { original_asset_id, corrected_asset_id }
  ELSE:
    → 标记 issue = "asset_not_found_in_registry"
    → 建议 Asset Builder 创建新资产
```

---

## Step 8️⃣ 构建 Character Binding（身份绑定）

对每个 shot 构建角色绑定：

```text
character_bindings:
  FOR each character in shot:

    binding = {
      character_id: character.character_id
      asset_id: character.asset_id
      reference_image: character.reference.face_image   # 修复后的值
      appearance_fingerprint: character.appearance_fingerprint  # 修复后的值
      must_keep: []                                     # 从 fingerprint 提取的关键锚点
      variant_locked: registry_entry.locked
      appearance_consistent: true/false                 # 修复后是否一致
    }

    # 构建 must_keep（从 fingerprint 提取不可变特征）
    FOR each fp in appearance_fingerprint:
      IF fp 属于 identity 特征（face_shape, eye_color, hair_style, skin_tone）:
        → 添加到 must_keep
```

---

## Step 9️⃣ 构建 Location Binding + Object Binding

```text
# 场景绑定（✅ 统一命名：location_bindings）
location_bindings:
  FOR each location in shot:

    binding = {
      location_id: location.location_id
      asset_id: location.asset_id
      anchors: location.anchors                         # 修复后的值
      reference_image: location.reference.scene_image
    }

# 物品绑定
object_bindings:
  FOR each object in shot:

    binding = {
      object_id: object.object_id
      asset_id: object.asset_id
      state: object.state                               # 从 temporal 层获取最新状态
      holder: object.holder                             # 持有者
      reference_image: object.reference.object_image
    }
```

---

## Step 🔟 构建 Spatial Tags + Temporal Tags

```text
# 空间标签（从 consistency 校验生成）
spatial_tags:
  - 同一 location 内的镜头 → "same_location"
  - 多角色同场景 → "multi_character_scene"
  - 物品位置变化 → "object_relocated"

# 时序标签（从 temporal 层传递）
temporal_tags:
  - 继承 prompt_temporal.yaml 的 temporal_tags
  - 校验是否有新增一致性需求
```

---

## Step 1️⃣1️⃣ 输出 prompt_consistency.yaml

```yaml
chapter_id: "1"

shots:
  - shot_id: "C1-S3-shot20"

    # ===== 角色绑定 =====
    character_bindings:
      - character_id: "shen_yan"
        asset_id: "shen_yan_v1"
        reference_image: "assets/characters/shen_yan/face_v1.png"
        appearance_fingerprint:
          - "short_black_hair"
          - "dark_suit"
          - "calm_face"
          - "late_20s"
        must_keep:
          - "face_identity"
          - "hair_shape"
          - "dark_suit"
        variant_locked: true
        appearance_consistent: true

    # ===== 场景绑定（✅ 统一命名）=====
    location_bindings:
      - location_id: "banquet_hall"
        asset_id: "banquet_hall_day_v1"
        anchors:
          - "crystal_chandelier"
          - "white_round_tables"
          - "warm_gold_light"
        reference_image: "assets/scenes/banquet_hall/day_v1.png"

    # ===== 物品绑定 =====
    object_bindings:
      - object_id: "ring_1"
        asset_id: "ring_1_intact_v1"
        state: "intact"
        holder: "shen_yan"
        reference_image: null

    # ===== 标签 =====
    spatial_tags: ["same_location", "multi_character_scene"]
    temporal_tags: ["motion_continuity", "smooth_transition"]

    # ===== ⭐ 修复记录 =====
    repairs_applied:
      - field: "appearance_fingerprint"
        action: "fingerprint_added"
        source: "asset_registry.shen_yan_v1"
      - field: "reference_image"
        action: "reference_injected"
        value: "assets/characters/shen_yan/face_v1.png"

    # ===== 无法自动修复的问题 =====
    issues: []
```

---

---

# 🚫 Anti-Patterns

---

❌ 忽略 reference（reference 是一致性的核心保障）
❌ 每镜头重新描述人物（应通过 asset_id 引用）
❌ 不处理 previous_shot（时序一致性必须有）
❌ 修改 semantic 层字段（Consistency 对 semantic 只读）
❌ 静默修复而不记录 repairs_applied（所有修复必须可追溯）
❌ 跳过 fingerprint 冲突检测（这是身份漂移的根源）
❌ 修改 asset_id / character_id（只能校验和纠正，不能创造新的）

---

---

# 🧩 Final Note

---

> Consistency Enforcer v2.0 的核心升级：
>
> 👉 **从"仅校验"升级为"校验 + 自动修复"**
>
> 四种自动修复能力：
> 1. fingerprint 缺失 → 从 registry 补充或从 base_prompt 提取
> 2. prompt 与 fingerprint 冲突 → fingerprint 优先，覆盖 prompt
> 3. reference 缺失 → 从 registry 注入
> 4. asset_id 不匹配 → 从 registry 纠正
>
> 所有修复操作都记录在 repairs_applied 中，确保可追溯。
> 无法自动修复的问题记入 issues，等待人工介入。
