# Common Rules Specification v1.0

## 1. Purpose

Define unified rules for:

* field ownership
* write permissions
* generation stages

This ensures consistency across all pipeline stages.

---

## 2. Pipeline Stages

| Stage       | Description                    |
| ----------- | ------------------------------ |
| canonical   | generate semantic              |
| enhancer    | refine semantic (style only)   |
| consistency | enforce cross-shot consistency |
| temporal    | enforce time continuity        |
| adapter     | generate final prompt text     |

---

## 3. Meta Rules

```yaml
meta:
  stage: canonical | enhancer | consistency | temporal | adapter
```

### Rules

* `meta.stage` determines write permissions
* NO per-field lock (e.g. semantic_lock) is allowed

---

## 4. PromptBlock Structure

```yaml
PromptBlock:
  semantic: object
  text: string
  tokens: string[]
```

---

## 5. Field Ownership Rules

---

### 5.1 semantic

| Stage       | Permission  |
| ----------- | ----------- |
| canonical   | ✅ FULL      |
| enhancer    | ⚠ LIMITED   |
| consistency | ❌ READ ONLY |
| temporal    | ❌ READ ONLY |
| adapter     | ❌ READ ONLY |

---

### 5.2 PromptBlock.text

| Stage       | Permission              |
| ----------- | ----------------------- |
| canonical   | ⚠ placeholder only ("") |
| enhancer    | ❌                       |
| consistency | ❌                       |
| temporal    | ❌                       |
| adapter     | ✅ FULL                  |

---

### Rules

* text MUST be generated from semantic
* text MUST NOT be manually authored before adapter

---

### 5.3 PromptBlock.tokens

| Stage       | Permission |
| ----------- | ---------- |
| canonical   | ❌          |
| enhancer    | ❌          |
| consistency | ❌          |
| temporal    | ❌          |
| adapter     | ✅ FULL     |

---

### Rules

* tokens MUST be derived from semantic
* tokens MUST be generated together with text

---

### 5.4 Prompt.quality

| Stage     | Permission               |
| --------- | ------------------------ |
| canonical | ⚠ create empty structure |
| enhancer  | ✅ FULL                   |
| adapter   | ⚠ may refine             |

---

### Rules

* quality defines output quality modifiers
* examples: ultra detailed, 8k, high quality

---

### 5.5 Prompt.negative

| Stage     | Permission               |
| --------- | ------------------------ |
| canonical | ⚠ create empty structure |
| enhancer  | ✅ FULL                   |
| adapter   | ⚠ may refine             |

---

### Rules

* negative defines undesired elements
* examples: blur, distortion, low quality

---

### 5.6 Prompt.final

| Stage       | Permission               |
| ----------- | ------------------------ |
| canonical   | ⚠ create empty structure |
| enhancer    | ❌                        |
| consistency | ❌                        |
| temporal    | ❌                        |
| adapter     | ✅ FULL                   |

---

### Rules

* final is the final composed prompt
* MUST be generated in adapter stage only

---

## 6. Semantic Rules

* semantic MUST use enum keys only
* NO free-text allowed
* semantic MUST be complete enough to generate prompt

---

## 7. Intent Rules

* intent is NOT part of semantic
* intent is used ONLY during canonical stage
* intent MUST NOT appear in output

---

## 8. Environment vs Style

* environment → objective world state
* style → cinematic expression

```yaml
environment.semantic:
  location: ...
  env_atmosphere: ...

style.semantic:
  atmosphere: ...
```

---

## 9. Props vs Objects

---

### 9.1 定义

| 类型 | 一致性 | 观众注意 | asset_id |
|------|--------|----------|----------|
| **props** | 弱一致（背景） | ❌ 不会 | ❌ 不生成 |
| **objects** | 强一致（关键物品） | ✅ 会 | ✅ 需要生成 |

---

### 9.2 判断标准

```text
IF 观众会特别注意该物品:
    → object（需要 asset_id）
ELSE:
    → prop（不需要 asset_id）
```

---

### 9.3 示例

```yaml
# props - 背景道具
props:
  - chandelier      # 吊灯：背景装饰
  - round_tables    # 圆桌：场景元素
  - background_crowd # 人群：背景

# objects - 关键物品
objects:
  - object_id: ring_1
    type: ring
    object_state: intact
    role: key_item        # 戒指：关键道具

  - object_id: glass_1
    type: champagne_glass
    object_state: full
    role: prop            # 酒杯：但状态会变化
```

---

## 10. State Rules（状态规则）

---

### 10.1 State 分类

| 类型 | 说明 | 定义位置 | 推导位置 |
|------|------|----------|----------|
| **subject_state** | 人物状态 | IR 层 | Temporal 层 |
| **object_state** | 物品状态 | IR 层 | Temporal 层 |

---

### 10.2 State 是剧情事实

```yaml
# IR 层定义（来自 shot_spec 或 characters.yaml）
subject_state: clean        # 人物状态
object_state: full          # 物品状态
```

---

### 10.3 状态变化由 Temporal 推导

```yaml
# Temporal 层推导
previous.subject_state: clean
current.subject_state: dirty
    → temporal_tag: "subject_degradation"
```

---

### 10.4 枚举定义

所有状态枚举定义在 `mappings/enums.yaml`：

```yaml
subject_state: [clean, slightly_dirty, dirty, wet, damaged, bloody]
object_state: [full, half_full, empty, broken, spilled, intact, cracked, lit, extinguished]
```

---

## 11. Role Rules（角色规则）

---

### 11.1 Role 是表达策略

**role 只影响 prompt 表达，不影响 semantic**。

---

### 11.2 Role 枚举

```yaml
role: [prop, key_item, weapon, artifact]
```

| role | detail_level | 描述策略 |
|------|--------------|----------|
| prop | low | 简单提及 |
| key_item | high | 详细强调 |
| weapon | high | 武器描述 |
| artifact | high | 神秘氛围 |

---

## 12. General Constraints

* DO NOT introduce new fields outside schema
* DO NOT skip required PromptBlocks
* ALL PromptBlocks MUST exist

---

## 10. Key Principle

Semantic is the source of truth.
Text and tokens are derived artifacts.
