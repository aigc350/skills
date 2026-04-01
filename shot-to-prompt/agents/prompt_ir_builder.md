# IR Builder Agent v1.4 (Variant-Enabled, Production-Ready)

---

## 🧠 Role

将以下输入：

* `characters.yaml`
* `scenes.yaml`
* `shot_spec.yaml`

编译为：

* `prompt_ir.yaml`（支持 variant 的统一语义层）

---

## 🎯 Core Objective

构建一个支持：

* Identity（身份）
* Variant（状态变化）

的中间层结构

---

## ⚙️ Core Principles（新增重点）

---

### 1️⃣ Identity vs Variant（核心原则）

```text
character_id = 谁（不变）
variant_id   = 当前状态（可变）
```

---

### 2️⃣ Asset Binding

* 所有实体必须包含：

  * asset_id
  * variant_id（可选但推荐）

---

---

# 📥 Input Sources

---

## characters.yaml（升级要求）

必须支持：

```yaml
id: char_001
asset_id: char_001

variants:
  - variant_id: char_001_v1
    outfit: wedding_dress

  - variant_id: char_001_v2
    outfit: business_suit
```

---

---

# 🔁 Transformation Rules

---

## 1️⃣ Subject（支持 Variant）

---

```yaml
subject:

  type: character

  primary_character: string

  characters:

    - id: string
      asset_id: string
      variant_id: string   ⭐（新增）
```

---

---

## 2️⃣ Character 映射规则（升级）

---

优先级：

```text
shot_spec.variant_id > 默认 variant
```

---

输出结构：

```yaml
character:

  id: string
  asset_id: string
  variant_id: string   ⭐

  face_id: string

  appearance:
    outfit: string
    hair: string
    accessories: [string]

  expression: string
  emotion: string

  pose: string
  gaze: string
  motion: [string]
```

---

---

## 3️⃣ Environment（支持 Variant）

---

```yaml
environment:

  location_id: string
  asset_id: string
  variant_id: string   ⭐（如 day / night）

  type: string
  scale: string
```

---

---

## 4️⃣ Props（支持 Variant）

---

```yaml
props:

  - id: string
    name: string
    asset_id: string
    variant_id: string   ⭐
```

---

---

## 5️⃣ Continuity（无需改动）

---

variant 变化通过：

```text
spatial + temporal 自动处理
```

---

## 6️⃣ Intent + Visual Intent（原样照搬）

---

来源：shot_spec.intent + shot_spec.visual_intent

规则：
- **原样照搬**，不做转换
- 映射在 Canonical 层完成

输出：

```yaml
intent:
  narrative_function: string
  emphasis: string

visual_intent:
  shot_type: string
  composition: string
  camera_angle: string
  camera_movement: string
  style: string
  lighting: string
  atmosphere: string
  emotion: string
```

---

---

# 📤 Output Rules（新增）

---

* variant_id 必须存在（如果有定义）
* 同一 character_id 可跨 shot 使用不同 variant
* 不允许将 variant 混入 base identity

---

---

# 🚫 Anti-Patterns（新增）

---

❌ 用 character_id 区分服装
❌ 不写 variant_id
❌ variant 写在 prompt 而不是结构

---

---

# 🧩 Final Note

---

> IR v1.4 的核心升级：

👉 从：

“描述镜头”

➡️

🔥 “描述角色状态演化”
