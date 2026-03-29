# Prompt Optimizer Agent

## 类型
Optimizer - Prompt 优化器

## 职责
针对不同 AI 视频生成平台优化 Prompt

## 支持平台

| 平台 | 模型 | 特点 |
|------|------|------|
| Sora | OpenAI Sora | 长视频（60s+），复杂场景，剧情性强 |
| Runway | Gen-3 Alpha | 电影感，高质量，镜头语言丰富 |
| Pika | Pika 1.5 | 快速生成，动作流畅，简洁风格 |
| Kling | 快手可灵 | 国产，亚洲面孔支持好，中文友好 |

## 输入

### 来自 prompt_builder 的结构化 Shot Prompt

```yaml
shot_prompts:
  - shot_id: "C01-S1-shot01"
    subject_description: "A man in his 30s, short messy hair..."
    scene_description: "A dimly lit abandoned warehouse..."
    camera_description: "Wide shot, low angle looking up..."
    style_description: "Cinematic, film noir atmosphere..."
    prompt: "A man in his 30s, short messy hair..."
    negative_prompt: "cartoon, anime, bright..."
    duration: "3-5 seconds"
```

## 输出

### 平台优化后的 Prompt

```yaml
optimized_prompts:
  - shot_id: "C01-S1-shot01"
    platform: "sora"
    prompt: "Cinematic film scene: A man in his 30s with short messy hair, wearing a worn leather jacket, stands in a dimly lit abandoned warehouse. Cold, calculating expression with an emotionless smile. Dramatic low-key lighting creates deep shadows on his face. Low angle shot slowly pushes in. Film noir aesthetic. Shot on 35mm anamorphic lens."
    negative_prompt: "anime, cartoon, low quality, distorted face, extra limbs, watermark, text, signature, logo, bright lighting, cheerful"
    parameters:
      duration: 5
      resolution: "1920x1080"
      motion: "medium"
    metadata:
      prompt_length: 280
      style_tags: ["film_noir", "cinematic", "dramatic"]
```

## 平台优化规则

### Sora 优化

| 规则 | 说明 |
|------|------|
| 增加场景设定 | "Cinematic film scene: ..." |
| 强调时间线 | "60 seconds, continuous shot" |
| 丰富细节 | 加入情绪、氛围、镜头运动描述 |
| 避免冲突 | Sora 不擅长处理快速切换 |

### Runway 优化

| 规则 | 说明 |
|------|------|
| 镜头语言 | "Medium shot, eye level, static" |
| 风格标签 | "Runway Gen-3 Alpha style" |
| 负面 Prompt | 强调质量和技术规格 |

### Pika 优化

| 规则 | 说明 |
|------|------|
| 简洁为主 | 避免过长描述 |
| 动作明确 | "Character walks towards camera" |
| 适合短片段 | 10秒以内最佳 |

### Kling 优化

| 规则 | 说明 |
|------|------|
| 中文友好 | 支持中文 Prompt |
| 亚洲面孔 | 强调东亚人特征 |
| 国产风格 | 武侠、古风支持好 |

## 参数映射

| shot_spec | Sora | Runway | Pika | Kling |
|-----------|------|--------|------|-------|
| shot_type: wide | "wide shot" | "wide shot" | "wide" | "全景" |
| camera_movement: dolly_in | "slow push in" | "dolly in" | "zoom in" | "推进" |
| style: cinematic | "cinematic" | "cinematic" | "film" | "电影感" |
| duration | 3-5s | 4-10s | 3-5s | 5-10s |

## 优化策略

### 1. Prompt 压缩
- 原始 Prompt 可能超过平台限制
- 保留核心元素，压缩修饰词

### 2. 负面 Prompt 扩展
- 根据平台弱点扩展负面 Prompt
- 避免常见失败模式

### 3. 参数标准化
- 分辨率、时长、运动强度标准化
- 平台特定参数映射
