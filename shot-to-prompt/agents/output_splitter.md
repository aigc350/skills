# Output Splitter Agent v1.0（多模态输出拆分）

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `splitter` | Pipeline 最终阶段
>
> ⭐ v0.4 核心模块：将 resolved_shots + final_prompts 拆分为四种可执行输出

---

## 🧠 Role

将以下输入：

* resolved_shots.yaml（平台无关真相层）
* final_prompts.yaml（平台请求层）
* asset_registry.yaml（全局资产库）

拆分为四种输出：

* **video_prompts.yaml**（视频生成请求）
* **image_prompts.yaml**（参考图生成请求）
* **voice_prompts.yaml**（配音生成请求）
* **asset_manifest.yaml**（资产状态汇总 + 生成任务清单）

同时更新 asset_registry.yaml 的使用追踪。

---

## 🎯 Core Objective

1. **拆分**：将统一数据拆分为不同生成器可用的格式
2. **追踪**：更新 asset_registry 的 used_in_chapters / used_in_shots
3. **调度**：生成任务依赖关系清单
4. **剪辑**：输出剪辑元数据（供 auto-edit skill 使用）

---

## ⚙️ Core Principles

---

### 1️⃣ Single Source of Truth

所有输出的共同上游是 resolved_shots.yaml，不存在其他真相源。

### 2️⃣ Non-Destructive

拆分不修改原始数据，只做格式转换和分类。

### 3️⃣ Registry Update

拆分完成后必须更新 asset_registry.yaml 的使用追踪字段。

---

---

# 📥 Input

```yaml
input:
  - {runtime_dir}/resolved_shots.yaml   # 平台无关真相层
  - {runtime_dir}/final_prompts.yaml    # 平台请求层
  - {memory_dir}/asset_registry.yaml    # 全局资产库
```

---

# 📤 Output

```yaml
output:
  - {output_dir}/video_prompts.yaml     # 视频生成请求
  - {output_dir}/image_prompts.yaml     # 参考图生成请求
  - {output_dir}/voice_prompts.yaml     # 配音生成请求
  - {output_dir}/asset_manifest.yaml    # 资产状态汇总
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 读取所有输入

```text
resolved = 读取 resolved_shots.yaml
final = 读取 final_prompts.yaml
registry = 读取 asset_registry.yaml
```

---

## Step 2️⃣ 构建 video_prompts.yaml

### 2.1 生成策略配置

```yaml
generation_strategy:
  mode: "shot_per_video"           # 默认策略：一个 shot 一个视频
  batch_size: 5                    # 批量提交数量
  auto_merge: false                # 是否自动合并同场景镜头

  # 自动剪辑配置（供 auto-edit skill 使用）
  output_for_edit:
    enabled: true                  # 输出剪辑元数据
    transition_hints: true         # 包含转场提示
```

### 2.2 遍历每个 shot

```text
FOR each shot in final_prompts.shots:

  video_entry = {
    shot_id: shot.shot_id
    final_prompt: shot.final_prompt
    negative_prompt: shot.negative_prompt

    # 剪辑元数据（从 resolved_shots 提取）
    edit_metadata:
      location_id: resolved[shot_id].continuity.location_bindings[0].location_id
                  # ⚠️ 使用 asset 层的 location_id（如 "banquet_hall"），不是 scene_id
      sequence: 从 shot_id 提取数字部分（如 "C1-S3-shot20" → 20）
      duration: shot.request.duration
      transition_in: infer_transition(shot, resolved[shot_id])
      transition_out: infer_transition(shot, resolved[shot_id], look_ahead=true)

    # 平台请求参数（直接传递，包含 seed/aspect_ratio）
    request: shot.request
  }
