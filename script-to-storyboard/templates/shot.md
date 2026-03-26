# Shot Output Template

## Shot {N}

```yaml
shot:
  id: {shot_number}
  scene_id: "S{scene_number}"
  type: "{shot_type}"           # ELS, LS, WS, MLS, MS, MCU, CU, ECU, 2S, OTS
  angle: "{camera_angle}"       # eye_level, high, low, tilted, overhead, dutch
  movement: "{movement_type}"    # static, pan, tilt, dolly_in, dolly_out, track, crane, zoom, handheld
  duration: "{duration}"        # e.g., "3s", "5s"
```

### Visual Description

{Describe what is shown in this shot - who/what is in frame, their position, action, expression, background elements, lighting, atmosphere}

### Dialogue / Audio

**Dialogue**:
{Dialogue if any, with character name}

**SFX**:
{Sound effects if any}

**Music/BGM**:
{Music direction if any}

### Technical Notes

| Element | Value |
|---------|-------|
| Type | {shot_type} |
| Angle | {camera_angle} |
| Movement | {movement_type} |
| Duration | {duration} |
| Equipment | {if any special equipment needed} |

### Purpose / Continuity

**Purpose**: {Why this shot is needed}

**Continuity**: {Connection to previous/next shots}

---

## Shot {N+1}

```yaml
shot:
  id: {shot_number}
  ...
```

<!-- Repeat for each shot in the scene -->
