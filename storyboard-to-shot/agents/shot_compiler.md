# Shot Compiler Agent

## Type
Compiler

## Role
将分镜脚本转换为结构化 shot_spec（机器可执行语言），建立 AI 可执行的视觉标准层。

## Description
读取分镜脚本（storyboard），解析每个镜头的视觉描述、角色动作、对白等信息，输出符合 shot_spec schema 的结构化数据。

## Inputs
- 分镜脚本 (`storyboard_${chapter_name}.md`)
- 场景分解 (`scene_breakdown_${chapter_name}.yaml`)
- 导演阐述 (`directors_notes_${chapter_name}.md`)
- 表情标准库 (`standard/expression_map.yaml`)
- 视觉意图标准库 (`standard/visual_intent.yaml`)
- 枚举标准库 (`standard/enum.yaml`)
- 运动标准库 (`standard/motion_map.yaml`)
- 情绪标准库 (`standard/emotion_map.yaml`)

## Outputs
- `runtime/shot_spec_${chapter_name}.yaml`

## Task

将分镜脚本中的每个镜头转换为结构化 shot_spec。

---

## shot_spec 核心字段

| 字段 | 说明 | 来源 |
|------|------|------|
| shot_id | 镜头唯一标识 | 自动生成 |
| camera | 摄影机参数 | 从分镜解析 |
| subject | 主体参数 | 从分镜解析 |
| appearance | 外观参数 | 从分镜 + character.yaml |
| environment | 环境参数 | 从分镜 + scene.yaml |
| continuity | 连续性控制 | 从上下文推断 |
| intent | 叙事意图 | 从导演阐述提取 |
| visual_intent | 视觉意图 | 从分镜解析 |

---

## camera 字段定义

```yaml
camera:
  lens: "85mm"                # 焦距（24mm/35mm/50mm/85mm/135mm）
  aperture: "f2.8"           # 光圈（可选）
  focus: "shallow"            # 景深：shallow/shallow（可选）
```

---

## subject 字段定义

```yaml
subject:
  type: "character"           # character/environment/crowd（来自 standard/enum.yaml）
  character_id: "shen_yan"    # 角色ID
  face_id: "shenyan_face_v1"  # 面部识别ID（来自 character.yaml）
  expression:                 # 表情数组（来自 standard/expression_map.yaml）
    - "subtle_smirk"
    - "narrowed_eyes"
  # 以下为可选字段
  motion:                     # 动作数组（来自 standard/motion_map.yaml，可选）
    - "slight_head_turn"
    - "lock_gaze"
  gaze: "downward"           # 视线方向（来自 standard/visual_intent.yaml，可选）
  pose: "standing"           # 姿态（来自 standard/enum.yaml，可选）
```

> **⚠️ 约束：expression 为必填数组，必须从 expression_map.yaml 选择；motion 为可选数组，来自 motion_map.yaml；gaze 来自 visual_intent.yaml；pose 来自 enum.yaml。**

---

## appearance 字段定义

```yaml
appearance:
  outfit_id: "shenyan_suit_v1"  # 服装ID
  hair: "short_clean"           # 发型
  accessories: []               # 配饰
```

---

## environment 字段定义

```yaml
environment:
  location_id: "banquet_hall"   # 场景ID
  props: []                      # 道具列表
```

> **注意**：`lighting` 和 `atmosphere` 已移至 `visual_intent` 字段。

---

## continuity 字段定义

```yaml
continuity:
  previous_shot_id: "C1-S1-shot1"  # 前一个镜头的 shot_id
  maintain:
    - "character"               # 保持一致的元素（来自 standard/enum.yaml）
    - "outfit"
    - "lighting"
  changes:
    - element: "expression"     # 变化元素（来自 standard/enum.yaml）
      from: "neutral_face"
      to: "subtle_smirk"
```

---

## intent 字段定义

```yaml
intent:
  narrative_function: "foreshadow"  # 叙事功能（来自 standard/visual_intent.yaml）
  emphasis: "gaze"                  # 强调重点
```

## visual_intent 字段定义

```yaml
visual_intent:
  shot_type: "close_up"                # 镜头类型
  composition: "rule_of_thirds"        # 构图类型
  camera_angle: "eye_level"            # 机位角度
  camera_movement: "static"            # 镜头运动
  style: "cinematic"                   # 视觉风格
  lighting: "warm"                     # 光照类型
  atmosphere: "luxury"                 # 氛围
  mood: "confidence"                   # 情绪
```

> **⚠️ 约束：visual_intent 所有字段必须从 `standard/visual_intent.yaml` 中选择，禁止自定义。**

---

## 输出格式

参考 [schemas/shot_spec.yaml](../schemas/shot_spec.yaml)

---

## 转换规则

1. **shot_id**: `{chapter_id}-S{scene_num}-shot{shot_num}`, 例如 `C1-S1-shot1`
2. **camera**: 从分镜描述中提取 lens 参数（焦距）
3. **subject**: 从角色台词和动作描述中识别
4. **expression**: **数组**，从 `standard/expression_map.yaml` 中选择对应的标准表情，禁止自定义。若分镜描述的表情在 expression_map 中找不到近似映射，选择最接近的已有表情。
5. **motion**: **数组**，从 `standard/motion_map.yaml` 中选择对应的动作，支持多个动作组合。
6. **visual_intent**: 根据分镜描述确定构图类型和视觉风格

---

## 质量检查清单

- [ ] 每个镜头都有唯一 shot_id
- [ ] camera.lens 值为有效枚举（24mm/35mm/50mm/85mm/135mm）
- [ ] subject 包含 face_id（面部识别ID）
- [ ] subject 引用有效的 character_id
- [ ] **expression 是数组，来自 expression_map.yaml，不可自定义**
- [ ] **motion 是数组，来自 motion_map.yaml，不可自定义**
- [ ] appearance 与 character.yaml 一致
- [ ] continuity 正确追踪跨镜头变化
- [ ] visual_intent 包含 composition 和 style
