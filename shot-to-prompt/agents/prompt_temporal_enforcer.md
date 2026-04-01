# Temporal Enforcer v1.1 (Production-Ready)

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

## Step 5️⃣ State Evolution

---

条件：

```text
variant_id 改变
```

---

注入：

```text
state transition, outfit change
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