```

### 2.3 转场推断规则

```text
# ⭐ 基于 temporal_tags 和 dramatic context 推断，不依赖精确字符串匹配
infer_transition(current_shot, resolved, look_ahead=false):

  tags = resolved.continuity.temporal_tags
  hook = resolved.dramatic_focus.hook_type

  # 规则 1：场景切换（location 变化）
  IF location_changed_from_previous_shot:
    → "smooth"

  # 规则 2：建立/氛围镜头
  ELIF "establishing" IN tags OR "setting" IN tags:
    → "smooth"

  # 规则 3：高潮/冲突/反转
  ELIF "climax" IN tags OR hook == "climax":
    → "dramatic"
  ELIF "conflict" IN tags OR hook == "confrontation":
    → "dramatic"
  ELIF "reveal" IN tags OR hook == "reveal":
    → "dramatic"

  # 规则 4：转场/过渡镜头
  ELIF "transition" IN tags OR "power_exit" IN tags:
    → "smooth"

  # 规则 5：反应/爆发
  ELIF "reaction" IN tags AND "chaos" IN tags:
    → "cut"
  ELIF "reaction" IN tags:
    → "match"

  # 规则 6：紧张对峙（枪战/凝视）
  ELIF "locked_gaze" IN tags OR "aggression" IN tags:
    → "dramatic"

  # 默认
  DEFAULT:
    → "cut"
```

---

## Step 3️⃣ 构建 image_prompts.yaml

### 3.1 收集待生成参考图

```text
pending_images = []
completed_images = []
seen_asset_ids = SET()          # ⭐ 去重：避免同一资产被多次处理

FOR each shot in resolved.shots:
  # ⭐ 从 continuity.character_bindings 提取（不是 referenced_assets）
  FOR each char_binding in shot.continuity.character_bindings:
    asset_id = char_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        IF registry_entry.generation_status.image == "pending":
          → 添加到 pending_images，priority = "critical"，type = "character"，final_prompt = registry_entry.final_prompt，negative_prompt = registry_entry.negative_prompt
        ELIF registry_entry.generation_status.image == "approved":
          → 添加到 completed_images

  # ⭐ 从 continuity.location_bindings 提取
  FOR each loc_binding in shot.continuity.location_bindings:
    asset_id = loc_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        IF registry_entry.generation_status.image == "pending":
          → 添加到 pending_images，priority = "high"，type = "location"，final_prompt = registry_entry.final_prompt，negative_prompt = registry_entry.negative_prompt
        ELIF registry_entry.generation_status.image == "approved":
          → 添加到 completed_images

  # ⭐ 从 continuity.object_bindings 提取
  FOR each obj_binding in shot.continuity.object_bindings:
    asset_id = obj_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        IF registry_entry.generation_status.image == "pending":
          → 添加到 pending_images，priority = "medium"，type = "object"，final_prompt = registry_entry.final_prompt，negative_prompt = registry_entry.negative_prompt
        ELIF registry_entry.generation_status.image == "approved":
          → 添加到 completed_images
```

**关键修复**：`referenced_assets` 在 resolved_shots 中为空，资产绑定实际在 `continuity.character_bindings`、`continuity.location_bindings`、`continuity.object_bindings` 中。必须从这些字段提取 asset_id。

### 3.2 构建图片请求

```text
FOR each pending_asset in pending_images:

  # 类型映射（修正不一致问题）
  IF pending_asset.type == "location":
    → mapped_type = "scene"
  ELIF pending_asset.type == "crowd":
    → mapped_type = "scene"           # crowd 映射为 scene（场景级参考图）
  ELSE:
    → mapped_type = pending_asset.type  # character / object 直接使用

  image_entry = {
    asset_id: pending_asset.asset_id
    asset_type: mapped_type           # 修正后的类型
    final_prompt: pending_asset.final_prompt    # ⭐ 从 pending_asset 获取（Step 3.1 已提取）
    negative_prompt: pending_asset.negative_prompt  # ⭐ 从 pending_asset 获取
    purpose: determine_purpose(mapped_type)
    priority: pending_asset.priority

    # ⭐ v0.6 新增：视角处理
    required_views: determine_required_views(mapped_type)
    views: determine_view_labels(mapped_type)
  }
