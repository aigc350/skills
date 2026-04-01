# Asset Prompt Builder v2.1 (Production-Ready, Registry Enabled)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `asset` | Generates: asset_registry.yaml (parallel to canonical)

---

## 🧠 Role

从 `prompt_ir.yaml` 中解析：

* character_id（身份）- 来自 IR
* variant_id（状态）- 来自 IR

**生成**：

* asset_id（视觉资产 ID）- **由本阶段决定**

输出：

* `prompts_asset.yaml`
  并维护：
* `asset_registry.yaml`（全局资产库）

---

## 🎯 Core Objective

构建一个：

* 可复用（reuse）
* 可版本控制（versioning）
* 可锁定（locking）

的视觉资产系统

---

---

# ⚙️ Core Principles

---

## 1️⃣ Three-Layer Mapping

```
IR 输出                  Asset Builder 输出
─────────────────────    ─────────────────────
character_id: shen_yan   → base_prompt（身份）
variant_id: work_v1      → variant_prompt（状态）
                         → asset_id: shen_yan_work_v1（资产）
```

**关键**：asset_id 由 asset_builder 决定，不是 IR。

---

## 2️⃣ Asset = Base + Variant

asset_prompt = base_prompt + variant_prompt

---

## 3️⃣ asset_id 生成规则

**默认规则**：
```yaml
asset_id = variant_id
```

**拆分规则**（根据上下文）：
```yaml
# 当需要区分同一服饰的不同场景时
variant_id: shenyan_work_clothes_v1
context:
  lighting: night
  scene: office
    → asset_id: shenyan_work_clothes_v1_night_office
```

**何时拆分**：

| 条件 | 是否拆分 |
|------|----------|
| 同一服饰，不同光照（day/night） | ✅ 可拆分 |
| 同一服饰，不同场景（office/outdoor） | ✅ 可拆分 |
| 同一服饰，同一环境 | ❌ 不拆分 |

---

## 4️⃣ Registry First（最重要）

在生成前必须：

* 查询 registry
* 决定复用 / 更新 / 新建

---

---

# 📥 Input

```yaml
prompt_ir.yaml
prompt_canonical.yaml
```

---

---

# 📦 Registry

```yaml
memory/asset_registry.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 收集输入

从 IR 收集：

```yaml
character_id: shen_yan        # 身份 ID
variant_id: shenyan_work_v1   # 变体 ID
face_id: shenyan_male_v1      # 面部 ID
appearance:                   # 外观信息
  outfit: "工作服"
  accessories: ["watch"]
```

**注意**：IR 不提供 asset_id，由本阶段生成。

---

## Step 2️⃣ 决定 asset_id

---

### 🔥 2.1 默认情况

```yaml
asset_id = variant_id
```

示例：
```
variant_id: shenyan_work_clothes_v1
    → asset_id: shenyan_work_clothes_v1
```

---

### 🔥 2.2 需要拆分时

检查上下文：
* lighting（lighting = night 可能需要不同资产）
* scene（室内/室外可能有差异）

```yaml
# 判断逻辑
IF context.lighting == "night" AND registry.has(variant_id + "_night"):
    asset_id = variant_id + "_night"
ELSE:
    asset_id = variant_id
```

---

### 🔥 2.3 查询 Registry

---

#### 情况 A：存在 + locked = true

```text
→ 直接复用（source = reused）
```

---

#### 情况 B：存在 + locked = false

```text
→ 对比 prompt：

IF 相同：
    → 复用

IF 不同：
    → version +1
    → 更新 registry
```

---

#### 情况 C：不存在

```text
→ 新建 asset（source = generated）
```

---

---

## Step 3️⃣ 构建 Base Prompt

来源：

* appearance（face / hair）
* traits
* visual_keywords

规则：

* ❌ 去 emotion
* ❌ 去动作
* ✔ 强化 identity

---

---

## Step 4️⃣ 构建 Variant Prompt

来源：

* outfit
* accessories
* variant_id 语义

---

---

## Step 5️⃣ 合成 Final Prompt

```text
base + variant + cinematic + high detail + consistency
```

---

---

## Step 6️⃣ 写回 Registry

---

新增字段：

* version
* locked（默认 false）
* usage
* timestamps

---

---

## Step 7️⃣ 输出 asset_prompts.yaml

---

每个 asset 输出：

* character_id
* asset_id
* variant_id
* version
* locked
* source
* base_prompt
* variant_prompt
* final_prompt

---

---

# 🚫 Anti-Patterns

---

❌ 每次重复生成 asset
❌ variant 写进 base
❌ 输出动作 / 镜头

---

---

# 🧩 Final Note

---

> Asset Layer =
> 🔥 “视觉资产数据库（不是生成工具）”
