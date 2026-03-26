# Scene Output Template

## Scene {N}: {Scene Name}

```yaml
scene:
  id: "S{N}"
  chapter_id: "{chapter_id}"
  location:
    name: "{location_name}"
    type: "INT | EXT"
  time: "{time_of_day}"
  duration: "{estimated_duration}"

characters:
  - name: "{character_name}"
    role: "protagonist | antagonist | supporting"
    emotion: "{emotional_state}"
    position: "{position_in_scene}"

coverage:
  type: "Full Coverage | Minimal | Intensive | Sequential"
  shot_count: {number}
  rationale: "{why_this_coverage}"

content_summary: |
  {What happens in this scene}

visual_notes: |
  {Visual指导 from director}

continuity:
  character_positions: "{positions}"
  key_props: "{props_and_states}"
  warnings: "{if_any}"
```

---

## Scene Metadata

| Field | Value |
|-------|-------|
| Scene ID | S{N} |
| Chapter | {chapter_id} |
| Location | {location_name} |
| Time | {time_of_day} |
| Duration | {estimated_duration} |
| Characters | {character_count} |
| Shot Count | {number} |

---

## Coverage Plan

**Type**: {coverage_type}

**Rationale**: {why_this_coverage}

**Shot Sequence**:
1. {shot_1_type} - {purpose}
2. {shot_2_type} - {purpose}
3. ...

<!-- Repeat for each scene -->
