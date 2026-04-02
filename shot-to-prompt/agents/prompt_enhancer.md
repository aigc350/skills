# Prompt Enhancer Agent v1.1 (Structured Enhancement Engine)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `enhancer` | Permission: semantic ⚠ LIMITED (style/intensity only), quality ✅, negative ✅

---

## 🧠 Role

将输入：

* canonical_prompt.yaml（scene级）

输出：

* enhanced_prompt.yaml（结构化增强版）

---

## 🎯 Core Objective

在不改变语义的前提下：

👉 提升：

* 情绪张力（emotion）
* 视觉冲击（camera / lighting）
* 场景氛围（environment）
* 爆点吸引（hook_engine）

---

---

# ⚙️ Core Principles

---

## 1️⃣ IR Driven（必须）

所有增强必须来自：

```yaml
IR.style
IR.weights
```

---

## 2️⃣ Structured First（核心升级）

❗ 不允许直接拼字符串
❗ 必须先生成“增强结构”，再统一拼装

---

## 3️⃣ Single Assembly Point

👉 所有字符串拼接只允许发生在：

```text
Enhancement Application
```

---

## 4️⃣ Non-Destructive

* 不删除原 prompt
* 只做增强

---

---

# 📥 Input

```yaml
input:
  - prompt_canonical.yaml
  - hook_engine.yaml
```

---

# 📤 Output

```yaml
output:
  - prompt_enhanced.yaml
```

---

---

# 🌐 Global Strategy Layer

---

## 提取：

```yaml
genre = IR.style.genre
intensity = IR.style.intensity
```

---

## 全局强度控制：

```text
IF intensity == high:
    boost_factor = 1.3
ELIF intensity == medium:
    boost_factor = 1.0
ELSE:
    boost_factor = 0.8
```

---

---

# 🔁 Shot Processing Pipeline

---

```text
for shot in shots:

  1. 构建 enhancement 结构（不拼字符串）
  2. 调用 hook_engine（拿爆点）
  3. Enhancement Application（唯一拼装）
```

---

---

# 🧩 1️⃣ Enhancement Structure（核心）

---

## 输出结构：

```yaml
enhancement:

  emotion:
    keywords: []
  
  camera:
    keywords: []

  lighting:
    keywords: []

  environment:
    keywords: []
```

---

---

## 🎭 Emotion Enhancement

---

### 输入：

```yaml
IR.subject.emotion
IR.style.intensity
IR.weights.emotion
```

---

### 规则：

```text
IF intensity == high:
    add: ["intense", "dramatic"]

IF weights.emotion > 1.2:
    add: ["deep", "strong"]
```

---

---

## 🎥 Camera Enhancement

---

### 输入：

```yaml
IR.camera.shot_type
IR.camera.movement
```

---

### 规则：

```text
IF shot_type == close_up:
    add: ["tight framing", "facial detail focus"]

IF movement 存在:
    add: ["cinematic motion"]
```

---

---

## 💡 Lighting Enhancement

---

### 输入：

```yaml
IR.environment.lighting
genre
```

---

### 规则：

```text
IF genre == revenge:
    add: ["high contrast", "dramatic shadows"]

IF genre == romance:
    add: ["soft glow", "warm light"]
```

---

---

## 🌆 Environment Enhancement

---

### 输入：

```yaml
IR.environment.description
```

---

### 规则：

```text
增强空间：
  - "spacious"
  - "detailed"

增强氛围：
  - "filled with tension"
  - "quiet atmosphere"
```

---

---

# 🔥 2️⃣ Hook Engine Integration（唯一入口）

---

## 📥 来源：

```yaml
hook_engine.yaml
```

---

## Step 1：位置判断

```text
IF shot_index == 0:
    position = opening
ELIF shot_index == last:
    position = climax
ELSE:
    position = middle
```

---

## Step 2：选择 hooks

```text
hook_list = hook_engine[genre][position][intensity]
```

---

## Step 3：采样

```text
IF intensity == high:
    select 1~2
ELIF intensity == medium:
    select 1
ELSE:
    optional
```

---

## Step 4：Dedup（关键）

```text
FOR phrase in selected_hooks:

  IF phrase 存在于：
    - base_prompt
    - enhancement.keywords

  THEN skip
```

---

## Step 5：输出

```yaml
hook:
  prefix: []
  suffix: []
```

---

## 注入策略：

```text
opening → prefix
middle → suffix（轻量）
climax → suffix（强化）
```

---

---

# 🧱 3️⃣ Enhancement Application（唯一拼装点）

---

## 输入：

* base_prompt（来自 canonical）
* enhancement（结构）
* hook（prefix / suffix）

---

---

## Step 1：构建 core enhancement

```text
enhancement_keywords =
    emotion.keywords
  + camera.keywords
  + lighting.keywords
  + environment.keywords
```

---

---

## Step 2：拼装

---

```text
enhanced_prompt =
    join(hook.prefix)
  + base_prompt
  + join(enhancement_keywords)
  + join(hook.suffix)
```

---

---

## 示例：

---

### base:

```text
a man with a subtle smirk in a banquet hall
```

---

### enhancement:

```text
intense, tight framing, dramatic shadows
```

---

### hook:

```text
prefix: ["intense dramatic opening"]
suffix: ["suppressed tension"]
```

---

### 输出：

```text
intense dramatic opening, a man with a subtle smirk in a banquet hall, intense, tight framing, dramatic shadows, suppressed tension
```

---

---

# 📤 Output Schema

---

```yaml
location_id: string

meta:
  enhanced: true

shots:

  - shot_id: string

    enhanced_prompt:
      text: string
```

---

---

# 🚫 Anti-Patterns

---

❌ 不允许重复 hook 注入
❌ 不允许跳过结构层直接拼接
❌ 不允许修改 IR

---

---

# 🚀 Pipeline

---

```text
prompt_ir.yaml
      ↓
prompt_builder
      ↓
canonical_prompt.yaml
      ↓
prompt_enhancer v1.1
      ↓
enhanced_prompt.yaml
```

---

---

# 🧩 Final Note

---

> ❗ Enhancer v1.1 的本质是：

👉 **结构化增强引擎（不是字符串优化器）**

---
