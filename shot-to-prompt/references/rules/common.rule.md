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

## 9. General Constraints

* DO NOT introduce new fields outside schema
* DO NOT skip required PromptBlocks
* ALL PromptBlocks MUST exist

---

## 10. Key Principle

Semantic is the source of truth.
Text and tokens are derived artifacts.
