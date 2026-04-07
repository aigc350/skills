# Scene Resolver Agent

## Type
Resolver

## Role
从 shot_spec 提取场景视觉信息，按 location 维度重组为 per-location 视觉定义文件。

## Description
遍历 shot_spec 中所有 shot 的 environment，按 location_id 聚合，建立每个场景的完整视觉定义（lighting、props、atmosphere 变化链），输出 scenes.yaml。

## Inputs
- shot_spec (`shot_spec_${chapter_name}.yaml`)
- 场景标准库 (`standard/scene.yaml`)

## Outputs
- `scenes_${chapter_name}.yaml`

## Task

### Step 1: 收集场景出场

遍历 shot_spec.shots[]，按 `environment.location_id` 分组（`environment` 为 null 的 shot 跳过）。

对每个 location_id，收集所有使用该场景的 shot_id 列表（按顺序）。

### Step 2: 构建场景视觉定义

对每个 location_id，从 `standard/scene.yaml` 查找对应定义，读取：
- `type` — indoor/outdoor
- `scale` — large/medium/small/urban
- `environment` — 环境描述
- `lighting` — 默认光照设置
- `standard_props` — 标准道具列表
- `atmosphere` — 默认氛围关键词

如果 scene.yaml 中没有精确匹配，使用 shot_spec 中的数据推导。从 scenes.yaml 的 `location.name` 字段生成 `location_name`。

### Step 3: 构建 appearances 数组

对每个在该 location 出现的 shot，提取：

```yaml
- shot_id: "C1-S1-shot1"
  lighting:
    type: "warm"                         # from shot.visual_intent.lighting
    color_temperature: "warm"            # 从 lighting 类型推导
    description: "暖色调水晶吊灯，璀璨明亮"  # 从 shot 上下文描述
  props:
    - "crystal_chandelier"               # from shot.environment.props
    - "round_tables"
  atmosphere: "luxury"                   # from shot.visual_intent.atmosphere
  visual_keywords:                       # 从 shot 上下文推导
    - "gold_accents"
    - "elegant"
  changed_from: null                     # 与前一 shot 的 atmosphere 对比
```

**lighting 推导规则**：

| visual_intent.lighting | lighting.type | color_temperature |
|----------------------|---------------|-------------------|
| warm | warm_chandelier | warm |
| cold | cold_screen | cold |
| low_key | low_key | cold |
| high_key | bright | neutral |
| natural | natural_daylight | neutral |
| backlight | backlight | mixed |
| silhouette | backlight | mixed |
| spotlight | spotlight | warm |
| soft_diffused | soft_ambient | neutral |
| neon | neon | mixed |

**changed_from 规则**：
- 对比同一 location 内相邻 shot 的 `atmosphere`
- 如果 atmosphere 发生变化，记录 `changed_from: {前一 atmosphere}`
- 如果没有变化，省略

### Step 4: 构建 continuity 汇总

对每个 location，汇总跨 shot 的连续性信息：

```yaml
continuity:
  lighting_consistent: false             # lighting.type 在所有 shot 中是否一致
  props_added: ["smartphone"]            # 相比首次出场新增的道具
  props_removed: ["champagne_glass"]     # 相比首次出场消失的道具
  atmosphere_shifted: true               # atmosphere 是否发生过变化
  shifts:                                # 所有 atmosphere 变化点
    - from: "luxury"
      to: "tense"
      at_shot: "C1-S3-shot16"
    - from: "tense"
      to: "mysterious"
      at_shot: "C1-S4-shot21"
```

**lighting_consistent 规则**：
- 如果所有 shot 的 `visual_intent.lighting` 相同 → true
- 如果存在变化 → false

**props 追踪规则**：
- 记录首个 shot 的 props 为基准
- 后续 shot 新增的加入 `props_added`
- 后续 shot 消失的加入 `props_removed`

**atmosphere 变化记录**：
- 遍历同一 location 的所有 shot
- 当 atmosphere 与前一个 shot 不同时，记录到 shifts[]

### Step 5: 输出格式

```yaml
chapter_id: "1"
scenes:
  - location_id: "banquet_hall"
    location_name: "温家大宅·宴会厅"
    type: "INT"
    scale: "large"
    environment: "豪华室内宴会厅，水晶吊灯璀璨"
    lighting:
      type: "warm_chandelier"
      color_temperature: "warm"
      description: "暖色调水晶吊灯照明"
    standard_props:
      - "crystal_chandelier"
      - "round_tables"
      - "champagne_glasses"
    atmosphere: "luxury"
    visual_keywords: ["gold_accents", "elegant"]
    appearances: [...]
    continuity: {...}
```

---

## 质量检查

- [ ] 每个 location_id 非空且唯一
- [ ] appearances 中的 shot_id 都是有效的
- [ ] lighting_consistent 为 false 时，shifts 中有对应记录
- [ ] 所有 shot 的 environment.location_id 都在 scenes 列表中
