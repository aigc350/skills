# Continuity Engine

## Type
Engine

## Role
校验 shot_spec、characters、scenes 的跨镜头一致性，输出一致性评分和问题报告。

## Description
从三个维度校验数据一致性：角色连续性（outfit/expression）、场景连续性（lighting/atmosphere）、技术连续性（camera/continuity chain），输出带评分的 consistency.yaml。

## Inputs
- shot_spec (`shot_spec_${chapter_name}.yaml`)
- characters (`characters_${chapter_name}.yaml`)
- scenes (`scenes_${chapter_name}.yaml`)

## Outputs
- `consistency_${chapter_name}.yaml`

## Task

### Step 1: 角色一致性检查（权重 25%）

对 characters.yaml 中的每个角色：

1. **outfit 一致性**：
   - 遍历该角色的所有 appearances
   - 同一 scene 内 outfit_id 应保持一致
   - 如果 scene 内 outfit 变化无合理理由 → 扣分
   - 验证 `continuity.outfit_consistent` 与实际数据一致

2. **face_id 一致性**：
   - 从 shot_spec 中提取该角色所有 shot 的 `subject.face_id`
   - 所有 face_id 应相同
   - 如果不一致 → 标记为 error

3. **expression 变化合理性**：
   - 检查 `expression_changes` 中的 from/to 是否与 shot_spec 中的 `subject.expression[0]` 一致
   - expression 变化应在 drama 需要的地方发生（不是随机跳变）

评分规则：
- 全部通过 → 1.0
- outfit 在同一 scene 内变化但无理由 → -0.1 每次
- face_id 不一致 → -0.3
- expression 变化记录不准确 → -0.05 每次

### Step 2: 场景一致性检查（权重 25%）

对 scenes.yaml 中的每个 location：

1. **location_id 匹配**：
   - shot_spec 中所有 `environment.location_id` 必须在 scenes.yaml 中有对应条目
   - 反之，scenes.yaml 中的 location_id 必须在 shot_spec 中被引用

2. **lighting 变化合理性**：
   - atmosphere 变化应有叙事依据（如从 luxury → tense 是冲突升级）
   - `shifts` 记录应与 shot_spec 中的 `visual_intent.atmosphere` 一致

3. **props 连续性**：
   - 同一 scene 内 props 的增减应合理
   - 角色"持物"的 prop 应在 environment.props 中出现

评分规则：
- 全部通过 → 1.0
- location_id 不匹配 → -0.2 每个
- atmosphere shift 不合理 → -0.1 每次
- props 不连续 → -0.05 每次

### Step 3: 技术连续性检查（权重 25%）

1. **continuity chain 完整性**：
   - 每个 shot 的 `continuity.previous_shot_id` 必须指向有效 shot
   - 第一个 shot 的 previous_shot_id 应为 null
   - 链条不应断裂或循环

2. **camera 一致性**：
   - 同一 scene 内 camera.lens 不应无理由跳变（如 85mm → 24mm → 85mm）
   - camera_movement 在同一 scene 内的风格应统一

3. **shot_id 连续性**：
   - shot_id 应全局递增，无断裂
   - 格式正确：`C{n}-S{n}-shot{n}`

评分规则：
- 全部通过 → 1.0
- continuity chain 断裂 → -0.2
- camera 无理由跳变 → -0.1 每次
- shot_id 不连续 → -0.05 每次

### Step 4: 格式合规检查（权重 25%）

1. **标准库合规**：
   - `subject.expression[]` 所有值存在于 expression_map.yaml
   - `subject.motion[]` 所有值存在于 motion_map.yaml
   - `visual_intent` 所有字段值存在于 visual_intent.yaml
   - `intent.narrative_function` 存在于 visual_intent.yaml

2. **Schema 合规**：
   - 所有 required 字段非空
   - dialogue.speaker 是有效 character_id
   - dialogue.type 是有效枚举

3. **cross-reference 完整性**：
   - shot_spec 中引用的 character_id 在 characters.yaml 中存在
   - shot_spec 中引用的 location_id 在 scenes.yaml 中存在

评分规则：
- 全部通过 → 1.0
- 标准库违规 → -0.1 每个字段
- Schema 违规 → -0.15 每个
- cross-reference 缺失 → -0.1 每个

### Step 5: 计算总分

```yaml
total_score: = (角色 * 0.25 + 场景 * 0.25 + 技术 * 0.25 + 格式 * 0.25)
passed: = total_score >= 0.85
```

### Step 6: 输出格式

```yaml
chapter_id: "1"
status: "passed"
score: 0.92
passed: true

dimensions:
  character_consistency:
    score: 0.95
    issues: []
  scene_consistency:
    score: 0.90
    issues:
      - severity: "warning"
        location: "banquet_hall_center"
        detail: "atmosphere shifted 3 times within scene"
  technical_continuity:
    score: 0.88
    issues:
      - severity: "info"
        shot_id: "C1-S3-shot18"
        detail: "lens changed from 85mm to 50mm within same scene"
  format_compliance:
    score: 0.95
    issues: []

summary: "4 dimensions checked, 2 minor issues found"
total_shots_checked: 30
total_characters_checked: 5
total_locations_checked: 3
```

---

## Issue 严重级别

| 级别 | 说明 | 对分数影响 |
|------|------|-----------|
| error | 必须修复（如 face_id 不一致） | -0.15 ~ -0.30 |
| warning | 建议修复（如 atmosphere 频繁变化） | -0.05 ~ -0.10 |
| info | 仅提示（如 lens 风格变化） | -0.02 ~ -0.05 |
