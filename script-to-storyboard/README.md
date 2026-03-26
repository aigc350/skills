# Script-to-Storyboard

将剧本转换为分镜脚本，支持镜头设计、景别规划和可视化拍摄指导。

## 功能概述

- **导演视角分析**：从整体视觉风格、叙事节奏、情感曲线分析剧本
- **场景拆解**：将剧本拆分为可拍摄的场景单元，规划镜头覆盖
- **分镜设计**：为每个场景设计具体镜头（景别、角度、运动、时长）
- **质量审查**：四维度评分，确保分镜可执行且连贯

## 快速开始

```bash
# 执行转换
/script-to-storyboard run

# 查看状态
/script-to-storyboard status

# 导出结果
/script-to-storyboard export
```

## 目录结构

```
script-to-storyboard/
├── SKILL.md                    # 入口
├── README.md                   # 本文档
│
├── agents/
│   ├── director.md             # 导演分析
│   ├── scene_breakdown.md      # 场景拆解
│   ├── storyboarder.md         # 分镜设计
│   └── reviewer.md            # 质量审查
│
├── pipelines/
│   └── run.yaml               # 完整流程
│
├── schemas/
│   ├── scene_breakdown.yaml   # 场景拆分校验
│   ├── storyboard.yaml        # 分镜校验
│   └── review.yaml           # 审查结果校验
│
├── references/
│   ├── shot_types.md          # 景别参考
│   ├── camera_movement.md     # 运镜参考
│   └── visual_storytelling.md # 视觉叙事参考
│
└── templates/
    ├── memory/
    │   ├── scene_states.yaml  # 场景状态记忆
    │   └── review_log.yaml    # 审查日志
    ├── scene.md               # 场景模板
    └── shot.md                # 镜头模板
```

## 输出结构

```
novels/{novel_id}/
├── script/                     # 剧本工作目录（来自 novel-to-script）
│   ├── memory/
│   └── runtime/
├── output/
│   ├── script/                 # 剧本输出
│   └── storyboard/             # 分镜输出
│       └── {chapter_id}/
│           ├── directors_notes.md
│           ├── scene_breakdown.yaml
│           ├── storyboard.md
│           └── full_storyboard.md
└── storyboard/                 # 分镜工作目录
    ├── memory/
    │   ├── scene_states.yaml
    │   └── review_log.yaml
    └── runtime/
```

## 核心概念

### 景别 (Shot Types)

| 代码 | 名称 | 描述 |
|------|------|------|
| ELS | 极远景 | 大环境，人物如蚂蚁 |
| LS | 远景 | 人的全身 |
| WS | 全景 | 包含环境的全身 |
| MS | 中景 | 腰部以上 |
| CU | 特写 | 脸部特写 |
| ECU | 大特写 | 眼睛/细节特写 |

### 角度 (Angles)

| 代码 | 名称 | 效果 |
|------|------|------|
| eye_level | 平视 | 客观、中性 |
| high | 高角度 | 俯视，弱小 |
| low | 低角度 | 仰视，强大 |
| dutch | 荷兰角 | 不稳定、紧张 |

### 运动 (Movement)

| 代码 | 名称 | 描述 |
|------|------|------|
| static | 静止 | 无运动 |
| dolly_in | 推镜 | 靠近主体 |
| dolly_out | 拉镜 | 远离主体 |
| track | 跟踪 | 跟随移动 |
| handheld | 手持 | 不稳定感 |

## 质量标准

| 分数 | 评估 | 通过 |
|------|------|------|
| 0.90-1.00 | 优秀 | ✓ |
| 0.85-0.89 | 良好 | ✓ |
| 0.75-0.84 | 可接受 | ✗ |
| 0.60-0.74 | 需要改进 | ✗ |
| 0.00-0.59 | 差 | ✗ |

**通过条件**：总分 >= 0.85 或所有维度 >= 0.85

## 审查维度

1. **技术可行性 (30%)**：镜头是否可以实际拍摄
2. **连续性 (25%)**：角色位置、视线、道具是否连贯
3. **视觉叙事 (25%)**：镜头是否有明确焦点、节奏是否合适
4. **格式合规 (20%)**：景别/角度/运动代码是否正确

## 设计原则

1. **导演视角优先** - 先理解整体视觉风格再拆解
2. **镜头可拍摄** - 每个镜头都应可直接执行
3. **连续性追踪** - 保持场景间的逻辑连贯
4. **Review 闭环** - 质量不达标必须重写
5. **记忆递增** - 不全量重跑，增量处理
