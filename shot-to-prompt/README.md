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
| **strategies** | 让内容能爆 - 钩子+爽点 | `references/strategies/*.yaml` |

## 统一规则

所有 Agent 必须遵守 [`references/rules/common.rule.md`](references/rules/common.rule.md)：
- 字段所有权规则
- 写入权限控制
- Pipeline 阶段定义
- Semantic vs Text vs Tokens 规范

## 目录结构

```
shot-to-prompt/
├── skill.md                    # Skill 入口（命令执行流程）
├── README.md                   # 架构说明
│
├── agents/                     # ⭐ 8 个执行模块
│   ├── prompt_ir_builder.md         # IR 构建（核心）
│   ├── prompt_canonical_builder.md  # 规范化 + mappings 翻译
│   ├── prompt_enhancer.md           # 策略增强 + styles 风格
│   ├── prompt_asset_builder.md      # 资产构建
│   ├── prompt_consistency_enforcer.md # 一致性强制
│   ├── prompt_temporal_enforcer.md  # 时序处理
│   ├── prompt_fusion.md             # 融合各层 IR
│   └── model_adapter.md             # 平台适配（核心）
│
├── pipelines/
│   └── run.yaml                 # Pipeline 步骤定义
│
├── references/
│   ├── rules/
│   │   └ common.rule.md       # ⭐ 统一规则（所有 agent 遵守）
│   │
│   ├── mappings/                # ⭐ 翻译层
│   │   ├── enums.yaml          # 枚举定义
│   │   ├── camera.yaml         # 镜头类型映射
│   │   ├── lighting.yaml       # 光照氛围映射
│   │   ├── expression_map.yaml # 外在表情映射
│   │   ├── emotion_map.yaml    # 内在情绪映射
│   │   └── motion_map.yaml     # 姿态动作映射
│   │
│   ├── styles/                  # ⭐ 风格层
│   │   ├── short_drama.yaml    # 短剧风格（竖屏/快节奏）
│   │   └── cinematic.yaml      # 电影感风格（横屏/叙事性）
│   │
│   ├── strategies/              # ⭐ 爆点层
│   │   ├── hook_engine.yaml    # Hook 引擎配置
│   │   ├── hook_first_frame.md # 首帧钩子策略
│   │   └── short_drama.md      # 短剧爆点策略
│   │
│   └── platform_templates/      # 平台适配模板
│       ├── sora.md
│       ├── runway.md
│       ├── pika.md
│       ├── kling.md
│       └── hailuo.md
│
├── templates/
│   └── gen_prompt.md           # Prompt 输出模板
│
└── memory/                      # Skill 级记忆
    └── prompt_history.yaml
```

## mappings（翻译层）

### 作用
将 shot_spec 中的结构化字段翻译为 AI 可理解的自然语言描述。

### 文件说明

| 文件 | 映射内容 | 示例 |
|------|---------|------|
| `enums.yaml` | 枚举定义 | subject_state, object_state, role |
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

## Pipeline 流程

详见 [`pipelines/run.yaml`](pipelines/run.yaml)。

| Step | Agent | 输入 | 输出 | 说明 |
|------|-------|------|------|------|
| 0 | check_config | novel.config.md | - | 检查配置 |
| 0 | ensure_directories | - | - | 创建目录结构 |
| 0 | load_mappings | mappings/*.yaml | mappings.yaml | 加载翻译层 |
| 0 | load_styles | styles/*.yaml | styles.yaml | 加载风格层 |
| 0 | load_platform_templates | platform_templates/*.md | platform_templates.yaml | 加载平台模板 |
| 0 | detect_shot_specs | output/shot/{id}/ | pending_shot_specs.yaml | 检测待处理文件 |
| 1 | prompt_ir_builder ⭐ | shot_spec + characters + scenes | prompt_ir.yaml | 编译为统一语义 IR |
| 2 | prompt_canonical_builder | prompt_ir + mappings | prompt_canonical.yaml | 规范化 + 翻译 |
| 3 | prompt_enhancer | prompt_ir + canonical + styles + hook_engine | prompt_enhanced.yaml | 策略增强 + 风格 |
| 4 | prompt_asset_builder | prompt_ir + asset_registry | prompt_asset.yaml | 资产构建 |
| 5 | prompt_temporal_enforcer | prompt_ir + prompt_asset | prompt_temporal.yaml | 时序处理（状态推进） |
| 6 | prompt_consistency_enforcer | prompt_ir + asset + canonical + temporal + registry | prompt_consistency.yaml | 一致性强制 |
| 7 | prompt_fusion | canonical + enhanced + asset + temporal + consistency | prompt_fusion.yaml | 融合各层 IR |
| 8 | model_adapter ⭐ | prompt_fusion + platform_template | final_prompts.yaml | 平台适配 |

> ⭐ = 核心模块

## Prompt 输出格式

### 镜头级 Prompt

```yaml
shot_prompts:
  - shot_id: "C01-S1-shot01"
    prompt: "A man in his 30s, short neat hair, wearing an old but clean suit..."
    negative_prompt: "cartoon, anime, bright, cheerful, low quality..."
    duration: 4
    camera:
      shot_type: "establishing"
      angle: "eye_level"
      movement: "crane"
    referenced_assets:
      - asset_id: "shenyan_male_v1"
        type: "character"
```

### 章节级联 Prompt

```yaml
chapter_prompt:
  chapter_id: "01"
  total_shots: 30
  total_duration: 120
  style: "short_drama"
  platform: "hailuo"
```

## 平台支持

| 平台 | 风格适配 | Prompt 长度限制 | 默认时长 |
|------|---------|---------------|---------|
| Sora | 详细叙事型 | 400 字符 | 10s |
| Runway | 电影感强调镜头语言 | 300 字符 | 5s |
| Pika | 简洁动作导向 | 200 字符 | 3s |
| Kling | 中文友好 | 250 字符 | 5s |
| Hailuo | 短剧优化 | 200 字符 | 4s |

## 小说级目录结构

```
novels/{novel_id}/
├── output/
│   └── shot/
│       └── {chapter_id}/           # shot_spec 源目录
│           ├── shot_spec.yaml
│           ├── characters.yaml
│           └── scenes.yaml
│   └── prompt/                    # 最终输出（暂未使用）
│       └── {chapter_id}/
│           ├── shot_prompt.yaml
│           └── full_prompt.yaml
└── prompt/
    ├── memory/                    # 记忆目录
    │   └── asset_registry.yaml    # 资产注册表
    └── runtime/{chapter_id}/       # 中间产物
        ├── mappings.yaml
        ├── styles.yaml
        ├── platform_templates.yaml
        ├── pending_shot_specs.yaml
        ├── prompt_ir.yaml
        ├── prompt_canonical.yaml
        ├── prompt_enhanced.yaml
        ├── prompt_asset.yaml
        ├── prompt_consistency.yaml
        ├── prompt_temporal.yaml
        ├── prompt_fusion.yaml
        ├── target_platform.yaml
        └── final_prompts.yaml
```