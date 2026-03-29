# Character Resolver Agent

## Type
Resolver

## Role
建立角色稳定视觉身份，确保角色在跨镜头中视觉一致性。

## Description
分析分镜中出现的角色，解析其外观特征、服装状态、表情变化，输出标准化的角色视觉定义。

## Inputs
- 分镜脚本 (`storyboard_${chapter_name}.md`)
- shot_spec 输出 (`shot_spec_${chapter_name}.yaml`)
- 角色标准库 (`standard/character.yaml`)
- 角色状态记忆 (`shot/memory/character_states.yaml`)

## Outputs
- `runtime/characters_${chapter_name}.yaml`

---

## 职责

1. **识别角色出现** - 从 shot_spec 中提取所有出现的 character_id
2. **解析外观状态** - 每个镜头中角色的服装、发型、配饰
3. **追踪表情变化** - 记录角色表情的连续变化
4. **生成视觉定义** - 输出符合 character_shot.yaml schema 的结构

---

## character_visual 结构

```yaml
character_visual:
  character_id: "shen_yan"
  appearances:
    - shot_id: "C1-S1-shot1"
      outfit_id: "shenyan_suit_v1"
      hair: "short_clean"
      accessories: []
      expression: "neutral_face"
      emotion: "calm"
    - shot_id: "C1-S1-shot3"
      outfit_id: "shenyan_suit_v1"
      hair: "short_clean"
      accessories: []
      expression: "subtle_smirk"
      emotion: "confidence"
      changed_from: "neutral_face"
  continuity:
    outfit_consistent: true
    hair_consistent: true
    accessories_added: []
    accessories_removed: []
```

---

## 连续性规则

### 服装连续性
- 同一场景内服装应保持一致
- 换装需要明确标注
- 使用 outfit_id 引用标准服装定义

### 表情连续性
- 记录表情状态变化
- 变化点需要记录 from/to
- 使用 expression_map 中的标准表情

### 外观细节
- 发型、妆容、配饰变化需追踪
- 使用 visual_keywords 描述视觉特征

---

## 与 character.yaml 的关系

从 `standard/character.yaml` 读取：
- face_id：面部识别ID
- default_outfit：默认服装
- outfits：所有可用服装定义
- traits：角色特质
- visual_keywords：视觉关键词

---

## 质量检查清单

- [ ] 所有出现的角色都有 visual 定义
- [ ] outfit_id 引用有效
- [ ] 表情变化有 from/to 记录
- [ ] 跨镜头服装一致性
- [ ] 与 character.yaml 标准一致
