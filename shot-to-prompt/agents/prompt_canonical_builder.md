# Prompt Canonical Builder

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `canonical` | Permission: semantic ✅ FULL, text ⚠️ placeholder only

---

## 1. Purpose

Convert IR (prompt_ir.yaml) into structured semantic Prompt.

This agent is the **only stage that generates semantic**.

---

## 2. Input

IR (prompt_ir.yaml)

Contains:

* subject
* intent
* visual_intent
* environment
* camera (optional)
* style (optional)

---

## 3. Output

Prompt (common.schema.yaml)

Each PromptBlock MUST contain:

* semantic (source of truth)
* text (empty or minimal placeholder)

---

## 4. Core Principle

IR = full context
Semantic = minimal executable meaning

Canonical = semantic compiler

---

## 5. Processing Pipeline

### Step 1: Extract Core Elements

* actor ← IR.subject.primary
* target ← IR.intent.target (if exists)

---

### Step 2: Derive Action Type

Action.type MUST be derived from intent.type

---

#### Intent → Action Mapping

##### A. Intimidation / Pressure

* intimidation → approach
* dominance → step_forward
* suppression → lock_gaze
* threat → slow_walk

---

##### B. Confrontation / Conflict

* confrontation → face
* challenge → step_forward
* aggression → aggressive_step
* attack_intent → lunge_forward

---

##### C. Escape / Avoidance

* escape → run
* avoidance → step_back
* fear_response → trembling
* retreat → slow_walk (reverse)

---

##### D. Emotional Expression

* sadness → still
* grief → slight_lean_forward
* anger → clenched_fists
* suppressed_anger → frozen
* shock → sudden_head_turn

---

##### E. Observation / Awareness

* realization → slow_look_up
* suspicion → glance_side
* attention_shift → gaze_shift
* focus → lock_gaze

---

##### F. Neutral / Transition

* idle → still
* pause → pause
* waiting → subtle

---

### Step 3: Derive Motion Dynamics

From visual_intent + emotion:

* oppressive → slow + high intensity
* tense → sharp + medium/high
* calm → slow + low
* chaotic → fast + high

---

### Step 4: Build Subject Semantic

```yaml
subject:
  actor: <character_id>
  target: <optional>

  emotion: <from emotion_map>
  expression: <optional>
```

---

### Step 5: Build Action Semantic

```yaml
action:
  type: <mapped action>
  speed: slow | normal | fast
  intensity: low | medium | high
```

---

### Step 6: Build Environment Semantic

```yaml
environment:
  location: <environment.location>  
  props: <environment.props>
```

---

### Step 7: Build Camera Semantic

Priority:

1. IR.camera (explicit)
2. visual_intent.shot_type
3. default mapping

```yaml
camera:
  shot_type: <enum>
  angle: <enum>
  movement: <enum>
  composition: <enum>

  lens: <enum>
  aperture: <enum>
  focus: <enum>
```

---

### Step 8: Build Style Semantic

```yaml
style:
  lighting: <enum>
  style: <enum>
  atmosphere: <enum>
  atmosphere_intensity: low | medium | high
```

---

## 6. Output Example

```yaml
prompt:
  subject:
    semantic:
      actor: antagonist
      target: protagonist
      emotion: dominance

    text: ""
    tokens: []    

  action:
    semantic:
      type: approach
      speed: slow
      intensity: high

    text: ""
    tokens: []    

  environment:
    semantic:
      location: alley      

    text: ""
    tokens: []    

  camera:
    semantic:      
      shot_type: establishing
      composition: symmetrical
      angle: bird_eye
      movement: crane

      lens: 24mm
      aperture: f2.8
      focus: deep

    text: ""
    tokens: []    

  style:
    semantic:
      lighting: low_key
      style: cinematic
      atmosphere: dark
      atmosphere_intensity: high

    text: ""
    tokens: []    

  quality:
    semantic: {}
    text: ""
    tokens: []    

  negative:
    semantic: {}
    text: ""
    tokens: []      

  final:
    text: ""
```

---

## 7. Constraints

* semantic MUST use enum values only
* NO free-text allowed in semantic
* action.type MUST be singular
* semantic MUST be complete without IR

---

## 8. Forbidden

* DO NOT generate final prompt text
* DO NOT modify IR
* DO NOT introduce new semantic fields
* DO NOT create intermediate IR (builder_ir)

---

## 9. Semantic Ownership

* Canonical: FULL control
* Enhancer: LIMITED refinement (style/intensity only)
* Consistency: READ-ONLY
* Temporal: READ-ONLY
* Adapter: TEXT generation only

---

## 10. Key Rule

Semantic is the only truth.
Text is a compiled artifact.
