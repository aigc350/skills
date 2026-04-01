# Semantic Field Specification v1.0

## 1. Purpose

The `semantic` field represents the structured meaning of a prompt block.
It is the single source of truth for all downstream prompt generation.

---

## 2. Ownership Rules

* Canonical: FULL control (generate semantic)
* Enhancer: LIMITED control (refine style/intensity only)
* Consistency: READ-ONLY
* Temporal: READ-ONLY
* Adapter: READ-ONLY (generate text only)

---

## 3. Mutation Rules

Allowed modifications:

* style-related attributes (intensity, pacing)
* descriptive refinements

Forbidden modifications:

* action.type
* subject.actor / target
* intent-related fields

---

## 4. Lifecycle

Canonical → Enhancer → (lock) → Consistency → Temporal → Adapter

---

## 5. Locking Mechanism

* `semantic_lock = false` (after Canonical)
* `semantic_lock = true` (after Enhancer)

Downstream stages MUST NOT modify locked semantic.

---

## 6. Text Generation Rule

* `text` MUST be derived from `semantic`
* Manual authoring of `text` is NOT allowed

---

## 7. Token Generation Rule

* tokens MUST be extracted from semantic
* tokens MUST be stable across equivalent semantics
