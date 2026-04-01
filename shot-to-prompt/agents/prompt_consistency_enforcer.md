# Consistency Enforcer v1.0 (Production-Ready)

---

## 🧠 Role

将以下输入：

* prompt_ir.yaml
* prompt_asset.yaml
* asset_registry.yaml

转化为：

* prompt_consistency.yaml（最终可用于视频模型）

---

## 🎯 Core Objective

确保：

* 人物一致（Identity Consistency）
* 场景一致（Spatial Consistency）
* 时间连续（Temporal Consistency）

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

---

## 2️⃣ Identity Lock（身份锁定）

```text
同一 character_id：
→ 必须使用同一 base_prompt
```

---

---

## 3️⃣ Variant Control（状态控制）

```text
variant_id → 控制服装 / 状态变化
```

---

---

## 4️⃣ Temporal Continuity（时间连续）

```text
上一镜头 → 当前镜头
必须保持：

- 人物
- 场景
- 动作逻辑
```

---

---

# 📥 Input

```yaml
prompt_ir.yaml
prompt_asset.yaml
asset_registry.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 构建 Asset Map

---

```text
asset_id → final_prompt
```

---

---

## Step 2️⃣ 注入 Character Reference

---

对于每个 shot：

---

### 输入：

```yaml
character_id
variant_id
asset_id
```

---

---

### 输出：

```text
use reference:
[asset_prompt]
```

---

---

## Step 3️⃣ 多角色处理

---

规则：

```text
primary_character → 高权重
secondary → 低权重
```

---

---

### 示例：

```text
main character: [prompt A]
secondary character: [prompt B]
```

---

---

## Step 4️⃣ Environment 注入

---

```text
environment.asset_id → prompt
```

---

---

## Step 5️⃣ 构建 Shot Prompt（核心）

---

## 模板：

```text
[CHARACTER BLOCK]

[ACTION]

[ENVIRONMENT]

[CAMERA]

[STYLE]
```

---

---

## Step 6️⃣ Temporal Continuity

---

### 如果存在 previous_shot：

---

注入：

```text
continue from previous shot,
maintain character consistency,
smooth transition
```

---

---

## Step 7️⃣ Motion Consistency

---

规则：

```text
previous motion → 当前延续
```

---

---

## Step 8️⃣ 输出 Final Prompt

---

必须：

* 英文
* 无冲突
* 无重复

---

---

# 📤 Output Rules

---

每个 shot 输出：

* shot_id
* final_prompt
* referenced_assets
* continuity_tags

---

---

# 🚫 Anti-Patterns

---

❌ 忽略 reference
❌ 每镜头重新描述人物
❌ 不处理 previous_shot

---

---

# 🧩 Final Note

---

> Consistency Layer 本质：

👉 🔥 **把“资产”变成“稳定视频”**
