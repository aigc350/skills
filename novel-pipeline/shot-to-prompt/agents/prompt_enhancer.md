# Prompt Enhancer Agent v2.0 (Structured Enhancement Engine)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `enhancer` | Permission: semantic ⚠ LIMITED (style/intensity only), quality ✅, negative ✅
>
> ⭐ v0.5 修正：只读 canonical（不再直接读 IR），输出结构化 prompt + enhancement

---

## 🧠 Role

将输入：

* prompt_canonical.yaml（标准化语义层）

输出：

* prompt_enhancer.yaml（结构化增强版）

> ⭐ v0.5: Enhancer 只读取 canonical 层，不直接读取 IR（遵守 pipeline_validator Rule 3）

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

## 1️⃣ Canonical Driven（⭐ v0.5 修正）

所有增强必须来自：

```yaml
canonical.style
canonical.subject.emotion
canonical.camera
canonical.location
```

> ❌ 不再直接读取 IR（pipeline_validator Rule 3: `Enhancer ❌ IR`）

---

## 2️⃣ Structured First（核心升级）

❗ 不允许直接拼字符串
❗ 必须先生成”增强结构”，再输出结构化数据

---

## 3️⃣ Non-Destructive

* 不删除原 prompt
* 只做增强

---

---

# 📥 Input

```yaml
input:
  - prompt_canonical.yaml       # ⭐ 唯一数据来源（不再读 IR）
  - hook_engine.yaml             # 爆点策略配置
```

---

# 📤 Output

```yaml
output:
  - prompt_enhancer.yaml
```

---

---

# 🌐 Global Strategy Layer

---

## 提取（从 canonical）：

```yaml
genre = canonical.style.semantic.style
intensity = canonical.style.semantic.intensity
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
canonical.subject.semantic.emotion
canonical.style.semantic.intensity
canonical.intent.emphasis  # 权重由 canonical 层提供
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
canonical.camera.semantic.shot_type
canonical.camera.semantic.movement
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
canonical.style.semantic.lighting
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
canonical.environment.semantic.location
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
chapter_id: string

meta:
  enhanced: true
  genre: string
  intensity: string

shots:

  - shot_id: string

    # 继承 canonical 的 prompt 结构（不修改）
    prompt:
      subject: {...}
      action: {...}
      location: {...}
      camera: {...}
      style: {...}
      quality: {...}
      negative: {...}

    # 本阶段新增的增强数据
    enhancement:
      style_tags: string[]           # 增强关键词汇总
      hook:
        type: string                 # opening / middle / climax
        prefix: string[]
        suffix: string[]

      emotion:
        keywords: string[]
      camera:
        keywords: string[]
      lighting:
        keywords: string[]
      environment:
        keywords: string[]

      # 爽点结构化（供 Resolver 的 dramatic_focus 使用）
      hook_type: string
      opening_beat: string
      payoff_target: string[]
      emphasis: string[]
```

---

---

# 🚫 Anti-Patterns

---

❌ 不允许重复 hook 注入
❌ 不允许跳过结构层直接拼接
❌ 不允许直接读取 IR（⭐ v0.5: 必须从 canonical 读取）
❌ 输出简单字符串（必须输出结构化 prompt + enhancement）

---

---

# 🚀 Pipeline

---

```text
prompt_canonical_builder
      ↓
prompt_canonical.yaml
      ↓
prompt_enhancer v2.0
      ↓
prompt_enhancer.yaml
```

---

---

# 🧩 Final Note

---

> ❗ Enhancer v2.0 的核心升级：
>
> 👉 **从"读 IR + 拼字符串"升级为"读 canonical + 结构化输出"**
>
> 1. 不再直接读取 IR（遵守 pipeline_validator Rule 3）
> 2. 所有增强数据来自 canonical 的 semantic 层
> 3. 输出结构化 prompt + enhancement（不再拼接字符串）
> 4. 下游 Resolver 读取结构化 enhancement 构建 dramatic_focus
