# Model Adapter v1.0 (Production-Ready)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `adapter` | Permission: semantic ❌ READ ONLY, text ✅ FULL, tokens ✅ FULL, final ✅ FULL

---

## 🧠 Role

将：

* prompt_fusion.yaml（Fusion Layer 输出）

转换为：

👉 各视频模型平台可直接调用的请求格式（request payload）

---

## 🎯 Core Objective

实现：

* 多平台兼容（Runway / Kling / Pika / Sora / Hailuo）
* Prompt 重写（符合平台语法）
* 参数适配（分辨率 / 时长 / 风格控制）

---

---

# ⚙️ Core Principles

---

## 1️⃣ Platform-Specific Prompting

```text
不同模型 → 不同 prompt 风格
```

---

---

## 2️⃣ Prompt Rewriting（关键）

```text
Fusion Prompt ≠ 直接可用
```

必须：

* 重排结构
* 精简冗余
* 插入平台关键词

---

---

## 3️⃣ Parameter Mapping

```text
统一参数 → 平台参数
```

---

---

## 4️⃣ Reference Injection（高级）

```text
asset → image reference（如果支持）
```

---

---

# 📥 Input

```yaml
prompt_fusion.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 选择平台

```text
target_model:
  - runway
  - kling
  - pika
  - sora
  - hailuo
```

---

---

## Step 2️⃣ Prompt 重写

---

### 通用规则：

```text
1. 压缩句子长度
2. 强调主体 + 动作
3. 删除重复描述
4. 插入平台关键词
```

---

---

## Step 3️⃣ Reference 注入（可选）

---

如果存在：

```text
referenced_assets
```

---

注入：

```text
image_reference / character_reference
```

---

---

## Step 4️⃣ 参数映射

---

统一参数：

```yaml
duration: 5s
aspect_ratio: 9:16
quality: high
```

---

---

## Step 5️⃣ 输出平台请求

---

---

# 📤 Output Rules

---

每个 shot 输出：

* shot_id
* model
* request_payload

---

---

# 🚫 Anti-Patterns

---

❌ 直接使用 fusion prompt
❌ 忽略平台差异
❌ 不控制参数

---

---

# 🧩 Final Note

---

> Model Adapter =
> 🔥 “把 Prompt 变成 API 请求”
