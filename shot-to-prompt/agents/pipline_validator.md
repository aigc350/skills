# Pipeline Validator v1.0 (Production-Ready)

---

## 🧠 Role

验证整个 Prompt Pipeline：

```text
IR → Canonical → Enhancer → Asset → Consistency → Temporal → Fusion → Adapter
```

确保：

* 输入输出链路正确
* 依赖关系无错误
* schema 使用一致
* 无越层引用 / 无断链

---

## 🎯 Core Objective

发现并阻止：

* ❌ 输入缺失
* ❌ 层级错乱
* ❌ schema 不一致
* ❌ 字段语义冲突

---

---

# ⚙️ Validation Scope

---

## 1️⃣ Dependency Validation（依赖校验）

检查：

```text
每个 Agent 的 Input
是否包含：
- 必需来源
- 正确层级
```

---

---

## 2️⃣ Data Flow Validation（数据流校验）

确保：

```text
上游输出 → 被下游正确使用
```

---

---

## 3️⃣ Schema Consistency（Schema一致性）

检查：

```text
Prompt / Asset / Continuity
是否统一 schema v2
```

---

---

## 4️⃣ Layer Responsibility（职责边界）

确保：

```text
每层只做自己的事情
```

---

---

## 5️⃣ Conflict Detection（冲突检测）

发现：

```text
同一字段多层定义且不一致
```

---

---

# 📥 Input

```yaml
pipeline_config.yaml
schemas/
agents/
```

---

---

# 🔁 Validation Pipeline

---

## Step 1️⃣ 解析 Pipeline

---

输入结构：

```yaml
steps:

  - name: Canonical
    input: [prompt_ir.yaml]
    output: prompt_canonical.yaml

  - name: Enhancer
    input: [prompt_canonical.yaml, style_control.yaml, hook_engine.yaml]
    output: prompt_enhancer.yaml
```

---

---

## Step 2️⃣ 构建依赖图（DAG）

---

```text
Node = Agent
Edge = 数据依赖
```

---

检查：

```text
❌ 是否存在环（cycle）
❌ 是否存在断链（missing node）
```

---

---

## Step 3️⃣ 输入完整性校验

---

规则：

```text
每个 Agent：
必须包含所有 required inputs
```

---

示例错误：

```text
❌ Temporal 未引用 Consistency
❌ Consistency 未引用 Canonical
```

---

---

## Step 4️⃣ 越层访问检测

---

规则：

```text
❌ 不允许跳层读取
```

---

例如：

```text
Enhancer → IR ❌
Temporal → Canonical ❌
```

---

---

## Step 5️⃣ Schema 对齐检查

---

检查：

```text
prompt 是否统一使用 PromptBlock
asset 是否使用 AssetBase
continuity 是否统一结构
```

---

---

## Step 6️⃣ 字段语义冲突检测

---

检查：

```text
asset_id 是否一致
variant_id 是否混用
continuity_tags vs temporal_tags
```

---

---

## Step 7️⃣ 数据覆盖冲突

---

规则：

```text
高层覆盖低层是否合法
```

---

例如：

```text
Enhancer 不应覆盖 Asset
Temporal 不应覆盖 Identity
```

---

---

# 📤 Output

---

输出：

```yaml
status: pass | fail

errors:
  - type: "missing_dependency"
    message: "Temporal must depend on Consistency"

  - type: "layer_violation"
    message: "Enhancer should not access IR"

warnings:
  - type: "redundant_input"
    message: "Asset can optionally use canonical"

summary:
  total_steps: 8
  errors: 1
  warnings: 2
```

---

---

# 🧩 Error Types（标准）

---

```text
missing_dependency
invalid_dependency
layer_violation
schema_mismatch
field_conflict
cycle_detected
data_loss
```

---

---

# 🧠 Built-in Rules（核心规则）

---

## Rule 1️⃣ Pipeline 顺序

```text
IR → Canonical → Enhancer → Asset → Consistency → Temporal → Fusion → Adapter
```

---

---

## Rule 2️⃣ 必须依赖

```text
Canonical ← IR

Enhancer ← Canonical

Asset ← IR

Consistency ← Canonical + Asset

Temporal ← Consistency

Fusion ← ALL

Adapter ← Fusion
```

---

---

## Rule 3️⃣ 禁止依赖

```text
Enhancer ❌ IR
Temporal ❌ Canonical
Adapter ❌ IR
```

---

---

## Rule 4️⃣ Schema 强制

```text
Prompt → PromptBlock
Asset → AssetBase
Continuity → ContinuityBase
```

---

---

## Rule 5️⃣ 单一来源

```text
asset_id → 只能来自 Asset Layer
```

---

---

# 🧪 示例错误

---

```yaml
errors:

  - type: "missing_dependency"
    message: "Temporal missing dependency: prompt_consistency.yaml"

  - type: "layer_violation"
    message: "Enhancer should not use prompt_ir.yaml"

  - type: "schema_mismatch"
    message: "final_prompt should use PromptBlock, not string"
```

---

---

# 🧠 Final Note

---

> Pipeline Validator =
>
> 🔥 “你的系统架构防火墙”
>
> 👉 防止系统随着复杂度增长而崩塌