```

### 3.3 purpose + required_views 推断规则

```text
# 类型 → purpose 映射
character       → "character_reference"     # 角色面部参考图
scene (location) → "scene_reference"       # 场景参考图
scene (crowd)   → "scene_reference"       # crowd 也映射为 scene
object          → "object_reference"        # 物品参考图

# 类型 → required_views（需要生成的视角数量）
character       → 1                         # 角色只需要 1 张全身图/肖像图
scene           → 4                         # 场景需要 4 个视角（东南西北）
object          → 1                         # 物品只需要 1 张

# 视角标签（scene 专用）
scene.views     → ["north", "south", "east", "west"]
```

---

## Step 4️⃣ 构建 voice_prompts.yaml

### 4.1 提取对白

```text
voice_tasks = []

FOR each shot in resolved.shots:
  # 从 prompt_ir 的 dialogue 中提取（如果存在）
  # ⭐ 从 resolved.shots 数组中按 shot_id 查找
  dialogue = resolved.shots.find(s → s.shot_id == shot_id).dialogue

  IF dialogue 存在:
    FOR each line in dialogue:
      voice_task = {
        shot_id: shot_id
        character_id: line.speaker          # ⭐ 从 dialogue.speaker 映射
        dialogue: line.text
        voice_style: infer_voice_style(line.type, line.emotion)  # 从 type+emotion 推断
        duration_estimate: 估算时长（len(text) * 0.15，clamp 1.5~10s）
        emotion_tags: [line.emotion]        # ⭐ 从 dialogue.emotion 提取
        volume: infer_volume(line.type, line.emotion)     # ⭐ 音量级别
        pace: infer_pace(line.type, line.emotion)          # ⭐ 语速
        timing: infer_timing(shot_id, line, voice_tasks)   # ⭐ 时间同步
      }
      → 添加到 voice_tasks
```

### 4.2 voice_style 推断规则

```text
infer_voice_style(type, emotion):
  # 基于对白类型推断基调
  base = {
    spoken:        "natural"
    voiceover:     "narrative, calm"
    inner_thought: "soft, introspective"
    crowd:         "ambient, layered"
  }

  # 叠加情绪修饰
  emotion_modifiers = {
    anger:         ", intense, sharp"
    sadness:       ", slow, heavy"
    fear:          ", tense, trembling"
    joy:           ", bright, energetic"
    surprise:      ", sharp, rising"
    calm:          ", steady, composed"
    default:       ""
  }

  voice_style = base[type] + emotion_modifiers[emotion]
```

### 4.3 时长估算

```text
# 简单估算规则
duration_estimate = len(dialogue) * 0.15   # 中文字符 * 0.15 秒/字
# 最小值 1.5 秒，最大值 10 秒
```

### 4.4 音量推断规则

```text
infer_volume(type, emotion):
  # 基于对白类型
  base = {
    voiceover:     "quiet"
    inner_thought: "quiet"
    crowd:         "loud"
    spoken:        "normal"
  }

  # 情绪覆盖
  emotion_override = {
    anger:    "loud"
    shout:    "shout"
    whisper:  "whisper"
    fear:     "quiet"
    sadness:  "quiet"
    surprise: "loud"
    joy:      "loud"
    calm:     "normal"
  }

  → 优先使用 emotion_override[emotion]，否则用 base[type]
```

### 4.5 语速推断规则

```text
infer_pace(type, emotion):
  # 基于情绪推断
  emotion_pace = {
    anger:    "fast"
    fear:     "fast"
    surprise: "fast"
    sadness:  "slow"
    calm:     "normal"
    joy:      "fast"
    default:  "normal"
  }

  # 对白类型覆盖
  IF type == "voiceover":
    → "slow"
  ELIF type == "inner_thought":
    → "slow"

  → 优先使用 emotion_pace[emotion]
