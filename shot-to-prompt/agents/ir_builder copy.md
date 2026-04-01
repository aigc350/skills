# IR Builder Agent v1.2

## Role

将以下输入：

* `characters.yaml`
* `scenes.yaml`
* `shot_spec.yaml`

编译为：

* `prompt_ir.yaml`（统一语义中间层）

---

## Core Objective

将"分散结构数据" → "统一语义结构"

为以下模块提供稳定输入：

* prompt_builder
* prompt_enhancer
* model_adapter

---

## Core Principles

### 1. Single Source of Truth

```
shot_spec > characters > scenes
```

### 2. Structural Only

* 禁止自然语言
* 只输出 token / 枚举 / 结构字段

### 3. Deterministic

* 相同输入 → 相同输出

---

## Input Sources

### characters.yaml

提供：

* appearance（outfit / hair / accessories）
* expression / emotion
* traits / visual_keywords

### scenes.yaml

提供：

* location / type / scale / description
* lighting / props / atmosphere
* visual_keywords

### shot_spec.yaml

提供：

* subject
* camera
* visual_intent
* motion / pose / gaze

---

# Transformation Rules

---

## 1. Subject（主体）

### type: character

来源：

* shot_spec.subject
* characters.yaml.appearances（按 shot_id）

字段规则：

* expression：shot_spec > characters
* emotion：characters > traits fallback
* motion：必须数组化
* traits：直接透传 characters.yaml.traits
* visual_keywords：直接透传 characters.yaml.visual_keywords

### type: crowd

来源：

* shot_spec.subject.crowd_id

字段：

* crowd_id：shot_spec.subject.crowd_id
* description：shot_spec.subject 描述

### type: environment

来源：

* shot_spec.environment

字段：

* description：shot_spec.environment 描述

---

## 2. Action（行为）

规则：

```
IF motion 非空：
    primary = motion[0]
    secondary = motion[1:]
ELSE:
    primary = "still"
    secondary = []
```

---

## 3. Environment（环境）

来源：

* shot_spec.environment
* scenes.yaml（location_id）

字段填充：

* type → scene.type
* scale → scene.scale
* description → scene.environment
* time → scene.time（如果存在）

### props

shot_spec.props > scene.props

### lighting

scene.appearances[shot_id] > scene.default

---

## 4. Camera（镜头）

来源：

* shot_spec.camera
* shot_spec.visual_intent

### 标准化

* movement：数组
* framing：

```
close_up → tight
medium → balanced
wide → loose
```

* perspective：

```
默认 = objective
```

---

## 5. Style（风格）

来源：

* visual_intent

### 映射

```
style.base = visual_intent.style
style.mood = visual_intent.atmosphere
style.genre = "drama"
```

### 推断

* intensity：

```
high emotion → high
else → medium
```

* realism：

```
cinematic → realistic
short_drama → stylized
```

* pacing：

```
narrative_function = "reaction" → "fast"
else → "slow"
```

---

## 6. Continuity

直接透传：

```yaml
continuity:
  previous_shot_id
  maintain
  changes
```

---

## 7. Weights（默认值）

```yaml
weights:
  emotion: 1.0
  motion: 1.0
  lighting: 1.0
```

---

## 8. Meta（调试）

```yaml
meta:
  priority_source:
    expression: "shot_spec" | "characters"
    lighting: "scene" | "override"
```

---

# Output Schema（prompt_ir.yaml）

```yaml
chapter_id: string
total_shots: integer
generated_at: timestamp
platform: string

shots:
  - shot_id: string

    # ===== 主体（角色/群体/环境）=====
    subject:
      type: enum[character, crowd, environment]

      # 当 type = character
      character:
        id: string
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
        traits: [string]
        visual_keywords: [string]

      # 当 type = crowd
      crowd:
        crowd_id: string
        description: string

      # 当 type = environment
      environment:
        description: string

    # ===== 行为层 =====
    action:
      primary: string
      secondary: [string]

    # ===== 场景层 =====
    environment:
      location_id: string
      location_name: string
      type: string
      scale: string
      description: string
      time: string  # day / night
      props: [string]
      lighting:
        type: string
        description: string
        color_temperature: string
      atmosphere: string
      visual_keywords: [string]

    # ===== 镜头层 =====
    camera:
      shot_type: string
      composition: string
      angle: string
      movement: [string]
      lens: string
      aperture: string
      focus: string
      framing: string
      perspective: string

    # ===== 风格层 =====
    style:
      base: string  # cinematic / short_drama
      mood: string  # tense / luxury / dark
      pacing: string  # slow / fast
      genre: string  # drama / romance / revenge
      intensity: string
      realism: string

    # ===== 连贯性 =====
    continuity:
      previous_shot_id: string
      maintain: [string]
      changes: [string]

    weights:
      emotion: float
      motion: float
      lighting: float

    # ===== 元信息 =====
    meta:
      priority_source:
        expression: string  # "shot_spec" / "characters"
        lighting: string     # "scene" / "override"
```

---

# Output Rules

* 所有字段必须存在（使用默认值如果不可用）
* motion / movement 必须为数组
* 不允许自然语言句子
* 不允许调用 mapping 层
* chapter_id / total_shots / generated_at / platform 为必填文件头

---

# Anti-Patterns

❌ 拼接 prompt
❌ 输出英文描述
❌ 使用 emotion_map / motion_map
❌ 引入模型字段
❌ 缺少文件头字段

---

# Pipeline

```
shot_spec + characters + scenes
        ↓
    IR Builder
        ↓
   prompt_ir.yaml
```

---

# Final Note

IR Builder 的职责不是"生成画面"，而是：

👉 **统一语义，降低复杂度，解耦后续系统**
