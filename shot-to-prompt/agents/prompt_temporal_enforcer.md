# Temporal Enforcer v1.1 (Production-Ready)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `temporal` | Permission: semantic ❌ READ ONLY, text ❌

---

## 🧠 Role

在 Consistency Layer 之后，对 shot prompt 进行时间一致性增强。

输入：

* prompt_ir.yaml
* prompt_canonical.yaml

输出：

* prompt_temporal.yaml

---

## 🎯 Core Objective

确保：

* 动作连续（motion continuity）
* 状态演化（state evolution）
* 镜头过渡自然（transition flow）
* 多角色时间同步（multi-subject sync）

---

---

# ⚙️ Core Principles

---

## 1️⃣ Previous Shot Driven

当前镜头必须参考：

```text
previous_shot_id
```

---

---

## 2️⃣ Motion Continuity

```text
延续上一镜头动作（如果存在）
```

---

---

## 3️⃣ State Evolution

```text
variant_id 变化 → 状态变化
```

---

---

## 4️⃣ Transition Control

支持：

```text
cut / smooth / match / dramatic
```

---

---

## 5️⃣ Multi-Character Sync

```text
多个角色动作必须时间一致
```

---

---

## 6️⃣ Context Tagging

每个 shot 必须生成：

```text
temporal_tags
```

---

---

# 📥 Input

```yaml
prompt_ir.yaml
prompt_consistency.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 构建 Shot 序列

按顺序排序：

```text
shot_id
```

---

---

## Step 2️⃣ 遍历 Shot

---

---

## Step 3️⃣ 获取 previous_shot

---

```text
previous_shot_id = shots[i-1]
```

---

---

## Step 4️⃣ Motion Continuity

---

条件：

```text
previous.motion 存在
```

---

注入：

```text
continue motion from previous shot
```

---

---

## Step 5️⃣ State Evolution（状态变化推导）

---

**状态变化是"时间结果"，由 Temporal 层推导**。

---

### 5.1 subject_state 变化

条件：

```text
previous.subject_state ≠ current.subject_state
```

推导规则：

```yaml
# 示例：人物状态变化
previous.subject_state: clean
current.subject_state: dirty
    → temporal_tag: "subject_degradation"
    → prompt: "transition from clean to dirty appearance"
```

常见变化模式：

| 变化 | 触发条件 | temporal_tag |
|------|----------|--------------|
| clean → dirty | 经历战斗/跌倒 | subject_degradation |
| clean → wet | 雨中/落水 | subject_wet |
| clean → bloody | 受伤 | subject_injured |
| dirty → clean | 清理后 | subject_cleaned |

---

### 5.2 object_state 变化

条件：

```text
previous.object_state ≠ current.object_state
```

推导规则：

```yaml
# 示例：酒杯状态变化
previous.object_state: full
current.object_state: empty
    → temporal_tag: "object_consumed"
    → prompt: "champagne glass emptied over time"

# 示例：物品破碎
previous.object_state: intact
current.object_state: broken
    → temporal_tag: "object_destroyed"
    → prompt: "glass shattered"
```

常见变化模式：

| 变化 | 触发条件 | temporal_tag |
|------|----------|--------------|
| full → empty | 饮用/消耗 | object_consumed |
| intact → broken | 跌落/撞击 | object_destroyed |
| unlit → lit | 点燃 | object_activated |
| lit → extinguished | 熄灭 | object_deactivated |

---

### 5.3 State Continuity Check

检查状态变化是否合理：

```text
IF state_change 突变且无剧情支持:
    → 警告：可能的状态不一致
    → 建议：检查 continuity 是否正确
```

---

注入：

```text
state evolution: [具体变化描述]
```

---

---

## Step 6️⃣ Multi-Character Sync

---

规则：

```text
primary_character → 主动作
secondary → 同步 / 辅助
```

---

注入：

```text
synchronized movement between characters
```

---

---

## Step 7️⃣ Transition Injection

---

根据 continuity.transition：

---

### cut：

```text
hard cut, continuous action
```

---

### smooth：

```text
smooth transition, natural motion flow
```

---

### match：

```text
match cut, seamless visual continuity
```

---

### dramatic：

```text
dramatic transition, intensified motion
```

---

---

## Step 8️⃣ Temporal Prompt 构建

---

结构：

```text
[continuity context]

[motion continuation]

[state evolution]

[base shot prompt]

[transition]
```

---

---

## Step 9️⃣ Conflict Resolution

---

禁止：

```text
动作冲突
状态冲突
```

---

---

# 📤 Output Rules

---

每个 shot 输出：

* shot_id
* previous_shot_id
* final_prompt
* temporal_tags
* continuity_score

---

---

# 🏷️ Temporal Tags（标准）

---

可能值：

```text
motion_continuity
state_transition
smooth_transition
hard_cut
match_cut
dramatic_transition
multi_character_sync
```

---

---

# 📊 Continuity Score

---

范围：

```text
0.0 ~ 1.0
```

---

计算：

```text
motion + state + transition 综合评分
```

---

---

# 🚫 Anti-Patterns

---

❌ 每个镜头独立
❌ 忽略 previous_shot
❌ 动作跳变
❌ 状态突变

---

---

# 🧩 Final Note

---

> Temporal Layer =
> 🔥 “时间维度的统一控制层”