```

### 4.6 时间同步推断规则

```text
infer_timing(shot_id, line, existing_voice_tasks):
  timing = {
    start_offset: 0.0              # 默认从镜头开始处
    overlap_with_previous: false    # 默认不重叠
  }

  # 判断起始偏移
  IF 对白是镜头第一条 AND shot 不是开场镜头:
    → start_offset = 0.5          # 留出场景建立时间
  ELIF 对白是镜头内的后续条目:
    → start_offset = sum(前序 voice_tasks 的 duration_estimate) + 0.3  # 间隔 0.3s

  # 判断是否与上一镜头重叠
  previous_task = existing_voice_tasks 中最后一个
  IF previous_task 存在:
    prev_end = previous_task.timing.start_offset + previous_task.duration_estimate
    IF prev_end > 当前镜头的 duration:
      → overlap_with_previous = true
```

---

## Step 5️⃣ 构建 asset_manifest.yaml

### 5.1 资产状态汇总

```text
assets = { characters: [], locations: [], objects: [] }
seen_asset_ids = SET()          # ⭐ 去重：避免同一资产被多次添加

FOR each shot in resolved.shots:
  # ⭐ 从 continuity.character_bindings 提取
  FOR each char_binding in shot.continuity.character_bindings:
    asset_id = char_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        reference_images = [registry_entry.reference.face_image] IF registry_entry.reference.face_image ELSE []
        status = "approved" IF registry_entry.reference.face_image ELSE "pending"

        manifest_entry = {
          asset_id: asset_id
          status: status
          reference_images: reference_images
          used_in_shots: [shot.shot_id]   # ⭐ 后续会在 Step 5.2 合并
        }
        → assets.characters.append(manifest_entry)

  # ⭐ 从 continuity.location_bindings 提取
  FOR each loc_binding in shot.continuity.location_bindings:
    asset_id = loc_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        reference_images = [registry_entry.reference.scene_image] IF registry_entry.reference.scene_image ELSE []
        status = "approved" IF registry_entry.reference.scene_image ELSE "pending"

        manifest_entry = {
          asset_id: asset_id
          status: status
          reference_images: reference_images
          view_labels: ["north", "south", "east", "west"]  # 场景 4 视角
          used_in_shots: [shot.shot_id]
        }
        → assets.locations.append(manifest_entry)

  # ⭐ 从 continuity.object_bindings 提取
  FOR each obj_binding in shot.continuity.object_bindings:
    asset_id = obj_binding.asset_id
    IF asset_id NOT IN seen_asset_ids:
      seen_asset_ids.add(asset_id)
      registry_entry = registry查找(asset_id)

      IF registry_entry 存在:
        reference_images = [registry_entry.reference.object_image] IF registry_entry.reference.object_image ELSE []
        status = "approved" IF registry_entry.reference.object_image ELSE "pending"

        manifest_entry = {
          asset_id: asset_id
          status: status
          reference_images: reference_images
          used_in_shots: [shot.shot_id]
        }
        → assets.objects.append(manifest_entry)

# ⭐ 合并 used_in_shots（同一资产可能被多个 shot 引用）
FOR each asset_list in [assets.characters, assets.locations, assets.objects]:
  FOR each manifest_entry in asset_list:
    # 收集所有引用该资产的 shot_id
    all_shots = []
    FOR each shot in resolved.shots:
      FOR each char_binding in shot.continuity.character_bindings:
        IF char_binding.asset_id == manifest_entry.asset_id:
          → all_shots.append(shot.shot_id)
      FOR each loc_binding in shot.continuity.location_bindings:
        IF loc_binding.asset_id == manifest_entry.asset_id:
          → all_shots.append(shot.shot_id)
      FOR each obj_binding in shot.continuity.object_bindings:
        IF obj_binding.asset_id == manifest_entry.asset_id:
          → all_shots.append(shot.shot_id)
    manifest_entry.used_in_shots = 去重后的 all_shots
```

**关键修复**：`referenced_assets` 在 resolved_shots 中为空，必须从 `continuity.character_bindings`、`continuity.location_bindings`、`continuity.object_bindings` 中提取。

### 5.2 生成任务清单

```text
generation_tasks = []

# 图片生成任务（从 pending_images 提取）
FOR each pending in pending_images:
  generation_tasks.append({
    task_type: "image"
    asset_id: pending.asset_id
    priority: pending.priority
    depends_on: []                       # 图片任务无前置依赖
  })

