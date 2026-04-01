# shot-to-prompt

将 shot_spec 转换为 AI 视频生成模型的 Prompt。

## 核心定位

**Prompt 编译层（Prompt Compiler Layer）**：将结构化 shot_spec（机器语言）转换为自然语言 Prompt（人类语言/AI可执行语言）。

```
storyboard-to-shot（shot_spec）
         │
         ▼
    mappings（翻译层）- 让 AI "听懂"
         │
         ▼
    styles（风格层）- 让内容 "有辨识度"
         │
         ▼
  strategies（爆点层）- 让内容 "能爆"
         │
         ▼
   gen_prompt（AI视频模型可执行）
         │
         ▼
   video-generator
```

## 三层架构

| 层 | 目的 | 文件 |
|----|------|------|
| **mappings** | 让 AI 听懂 - 字段翻译 | `references/mappings/*.yaml` |
| **styles** | 让内容有辨识度 - 风格统一 | `references/styles/*.yaml` |
| **strategies** | 让内容能爆 - 钩子+爽点 | `references/strategies/*.md` |

## 目录结构

```
shot-to-prompt/
├── SKILL.md
├── README.md
│
├── agents/
│   ├── prompt_builder.md     # 三层处理入口
│   ├── prompt_optimizer.md   # 平台优化
│   └── prompt_enhancer.md     # 策略增强
│
├── pipelines/
│   └── run.yaml
│
├── schemas/
│   └── gen_prompt.yaml
│
├── references/
│   ├── mappings/              # ⭐ 翻译层
│   │   ├── camera.yaml       # 镜头类型映射
│   │   ├── lighting.yaml     # 光照氛围映射
│   │   ├── expression_map.yaml   # 外在表情映射
│   │   ├── emotion_map.yaml      # 内在情绪映射
│   │   └── motion_map.yaml       # 姿态动作映射
│   │
│   ├── styles/               # ⭐ 风格层
│   │   ├── short_drama.yaml  # 短剧风格（竖屏/快节奏）
│   │   └── cinematic.yaml    # 电影感风格（横屏/叙事性）
│   │
│   ├── strategies/           # ⭐ 爆点层
│   │   ├── hook_first_frame.md  # 首帧钩子策略
│   │   └── short_drama.md      # 短剧爆点策略
│   │
│   └── platform_templates/   # 平台适配
│       ├── sora.md
│       ├── runway.md
│       ├── pika.md
│       └── kling.md
│
├── templates/
│   ├── gen_prompt.md
│   └── log.yaml              # ⭐ 生成日志模板
│
└── memory/                   # ⭐ 新增记忆目录
    └── prompt_history.yaml
```

## mappings（翻译层）

### 作用
将 shot_spec 中的结构化字段翻译为 AI 可理解的自然语言描述。

### 文件说明

| 文件 | 映射内容 | 示例 |
|------|---------|------|
| `camera.yaml` | shot_type, camera_angle, camera_movement, composition | `wide` → "wide shot showing full environment" |
| `lighting.yaml` | lighting, atmosphere, style | `low_key` → "low-key lighting with dramatic shadows" |
| `expression_map.yaml` | expression（外在表情） | `cold_smile` → "cold, emotionless smile, eyes unchanged" |
| `emotion_map.yaml` | emotion（内在情绪） | `calm` → "内心平静，沉着应对" |
| `motion_map.yaml` | pose, gaze, narrative_function | `standing` → "standing upright" |

## styles（风格层）

### 作用
给 Prompt 注入统一风格/世界观/视觉体系，让内容有辨识度。

### short_drama（短剧风格）
- **场景**: 抖音/快手 1-3 分钟竖屏短剧
- **特点**: 强冲突、快节奏、爽点密集、情绪爆发
- **视觉**: 9:16 竖屏，特写为主，2-4 秒/镜头

### cinematic（电影感风格）
- **场景**: 长视频、剧情片
- **特点**: 叙事性强、镜头语言丰富、氛围营造
- **视觉**: 16:9 横屏，多样化镜头，节奏从容

## strategies（爆点层）

### 作用
给内容注入钩子和爽点，让内容能爆。

### hook_first_frame（首帧钩子）
- 情绪冲击型、悬念型、冲突型、动作中断型、反差型
- 前 3 秒抓住观众，制造"为什么"的疑问

### short_drama（短剧爆点）
- **打脸爽点**: 弱者在场 → 强者羞辱 → 身份揭晓 → 反转打脸
- **身份逆转**: 被看不起 → 真实身份揭晓 → 全场震惊
- **甜宠时刻**: 暧昧 → 突破 → 撒糖
- **热血逆袭**: 被压制 → 绝地反击 → 胜利
- **悬疑揭秘**: 铺垫 → 暗示 → 揭晓

## Log 机制

每个 prompt 生成后记录：

```yaml
log:
  - shot_id: "C01-S1-shot01"
    timestamp: "2026-03-29T10:00:00"
    platform: "sora"
    input:
      shot_spec_hash: "sha256:..."
    processing:
      style_applied: "short_drama"
      mappings_used: [camera.yaml, lighting.yaml, expression_map.yaml]
      strategies_applied: [hook_first_frame]
    output:
      prompt_length: 280
      prompt_hash: "sha256:..."
    quality:
      hooks_injected: true
      explosive_points: [face_slapping]
```

## Pipeline 流程

```yaml
steps:
  - id: parse_shot_spec
    description: 解析 shot_spec 结构

  - id: apply_mappings
    description: 执行翻译层（mappings）
    input: shot_spec
    output: mapped_descriptions

  - id: apply_styles
    description: 执行风格层（styles）
    input: mapped_descriptions
    style: short_drama  # 或 cinematic
    output: styled_prompts

  - id: apply_strategies
    description: 执行爆点层（strategies）
    input: styled_prompts
    output: enhanced_prompts

  - id: optimize_for_platform
    description: 平台优化
    platform: sora  # 或 runway/pika/kling
    output: final_prompts

  - id: log_generation
    description: 记录生成日志
    output: memory/prompt_history.yaml
```

## Prompt 输出格式

### 镜头级 Prompt

```yaml
shot_prompts:
  - shot_id: "C01-S1-shot01"
    prompt: "A man in his 30s, short neat hair, wearing an old but clean suit..."
    negative_prompt: "cartoon, anime, bright, cheerful, low quality..."
    duration: "3-5 seconds"
    camera: "establishing shot, crane down movement"
    style: "cinematic, film-quality photography"
    hook_frame: "HOOK - the moment before revelation"
    explosive_point: null  # 或 "face_slapping"
```

### 章节级联 Prompt

```yaml
chapter_prompt:
  chapter_id: "01"
  full_prompt: "Scene setup: A luxurious banquet hall..."
  style: "short_drama"
  total_duration: "60-90 seconds"
  hooks: ["首帧悬念", "身份揭晓"]
  explosive_points: ["打脸爽点", "逆转时刻"]
```

## 平台支持

| 平台 | 风格适配 | Prompt 长度限制 |
|------|---------|---------------|
| Sora | 详细叙事型 | 400 字符 |
| Runway | 电影感强调镜头语言 | 300 字符 |
| Pika | 简洁动作导向 | 200 字符 |
| Kling | 中文友好 | 250 字符 |
