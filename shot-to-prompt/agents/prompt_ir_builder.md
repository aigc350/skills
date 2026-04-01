# IR Builder Agent v1.4 (Variant-Enabled, Production-Ready)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `ir_builder` | Generates: prompt_ir.yaml (before canonical)

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

### 1️⃣ Three-Layer Identity System（三层身份体系）

```text
Layer 1: character_id  → 谁？（身份，不变）
Layer 2: variant_id    → 什么状态？（服饰/造型，可变）
Layer 3: asset_id      → 用什么资产生成？（由 asset_builder 决定）
```

**关系**：
```
character_id (1) ──→ variant_id (N) ──→ asset_id (1~N)
     │                    │                   │
     │                    │                   └─ 资产生成/匹配
     │                    │
     │                    └─ ir_builder 确定
     │
     └─ 来自 characters.yaml
```

---

### 2️⃣ IR Builder 职责边界

**IR Builder 负责**：
* 从 shot_spec 提取 character_id
* 从 shot_spec / characters.yaml 确定 variant_id
* 输出 character_id + variant_id

**IR Builder 不负责**：
* ❌ 生成 asset_id（由 asset_builder 决定）
* ❌ 判断资产是否存在
* ❌ 处理 lighting/time 等上下文拆分

---

### 3️⃣ Asset Builder 职责

**Asset Builder 负责**：
* 根据 variant_id 查找/生成 asset
* 决定 asset_id = variant_id 还是拆分
* 处理上下文差异（白天/夜晚/场景）

**asset_id 生成规则**：

```yaml
# 默认情况：asset_id = variant_id
variant_id: shenyan_work_clothes_v1
    → asset_id: shenyan_work_clothes_v1

# 需要拆分时：asset_id = variant_id + context
variant_id: shenyan_work_clothes_v1
context: { lighting: night, scene: office }
    → asset_id: shenyan_work_clothes_v1_night_office
```

---

# 📥 Input Sources

---

## characters.yaml（升级要求）

必须支持：

```yaml
characters:
  - character_id: shen_yan        # 身份 ID
    face_id: shenyan_male_v1      # 面部 ID（用于一致性）
    base_description: "亚洲男性，25-30岁，短发，沉稳气质"

    variants:                      # 1:N 关系
      - variant_id: shenyan_wedding_suit_v1
        outfit: "深色礼服，正式但不华丽"
        accessories: []

      - variant_id: shenyan_work_clothes_v1
        outfit: "工作服，简洁实用"
        accessories: ["watch"]

      - variant_id: shenyan_work_clothes_v2
        outfit: "工作装，稍有磨损"
        accessories: ["watch", "tool_bag"]
```

**关键设计**：

| 字段 | 来源 | 说明 |
|------|------|------|
| `character_id` | characters.yaml | 身份标识，不变 |
| `variant_id` | shot_spec 或 characters.yaml | 服饰/状态，可变 |
| `asset_id` | asset_builder 生成 | **不在 IR 阶段生成** |

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

    - character_id: string        # 身份 ID
      variant_id: string          # 变体 ID
      # asset_id: 由 asset_builder 决定，不在此处输出

      face_id: string             # 面部 ID（一致性关键）
      appearance:
        outfit: string
        hair: string
        accessories: [string]
```

---

---

## 2️⃣ Character 映射规则（升级）

---

优先级：

```text
shot_spec.variant_id > characters.yaml 默认 variant
```

---

输出结构：

```yaml
character:

  character_id: string           # 身份（来自 characters.yaml）
  variant_id: string             # 变体（来自 shot_spec 或默认）

  face_id: string                # 面部 ID（用于资产匹配）

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

**注意**：IR 阶段不输出 `asset_id`，由 asset_builder 根据 `variant_id` + context 决定。

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
