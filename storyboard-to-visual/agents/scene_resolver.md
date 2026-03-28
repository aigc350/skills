# Scene Resolver Agent

## Type
Resolver

## Role
建立场景标准化视觉定义，确保场景在跨镜头中视觉一致性。

## Description
分析分镜中的场景描述，解析其光照、道具、氛围等视觉元素，输出标准化的场景视觉定义。

## Inputs
- 分镜脚本 (`storyboard_${chapter_name}.md`)
- shot_spec 输出 (`shot_spec_${chapter_name}.yaml`)
- 场景标准库 (`standard/scene.yaml`)
- 场景状态记忆 (`visual/memory/scene_states.yaml`)

## Outputs
- `runtime/scenes_${chapter_name}.yaml`

---

## 职责

1. **识别场景位置** - 从 shot_spec 中提取 location_id
2. **解析光照条件** - 每个镜头中的光照类型、颜色、温度
3. **追踪道具状态** - 记录关键道具的出现和使用
4. **生成视觉定义** - 输出符合 scene_visual.yaml schema 的结构

---

## scene_visual 结构

```yaml
scene_visual:
  location_id: "banquet_hall"
  appearances:
    - shot_id: "C1-S1-shot1"
      lighting:
        type: "warm_chandelier"
        color_temperature: "warm"
        description: "warm ambient light from chandeliers"
      props:
        - "round_table"
        - "champagne_glass"
        - "crystal_decorations"
      atmosphere: "luxury"
      visual_keywords:
        - "gold_accents"
        - "elegant"
        - "festive"
    - shot_id: "C1-S1-shot5"
      lighting:
        type: "warm_chandelier"
        color_temperature: "warm"
        description: "warm ambient light, slightly dimmer"
      props:
        - "round_table"
        - "champagne_glass"
        - "crystal_decorations"
        - "velvet_curtains"
      atmosphere: "high_society"
      visual_keywords:
        - "gold_accents"
        - "elegant"
        - "moody"
      changed_from: "C1-S1-shot1"
      changes:
        - element: "props"
          added: ["velvet_curtains"]
  continuity:
    lighting_consistent: true
    props_added: []
    props_removed: []
    atmosphere_shifted: false
```

---

## 连续性规则

### 光照连续性
- 同一场景内光照应保持一致
- 光照变化需要明确说明
- 使用 scene.yaml 中的标准光照类型

### 道具连续性
- 记录道具的出现/消失
- 道具状态变化需标注
- 使用 scene.yaml 中的标准道具列表

### 氛围连续性
- 追踪氛围关键词变化
- 显著变化需要说明原因

---

## 与 scene.yaml 的关系

从 `standard/scene.yaml` 读取：
- location_id：场景标识
- type：室内/室外
- scale：规模
- environment：环境描述
- lighting：标准光照定义
- props：标准道具列表
- atmosphere：氛围关键词
- visual_keywords：视觉关键词

---

## 质量检查清单

- [ ] 所有出现的场景都有 visual 定义
- [ ] lighting 类型符合 scene.yaml 标准
- [ ] props 引用有效
- [ ] 跨镜头光照一致性
- [ ] 与 scene.yaml 标准一致
