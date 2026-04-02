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
      sequence: 从 shot_id 解析序号
      duration: shot.request.duration
      transition_in: 从 temporal_tags 推断
      transition_out: 从 temporal_tags 推断

    # 平台请求参数（直接传递）
    request: shot.request
  }
```

### 2.3 转场推断规则

```text
# 从 temporal_tags 推断转场类型
IF "hard_cut" in temporal_tags:
  → transition_in = "cut"
IF "smooth_transition" in temporal_tags:
  → transition_in = "smooth"
IF "match_cut" in temporal_tags:
  → transition_in = "match"
IF "dramatic_transition" in temporal_tags:
  → transition_in = "dramatic"
DEFAULT:
  → transition_in = "cut"
```

---

## Step 3️⃣ 构建 image_prompts.yaml

### 3.1 收集待生成参考图

```text
pending_images = []
completed_images = []

FOR each asset in resolved referenced_assets:
  registry_entry = registry查找(asset.asset_id)

  IF registry_entry 不存在:
    → 跳过（资产可能未在 registry 中注册）

  IF registry_entry.generation_status.image == "pending":
    → 添加到 pending_images
    → priority = asset.priority（critical > high > medium > low）

  ELIF registry_entry.generation_status.image == "approved":
    → 添加到 completed_images
```

### 3.2 构建图片请求

```text
FOR each pending_asset in pending_images:

  image_entry = {
    asset_id: pending_asset.asset_id
    asset_type: pending_asset.type          # character / scene / object
    final_prompt: registry_entry.final_prompt
    purpose: determine_purpose(type)
    priority: pending_asset.priority
  }
```

### 3.3 purpose 推断规则

```text
character → "character_reference"     # 角色面部参考图
scene     → "scene_reference"         # 场景参考图
object    → "object_reference"        # 物品参考图
```

---

## Step 4️⃣ 构建 voice_prompts.yaml

### 4.1 提取对白

```text
voice_tasks = []

FOR each shot in resolved.shots:
  # 从 prompt_ir 的 dialogue 中提取（如果存在）
  dialogue = resolved[shot_id].dialogue  # 可能为空（无对白镜头）

  IF dialogue 存在:
    FOR each line in dialogue:
      voice_task = {
        shot_id: shot_id
        character_id: line.character_id
        dialogue: line.text
        voice_style: line.voice_style      # 从 canonical 或 IR 提取
        duration_estimate: 估算时长（字数 * 系数）
        emotion_tags: line.emotion_tags     # 从 IR 或 canonical 提取
      }
      → 添加到 voice_tasks
```

### 4.2 时长估算

```text
# 简单估算规则
duration_estimate = len(dialogue) * 0.15   # 中文字符 * 0.15 秒/字
# 最小值 1.5 秒，最大值 10 秒
```

---

## Step 5️⃣ 构建 asset_manifest.yaml

### 5.1 资产状态汇总

```text
assets = { characters: [], locations: [], objects: [] }

FOR each referenced_asset in all shots:
  registry_entry = registry 查找(asset_id)

  manifest_entry = {
    asset_id: asset_id
    status: registry_entry.generation_status.image
    reference_image: registry_entry.reference.face_image / scene_image / object_image
    used_in_shots: 收集所有引用该资产的 shot_id
  }

  # 按资产类型分类
  IF type == "character":
    → assets.characters.append(manifest_entry)
  ELIF type == "scene":
    → assets.locations.append(manifest_entry)
  ELIF type == "object":
    → assets.objects.append(manifest_entry)
```

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
  # 查找该角色的 reference_image 是否已就绪
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
  FOR each referenced_asset in shot.referenced_assets:
    asset_id = referenced_asset.asset_id
    registry_entry = registry 查找(asset_id)

    IF registry_entry 存在:
      # 更新 used_in_chapters（去重）
      IF chapter_id NOT IN registry_entry.used_in_chapters:
        → 追加 chapter_id

      # 更新 used_in_shots（去重）
      IF shot.shot_id NOT IN registry_entry.used_in_shots:
        → 追加 shot_id

      # 更新 last_used
      → registry_entry.generation_status.last_used = 当前日期

# 写回 registry
写入 asset_registry.yaml
```

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
      reference_image: "assets/characters/shen_yan/face_v1.png"
      used_in_shots: ["C1-S3-shot20", "C1-S3-shot21"]

  locations:
    - asset_id: "banquet_hall_day_v1"
      status: "approved"
      reference_image: "assets/scenes/banquet_hall/day_v1.png"
      used_in_shots: ["C1-S3-shot20"]

  objects:
    - asset_id: "ring_1_intact_v1"
      status: "pending"
      reference_image: null
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
