# Prompt Builder Agent

## 类型
Builder - Prompt 构建器

## 职责
将 shot_spec 转换为结构化 Prompt 文本

## 输入

### 来自 storyboard-to-shot 的 shot_spec

```yaml
chapter_id: "C01"
metadata:
  total_shots: 12
  characters: [zhang_san, li_si]
  locations: [warehouse, street]
shots:
  - shot_id: "C01-S1-shot01"
    camera:
      lens: "50mm"
      aperture: "f2.0"
      focus: "shallow"
    subject:
      type: "character"
      character_id: "zhang_san"
      face_id: "zhangsan_face_v1"
      expression: "cold_smile"
      gaze: "forward"
      pose: "standing"
    appearance:
      outfit_id: "leather_jacket_001"
      hair: "short messy"
      accessories: ["silver ring", "old watch"]
    environment:
      location_id: "warehouse"
      props: ["flashlight", "door"]
    continuity:
      maintain: ["outfit", "expression"]
      changes: []
    intent:
      narrative_function: "establish"
      emphasis: "悬念氛围"
    visual_intent:
      shot_type: "wide"
      composition: "rule_of_thirds"
      camera_angle: "low_angle"
      camera_movement: "dolly_in"
      style: "cinematic"
      lighting: "low_key"
      atmosphere: "dark"
      emotion: "tension"
```

## 输出

### 结构化 Shot Prompt

```yaml
shot_prompts:
  - shot_id: "C01-S1-shot01"
    subject_description: "A man in his 30s, short messy hair, wearing a worn leather jacket. Cold, calculating expression."
    scene_description: "A dimly lit abandoned warehouse. Rusty metal doors, scattered debris on the floor. A single beam of light from a broken window."
    camera_description: "Wide shot, low angle looking up at the character. Slow dolly in movement. Shallow depth of field."
    style_description: "Cinematic, film noir atmosphere. Low-key lighting with high contrast. Dark, moody tones."
    lighting_description: "Single dramatic spotlight from above, deep shadows on face."
    prompt: "A man in his 30s, short messy hair, wearing a worn leather jacket, stands in a dimly lit abandoned warehouse. Cold, calculating expression. Single dramatic spotlight from above creates deep shadows. Low angle camera slowly pushes in. Cinematic, film noir style. Shot on 35mm film."
    negative_prompt: "cartoon, anime, bright, cheerful, low quality, distorted face, extra limbs, watermark, text"
    duration: "3-5 seconds"
    continuity_tags:
      - "outfit: leather_jacket_001"
      - "character: zhang_san"
```

## Prompt 构建规则

### 1. Subject 描述转换

| shot_spec | Prompt 描述 |
|-----------|------------|
| `expression: cold_smile` | "cold, emotionless smile" |
| `expression: subtle_smirk` | "slight smirk, hint of confidence" |
| `pose: standing` | "stands confidently" |
| `gaze: forward` | "looks directly into camera" |

### 2. Environment 描述转换

| shot_spec | Prompt 描述 |
|-----------|------------|
| `location_id: warehouse` | "abandoned warehouse with rusty metal structure" |
| `props: [flashlight]` | "holding a flashlight creating a beam of light" |
| `atmosphere: dark` | "dark, shadowy atmosphere" |

### 3. Camera 描述转换

| shot_spec | Prompt 描述 |
|-----------|------------|
| `shot_type: wide` | "wide shot showing full environment" |
| `camera_angle: low_angle` | "low angle shot looking up" |
| `camera_movement: dolly_in` | "slowly pushes in towards subject" |

### 4. Style 描述转换

| shot_spec | Prompt 描述 |
|-----------|------------|
| `style: cinematic` | "cinematic, film-quality photography" |
| `lighting: low_key` | "low-key lighting with dramatic shadows" |
| `atmosphere: tense` | "tense, suspenseful atmosphere" |

## 质量要求

1. **描述具体化**：避免模糊词汇，使用具体细节
2. **保持一致性**：同一角色跨镜头描述一致
3. **平台适配**：输出可供后续平台优化器使用
4. **镜头语言**：融入专业镜头术语
