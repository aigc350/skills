# Asset Prompt Builder v2.1 (Production-Ready, Registry Enabled)

---

## 🧠 Role

从 `prompt_ir.yaml` 中解析：

* character_id（身份）
* variant_id（状态）
* asset_id（视觉）

生成：

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

## 1️⃣ Identity / Variant 分离

* base_prompt（身份）稳定
* variant_prompt（状态）变化

---

## 2️⃣ Asset = Base + Variant

asset_prompt = base_prompt + variant_prompt

---

## 3️⃣ Registry First（最重要）

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

## Step 1️⃣ 收集资产

收集：

* character_id
* variant_id
* asset_id

---

## Step 2️⃣ 处理每个 Asset

---

### 🔥 2.1 Resolve asset_id

```text
asset_id = variant_id（推荐）
```

---

---

### 🔥 2.2 查询 Registry

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
