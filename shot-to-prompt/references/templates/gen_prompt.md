# Gen Prompt Output Template

## 镜头级 Prompt 输出

```yaml
# Gen Prompt - {chapter_id}
# Platform: {platform}
# Generated: {timestamp}

chapter_id: "{chapter_id}"
platform: "{platform}"

metadata:
  total_prompts: {total_shots}
  total_duration: "{min_duration}-{max_duration} 秒"
  characters:
    - {character_list}
  locations:
    - {location_list}

shot_prompts:
{shot_prompts_block}

chapter_prompt:
  full_prompt: |
    {full_prompt_text}

  scene_setup: |
    {scene_setup_text}

  character_introductions: |
    {character_intro_text}

  continuity_notes: |
    {continuity_notes_text}

---

## 视频任务列表

video_tasks:
{video_tasks_block}
```

## 示例输出

```yaml
chapter_id: "C01"
platform: "sora"

metadata:
  total_prompts: 12
  total_duration: "45-60 秒"
  characters:
    - zhang_san
    - li_si
  locations:
    - warehouse
    - street

shot_prompts:
  - shot_id: "C01-S1-shot01"
    prompt: |
      Cinematic scene: A dimly lit abandoned warehouse with rusty metal structures.
      A man in his 30s with short messy hair, wearing a worn leather jacket,
      stands in the center. Cold, calculating expression. Single dramatic
      spotlight from above creates deep shadows. Low angle camera slowly
      pushes in towards the character.
    negative_prompt: "anime, cartoon, low quality, distorted face..."
    duration: "3-5 秒"
    camera: "Wide shot, low angle, dolly in"
    style: "Film noir, cinematic"

chapter_prompt:
  full_prompt: |
    Scene opens in a dark abandoned warehouse. Zhang San enters alone,
    his footsteps echoing in the vast space. He pauses, surveying the area
    with cold, calculating eyes. A flash of light reveals his determined
    expression before darkness engulfs him again.
  scene_setup: |
    Abandoned warehouse with rusted metal beams, broken windows letting in
    slivers of moonlight, debris scattered on concrete floor.
  character_introductions: |
    Zhang San: Male, 30s, short messy hair, worn leather jacket.
    Cold, authoritative presence.
  continuity_notes: |
    - Zhang San's outfit consistent throughout scene
    - Lighting transitions from dark to spotlight moments

video_tasks:
  - task_id: "C01-S1-shot01"
    shot_id: "C01-S1-shot01"
    prompt_length: 312
    estimated_time: 5
    status: "pending"
```
