# shot-to-prompt

将 shot_spec 转换为 AI 视频生成模型的 Prompt。

## 核心定位

**Prompt 编译层（Prompt Compiler Layer）**：将结构化 shot_spec（机器语言）转换为自然语言 Prompt（人类语言/AI可执行语言）。

```
storyboard-to-shot（shot_spec）
         │
         ▼
  shot-to-prompt（本模块）
         │
         ▼
   gen_prompt（AI视频模型可执行）
         │
         ▼
   video-generator
```

## 功能概述

- 将 shot_spec 的每个镜头转换为 AI 视频生成 Prompt
- 支持多平台：Sora, Runway, Pika, Kling
- 保持角色/场景一致性
- 输出镜头级和章节级 Prompt

## 目录结构

```
shot-to-prompt/
├── SKILL.md              # 入口
├── README.md             # 文档
│
├── agents/
│   ├── prompt_builder.md     # Prompt 构建
│   └── prompt_optimizer.md  # 平台优化
│
├── pipelines/
│   └── run.yaml              # 完整流程
│
├── schemas/
│   └── gen_prompt.yaml      # Prompt 校验
│
├── references/
│   └── platform_templates/   # 平台模板
│       ├── sora.md
│       ├── runway.md
│       ├── pika.md
│       └── kling.md
│
└── templates/
    └── gen_prompt.md        # 输出模板
```

## Pipeline 流程

```yaml
steps:
  - id: parse_shot_spec
    agent: prompt_builder
    prompt: prompts/builder.md
    schema: schemas/shot_spec.yaml

  - id: build_shot_prompt
    agent: prompt_builder
    prompt: prompts/builder.md
    output: runtime/shot_prompts.yaml

  - id: optimize_prompt
    agent: prompt_optimizer
    prompt: prompts/optimizer.md
    output: runtime/optimized_prompts.yaml

  - id: validate_prompts
    agent: prompt_optimizer
    schema: schemas/gen_prompt.yaml
    on_invalid: retry

  - id: assemble_chapter_prompts
    agent: prompt_builder
    output: runtime/chapter_prompts.yaml

  - id: export
    output: output/gen_prompts/{chapter_id}/
```

## Prompt 输出格式

### 镜头级 Prompt

```yaml
shot_prompts:
  - shot_id: "C01-S1-shot01"
    prompt: "A man in his 30s, short messy hair, wearing a worn leather jacket..."
    negative_prompt: "cartoon, anime, low quality, distorted face..."
    duration: "3-5 seconds"
    camera: "medium shot, eye level, slight push in"

  - shot_id: "C01-S1-shot02"
    prompt: "Close-up of a woman's face, cold expression, dim lighting..."
    negative_prompt: "bright, cartoon, low quality..."
    duration: "2-3 seconds"
    camera: "close-up, low angle, static"
```

### 章节级联 Prompt

```yaml
chapter_prompt:
  chapter_id: "C01"
  full_prompt: "Scene setup: A dark warehouse... [连贯的完整场景描述]"
  duration: "60-90 seconds"
  shots: [...]
```

## 平台支持

| 平台 | 特点 | Prompt 风格 |
|------|------|------------|
| Sora | 长视频，复杂场景 | 详细描述，剧情性强 |
| Runway Gen-3 | 电影感 | 强调镜头语言 |
| Pika | 快速生成 | 简洁，动作导向 |
| Kling | 国产，亚洲面孔 | 中文友好 |

## 与 storyboard-to-shot 的关系

shot-to-prompt 是 storyboard-to-shot 的下游：

- **输入**：shot_spec.yaml（结构化镜头规格）
- **输出**：gen_prompt.yaml（AI 视频模型 Prompt）
- **桥接**：将"机器语言"转为"AI 可理解的人类语言"

## 使用场景

1. **批量生成**：将整章 shot_spec 转为 Prompts
2. **平台适配**：针对不同平台优化同一批 Prompts
3. **风格调整**：调整 Prompt 风格（电影感、写实、动漫等）
