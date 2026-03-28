# Continuity Engine

## Type
Engine

## Role
控制跨镜头一致性，检测并修复视觉漂移。

## Description
检查 shot_spec、characters 和 scenes 的跨镜头一致性，确保角色外观、场景光照、服装道具等在合理范围内保持一致。

## Inputs
- shot_spec (`shot_spec_${chapter_name}.yaml`)
- characters (`characters_${chapter_name}.yaml`)
- scenes (`scenes_${chapter_name}.yaml`)
- 一致性标准 (`schemas/consistency.yaml`)

## Outputs
- `runtime/consistency_${chapter_name}.yaml`
- 更新的 shot_spec（带 continuity 标注）

---

## 一致性检查维度

### 1. 角色一致性 (25%)
- character_id 在跨镜头中一致
- outfit_id 不应有冲突
- 发型、配饰等细节一致
- 表情变化有连续性记录

### 2. 场景一致性 (25%)
- location_id 在相关镜头中一致
- lighting 类型一致
- 道具状态合理
- 氛围关键词合理

### 3. 摄影一致性 (20%)
- shot_size 变化平滑
- camera angle 过渡合理
- movement 类型一致

### 4. 叙事连续性 (15%)
- 时间线合理
- 空间位置连贯
- 情绪弧线平滑

### 5. 格式合规 (15%)
- 所有字段符合 schema
- 枚举值正确
- 必填字段完整

---

## continuity 标注

```yaml
continuity:
  status: "consistent"  # consistent/warning/error
  issues: []
  character_issues:
    - shot_id: "C1-S2-shot2"
      character_id: "shen_yan"
      issue: "outfit_changed"
      detail: "从 shenyan_suit_v1 变为未知 outfit"
      severity: "warning"
  scene_issues:
    - shot_id: "C1-S1-shot3"
      issue: "lighting_inconsistent"
      detail: "从 warm_chandelier 变为 cold_warehouse"
      severity: "error"
  camera_issues: []
```

---

## 问题级别

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| warning | 潜在问题 | 记录但不阻止 |
| error | 明显错误 | 标记并修复 |

---

## 修复策略

### 服装不一致
- 如果跨镜头服装变化未标注 → 警告
- 如果变化不合理 → 错误，回滚到前一服装状态

### 光照不一致
- 如果场景内光照剧变 → 错误，使用前一镜头光照
- 如果是场景转换 → 正常，记录变化

### 表情跳跃
- 如果表情变化过大且无过渡 → 警告
- 检查 expression_map 中间状态

---

## 输出格式

参考 [schemas/consistency.yaml](../schemas/consistency.yaml)

---

## 质量检查清单

- [ ] 所有镜头都有 continuity 标注
- [ ] character_id 跨镜头一致
- [ ] outfit_id 变化有记录
- [ ] lighting 变化有记录
- [ ] 无严重的 error 级别问题
