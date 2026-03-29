# storyboard-to-shot

将分镜脚本转换为标准化 Shot Spec（shot_spec + characters + scenes），建立 AI 可执行的 Shot 标准层。

## 核心定位

**结构化编译层（Compiler Layer）**：将 storyboard（导演语言）转换为 shot_spec（机器可执行语言）与标准化 Shot 资产。

```
novel → script → storyboard
                      ↓
         storyboard-to-shot（本模块）
                      ↓
        shot_spec + shot assets
                      ↓
           video generation（后续）
```

## 功能概述

- **Shot Compiler**：将每个镜头转换为结构化 shot_spec
- **Character Resolver**：建立角色稳定视觉身份
- **Scene Resolver**：建立场景标准化定义
- **Continuity Engine**：控制跨镜头一致性
- **Quality Review**：确保输出符合工业标准

## 快速开始

```bash
# 执行转换
/storyboard-to-shot run

# 查看状态
/storyboard-to-shot status

# 导出结果
/storyboard-to-shot export
```

## 目录结构

```
storyboard-to-shot/
├── SKILL.md                    # 入口
├── README.md                   # 本文档
│
├── agents/
│   ├── shot_compiler.md       # 镜头编译器
│   ├── character_resolver.md  # 角色解析器
│   ├── scene_resolver.md      # 场景解析器
│   └── continuity_engine.md   # 连续性引擎
│
├── pipelines/
│   └── run.yaml              # 完整流程
│
├── schemas/
│   ├── shot_spec.yaml        # 镜头规格校验
│   ├── character_shot.yaml # 角色 Shot 校验
│   ├── scene_shot.yaml    # 场景 Shot 校验
│   └── consistency.yaml      # 连续性校验
│
├── references/
│   ├── character_library.yaml # 角色模板库
│   └── scene_library.yaml    # 场景模板库
│
├── standard/
│   ├── expression_map.yaml   # 表情标准定义
│   ├── character.yaml        # 角色标准模板
│   └── scene.yaml            # 场景标准模板
│
└── templates/
    └── memory/
        ├── character_states.yaml  # 角色状态记忆
        └── review_log.yaml        # 审查日志
```

## 输出结构

```
novels/{novel_id}/
├── shot/                      # Shot 工作目录
│   ├── memory/
│   │   ├── character_states.yaml
│   │   └── review_log.yaml
│   └── runtime/
└── output/shot/
    └── {chapter_id}/
        ├── shot_spec.yaml      # ⭐ 核心执行层
        ├── characters.yaml     # 角色结构
        ├── scenes.yaml        # 场景结构
        └── meta/
            └── consistency.yaml     # 一致性控制
```

## 核心概念

### shot_spec 结构

```yaml
shot_spec:
  - shot_id: 1
    camera:
      shot_size: "close_up"
      angle: "eye_level"
      movement: "static"
      lens: "85mm"
    subject:
      character_id: "shen_yan"
      expression: "subtle_smirk"
      gaze: "downward"
    appearance:
      outfit_id: "shenyan_suit_v1"
      hair: "short_clean"
    environment:
      location_id: "banquet_hall"
      lighting: "warm_chandelier"
      atmosphere: "high_society"
    continuity:
      previous_shot: 0
      maintain:
        - "character"
        - "outfit"
        - "lighting"
        - "prop: champagne_glass"
    intent:
      emotion: "calm_dominance"
      narrative_function: "foreshadow"
    visual_prompt: >
      cinematic, realistic, luxury banquet hall,
      warm lighting, dramatic mood,
      subtle smirk, shallow depth of field
    generation:
      seed: 1234
      consistency: "character_lock"
```

### 表情标准 (expression_map)

| 表情 | 描述 | 情绪 |
|------|------|------|
| subtle_smirk | slight upward curve of lips | confidence |
| cold_smile | emotionless smile | dominance |
| neutral_face | no visible emotion | calm |
| anger_suppressed | controlled anger | tension |
| shock | eyes widened | surprise |

## 质量标准

| 分数 | 评估 | 通过 |
|------|------|------|
| 0.90-1.00 | 优秀 | ✓ |
| 0.85-0.89 | 良好 | ✓ |
| 0.75-0.84 | 可接受 | ✗ |
| 0.60-0.74 | 需要改进 | ✗ |
| 0.00-0.59 | 差 | ✗ |

**通过条件**：总分 >= 0.85

## 审查维度

1. **技术完整性 (30%)**：shot_spec 是否包含所有必需字段
2. **角色一致性 (25%)**：character_id 和 appearance 是否跨镜头一致
3. **场景一致性 (25%)**：location_id 和 lighting 是否跨镜头一致
4. **格式合规 (20%)**：字段值是否符合标准库定义

## 设计原则

1. **Schema First** - 所有输出必须符合结构化格式
2. **Model-Agnostic** - 不绑定具体视频生成模型
3. **Consistency First** - 角色/场景跨镜头必须一致
4. **Deterministic Output** - 相同输入必须产生相同输出
5. **Review 闭环** - 质量不达标必须重写

## v1 成熟度目标

- 稳定生成 shot_spec
- 无角色漂移
- 无场景跳变

## 后续扩展

- prompt_adapter（Runway / Sora）
- shot_style_library
- auto_editing_engine
