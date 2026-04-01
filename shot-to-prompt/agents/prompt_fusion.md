# Prompt Fusion Layer v1.0 (Production-Ready)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `fusion` | Permission: Combines all layers, semantic ❌ READ ONLY

---

## 🧠 Role

融合多层输出：

* prompt_canonical.yaml
* prompt_enhancer.yaml
* prompt_asset.yaml
* prompt_consistency.yaml
* prompt_temporal.yaml

生成：

👉 prompt_fusion.yaml（最终可用于模型）

---

## 🎯 Core Objective

构建：

👉 **最终模型级 Prompt（单一字符串 + 可控结构）**

同时保证：

* 风格一致（Enhancer）
* 视觉一致（Asset + Consistency）
* 时间连续（Temporal）

---

---

# ⚙️ Core Principles

---

## 1️⃣ Single Source of Truth（最终统一）

```text
所有层 → 融合为一个 prompt.final.text
```

---

---

## 2️⃣ Layer Priority（优先级）

```text
Temporal > Consistency > Asset > Enhancer > Canonical
```

---

---

## 3️⃣ Structured → Linear

```text
结构化 Prompt → 线性 Prompt（模型输入）
```

---

---

## 4️⃣ Conflict Resolution（冲突消解）

```text
高优先级覆盖低优先级
```

---

---

## 5️⃣ Platform-Agnostic

```text
本层不做平台适配
```

---

---

# 📥 Input

```yaml
prompt_canonical.yaml
prompt_enhancer.yaml
prompt_asset.yaml
prompt_consistency.yaml
prompt_temporal.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 合并 PromptBlock

---

来源：

```text
canonical.prompt
+ enhancer.prompt（增强）
```

---

输出：

```text
base_prompt（结构化）
```

---

---

## Step 2️⃣ 注入 Asset Prompt

---

```text
asset_id → final_prompt
```

---

规则：

```text
subject.block += asset_prompt
environment.block += env_prompt
```

---

---

## Step 3️⃣ 注入 Consistency

---

```text
加入 reference 语义：
consistent appearance, same identity
```

---

---

## Step 4️⃣ 注入 Temporal

---

```text
加入：
continue motion
transition
state change
```

---

---

## Step 5️⃣ 构建 Structured Prompt

---

结构：

```text
subject
action
environment
camera
style
quality
```

---

---

## Step 6️⃣ Linearization（关键）

---

拼接顺序（默认）：

```text
[subject]
[action]
[environment]
[camera]
[style]
[quality]
[temporal]
```

---

---

## Step 7️⃣ Hook 注入（来自 Enhancer）

---

```text
hook → 插入开头（优先）
```

---

---

## Step 8️⃣ 负面提示合并

---

来源：

* canonical
* asset
* enhancer

---

---

## Step 9️⃣ Prompt 清洗

---

必须：

```text
❌ 去重复
❌ 去冲突
✔ 保持紧凑
✔ 英文输出
```

---

---

# 📤 Output Rules

---

每个 shot 输出：

* shot_id
* final_prompt（string）
* negative_prompt
* referenced_assets
* fusion_trace

---

---

# 🧬 Fusion Trace（调试用）

---

记录：

```text
来源层：
- canonical
- enhancer
- asset
- consistency
- temporal
```

---

---

# 🚫 Anti-Patterns

---

❌ 重复拼接
❌ 忽略优先级
❌ 输出结构化而非线性

---

---

# 🧩 Final Note

---

> Fusion Layer =
> 🔥 “Prompt 的最终编译器”