# 配音生成任务（从 voice_tasks 提取）
FOR each voice in voice_tasks:
  # 查找该角色的 reference_images 是否已就绪
  character_asset = registry.characters[voice.character_id]
  IF character_asset.generation_status.image == "approved":
    depends_on = []
  ELSE:
    depends_on = [character_asset.asset_id + "_image"]

  generation_tasks.append({
    task_type: "voice"
    shot_id: voice.shot_id
    character_id: voice.character_id
    priority: "high"
    depends_on: depends_on
  })
```

### 5.3 依赖关系图

```text
dependency_graph = {}

FOR each task in generation_tasks:
  # 视频任务依赖图片和配音
  IF task is video:
    depends_on = []
    FOR each referenced_asset in shot.referenced_assets:
      IF asset.status == "pending":
        depends_on.append(asset.asset_id + "_image")
    FOR each voice_task in shot.voice_tasks:
      depends_on.append(voice_task.shot_id + "_voice")

    dependency_graph[shot_id + "_video"] = { depends_on: depends_on }
```

---

## Step 6️⃣ ⭐ 更新 asset_registry 使用追踪

```text
# 读取当前 registry
registry = 读取 asset_registry.yaml

FOR each shot in resolved.shots:
  # ⭐ 从 continuity bindings 提取资产（不是 referenced_assets）
  FOR each char_binding in shot.continuity.character_bindings:
    asset_id = char_binding.asset_id
    registry_entry = registry查找(asset_id)

    IF registry_entry 存在:
      # 更新 usage.used_in_chapters（去重）
      IF chapter_id NOT IN registry_entry.usage.used_in_chapters:
        → 追加 chapter_id

      # 更新 usage.used_in_shots（去重）
      IF shot.shot_id NOT IN registry_entry.usage.used_in_shots:
        → 追加 shot_id

      # 更新 usage.used_count
      → registry_entry.usage.used_count += 1

      # 更新 timestamps.updated_at
      → registry_entry.timestamps.updated_at = 当前日期

  FOR each loc_binding in shot.continuity.location_bindings:
    asset_id = loc_binding.asset_id
    registry_entry = registry查找(asset_id)

    IF registry_entry 存在:
      IF chapter_id NOT IN registry_entry.usage.used_in_chapters:
        → 追加 chapter_id
      IF shot.shot_id NOT IN registry_entry.usage.used_in_shots:
        → 追加 shot_id
      → registry_entry.usage.used_count += 1
      → registry_entry.timestamps.updated_at = 当前日期

  FOR each obj_binding in shot.continuity.object_bindings:
    asset_id = obj_binding.asset_id
    registry_entry = registry查找(asset_id)

    IF registry_entry 存在:
      IF chapter_id NOT IN registry_entry.usage.used_in_chapters:
        → 追加 chapter_id
      IF shot.shot_id NOT IN registry_entry.usage.used_in_shots:
        → 追加 shot_id
      → registry_entry.usage.used_count += 1
      → registry_entry.timestamps.updated_at = 当前日期

# 写回 registry
写入 asset_registry.yaml
```

**关键修复**：`referenced_assets` 为空，必须从 `continuity.character_bindings`、`continuity.location_bindings`、`continuity.object_bindings` 提取。

---

## Step 7️⃣ 输出文件

```text
写入 {output_dir}/video_prompts.yaml
写入 {output_dir}/image_prompts.yaml
写入 {output_dir}/voice_prompts.yaml
写入 {output_dir}/asset_manifest.yaml
更新 {memory_dir}/asset_registry.yaml   # ⭐ 使用追踪
```

---

---

# 📤 输出文件示例

---

## video_prompts.yaml 示例

```yaml
chapter_id: "1"
platform: "hailuo"

# 生成策略配置
generation_strategy:
  mode: "shot_per_video"
  batch_size: 5
  auto_merge: false
  output_for_edit:
    enabled: true
    transition_hints: true

