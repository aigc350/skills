# Character Resolver Agent

## Type
Resolver

## Role
从 shot_spec 提取角色视觉信息，按角色维度重组为 per-character 视觉定义文件。

## Description
遍历 shot_spec 中所有 type=character 的 shot，按 character_id 聚合，建立每个角色的完整视觉身份（outfit、hair、accessories、expression 变化链），输出 characters.yaml。

## Inputs
- shot_spec (`shot_spec_${chapter_name}.yaml`)
- 角色标准库 (`standard/character.yaml`)

## Outputs
- `characters_${chapter_name}.yaml`

## Task

### Step 1: 收集角色出场

遍历 shot_spec.shots[]，筛选 `subject.type == "character"` 的 shot，按 `subject.character_id` 分组。

对每个角色，收集所有出场的 shot_id 列表（按 shot 顺序排列）。

### Step 2: 构建角色视觉身份

对每个角色，从 `standard/character.yaml` 查找对应定义，读取：
- `face_id` — 面部识别 ID
- `default_outfit` — 默认服装 ID
- `outfits` — 可用服装列表
- `traits` — 性格特征
- `visual_keywords` — 视觉关键词

如果 character.yaml 中没有该角色（如群演），使用 shot_spec 中的数据构建。

### Step 3: 构建 appearances 数组

对角色的每个出场 shot，提取：

```yaml
- shot_id: "C1-S1-shot3"
  outfit_id: "shenyan_old_suit_v1"     # from shot.appearance.outfit_id
  hair: "short_neat"                    # from shot.appearance.hair
  accessories: []                        # from shot.appearance.accessories
  expression: "neutral_face"            # shot.subject.expression[0]（主表情）
  emotion: "calm"                       # from shot.visual_intent.mood 或推导
  changed_from: null                     # 与前一 shot 的 expression 对比
```

**changed_from 生成规则**：
- 取 `expression`（主表情，即 `subject.expression[0]`）
- 与同一角色的前一个出场 shot 对比
- 如果 expression 发生变化，记录 `changed_from: {前一 shot 的 expression}`
- 如果没有变化，省略 `changed_from` 字段

### Step 4: 构建 continuity 汇总

对每个角色，汇总跨 shot 的连续性信息：

```yaml
continuity:
  outfit_consistent: true               # 所有 shot 的 outfit_id 是否一致
  hair_consistent: true                 # 所有 shot 的 hair 是否一致
  accessories_added: ["smartphone"]     # 相比首次出场新增的配饰
  accessories_removed: []               # 相比首次出场移除的配饰
  expression_changes:                   # 所有 expression 变化点
    - from: "neutral_face"
      to: "subtle_smirk"
      at_shot: "C1-S1-shot4"
```

**accessories 追踪规则**：
- 记录首次出场的 accessories 为基准
- 后续出场中新增的加入 `accessories_added`
- 后续出场中消失的加入 `accessories_removed`

### Step 5: 处理 crowd 类型

对于 `subject.type == "crowd"` 的 shot，创建特殊角色条目：

```yaml
- character_id: "guests"
  type: "crowd"
  crowd_id: "banquet_guests"
  description: "衣香鬓影的宾客"
  visual_keywords:
    - "elegant"
    - "wealthy"
  appearances:
    - shot_id: "C1-S1-shot2"
      atmosphere: "luxury"              # from shot.visual_intent.atmosphere
    - shot_id: "C1-S2-shot12"
      atmosphere: "chaotic"
      changed_from: "luxury"
  continuity:
    atmosphere_shifted: true
```

### Step 6: 输出格式

```yaml
chapter_id: "1"
characters:
  - character_id: "shen_yan"
    face_id: "shenyan_face_v1"
    default_outfit: "shenyan_old_suit_v1"
    outfits:
      shenyan_old_suit_v1:
        description: "略显陈旧的深色西装"
        color: "dark"
        style: "classic"
        condition: "slightly_worn"
    hair: "short_neat"
    traits: ["calm_composed", "observant"]
    visual_keywords: ["understated", "dignified"]
    appearances: [...]
    continuity: {...}
```

---

## 质量检查

- [ ] 每个 character_id 的 face_id 非空
- [ ] appearances 中的 shot_id 都是有效的
- [ ] outfit_consistent 为 false 时，outfits 列表包含所有使用的 outfit_id
- [ ] expression_changes 的 from/to 是有效的 expression_map 值
- [ ] 所有出现的 character_id 都在 characters 列表中