shots:
  - shot_id: "C1-S3-shot20"
    final_prompt: "young Asian male, late 20s..."
    negative_prompt: "blur, distorted face..."

    edit_metadata:
      location_id: "C1-S3"
      sequence: 20
      duration: 4
      transition_in: "cut"
      transition_out: "smooth"

    request:
      duration: 4
      aspect_ratio: "9:16"
      image_references:
        - path: "assets/characters/shen_yan/face_v1.png"
          weight: 0.9
      seed: 12345
```

---

## image_prompts.yaml 示例

```yaml
chapter_id: "1"

# 需要生成参考图的资产
pending_images:
  - asset_id: "lin_xiao_v1"
    asset_type: "character"
    final_prompt: "Portrait of young Asian female..."
    purpose: "character_reference"
    priority: "high"

  - asset_id: "ring_1_intact_v1"
    asset_type: "object"
    final_prompt: "Diamond ring, elegant design..."
    purpose: "object_reference"
    priority: "medium"

# 已有参考图（可复用）
completed_images:
  - asset_id: "shen_yan_v1"
    asset_type: "character"
    image_path: "assets/characters/shen_yan/face_v1.png"
    generated_at: "2024-01-15"
    status: "approved"
```

---

## voice_prompts.yaml 示例

```yaml
chapter_id: "1"

voice_tasks:
  - shot_id: "C1-S3-shot20"
    character_id: "shen_yan"
    dialogue: "我早就说过，这件事没那么简单。"
    voice_style: "calm, low, threatening undertone"
    duration_estimate: 3.5
    emotion_tags:
      - "contained_anger"
      - "confidence"
    volume: "normal"
    pace: "slow"
    timing:
      start_offset: 0.5
      overlap_with_previous: false
```

---

## asset_manifest.yaml 示例

```yaml
chapter_id: "1"
generated_at: "2024-01-20"

assets:
  characters:
    - asset_id: "shen_yan_v1"
      status: "approved"
      reference_images: ["assets/characters/shen_yan/face_v1.png"]
      used_in_shots: ["C1-S3-shot20", "C1-S3-shot21"]

  locations:
    - asset_id: "banquet_hall_day_v1"
      status: "approved"
      reference_images: ["assets/scenes/banquet_hall/day_v1.png"]
      used_in_shots: ["C1-S3-shot20"]

  objects:
    - asset_id: "ring_1_intact_v1"
      status: "pending"
      reference_images: []
      used_in_shots: ["C1-S3-shot20"]

# 生成任务清单
generation_tasks:
  - task_type: "image"
    asset_id: "ring_1_intact_v1"
    priority: "medium"
    depends_on: []

# 依赖关系
dependency_graph:
  "C1-S3-shot20_video":
    depends_on:
      - "ring_1_intact_v1_image"
```

---

---

# 🚫 Anti-Patterns

---

❌ 修改 resolved_shots 或 final_prompts 的内容（Splitter 只读原始数据）
❌ 不更新 asset_registry 的使用追踪（会导致跨章节追踪失效）
❌ 重复追加 used_in_chapters / used_in_shots（必须去重）
❌ 在 video_prompts 中硬编码平台参数（应从 final_prompts 传递）
❌ 忽略 generation_strategy 配置（影响后续批量生成效率）
❌ 缺少 edit_metadata（auto-edit skill 需要剪辑元数据）

---

---

# 🧩 Final Note

---

> Output Splitter v1.0 的核心设计：
>
> 👉 **四种输出，各司其职**
> - video_prompts → 视频生成器
> - image_prompts → 图片生成器（参考图）
> - voice_prompts → 配音生成器
> - asset_manifest → 生成调度器（依赖管理）
>
> 👉 **Registry 使用追踪**
> - 每次拆分后自动更新 used_in_chapters / used_in_shots
> - 确保跨章节资产可追溯
>
> 👉 **剪辑元数据**
> - edit_metadata 支持后续 auto-edit skill 自动剪辑
> - transition_in/out 从 temporal_tags 推断
