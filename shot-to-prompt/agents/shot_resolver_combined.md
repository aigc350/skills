# Shot Resolver Combined Agent v1.0

> 合并 Agent：Consistency Enforcer + Prompt Resolver + Output Splitter
> 单次遍历所有镜头，输出最终 4 文件 + 更新 registry

---

## 1. 概述

本 Agent 将 3 个解析/输出阶段合并为单次执行，读取构建产物后一次性完成一致性校验、融合解析、平台适配、多模态输出拆分。

### 合并的阶段

| # | 原始阶段 | 职责 | 在本 Agent 中的位置 |
|---|---------|------|-------------------|
| 1 | Consistency Enforcer | 身份一致性校验 + 自动修复 | Phase A |
| 2 | Prompt Resolver | 融合解析 + 冲突裁决 + 平台适配 | Phase B |
| 3 | Output Splitter | 多模态输出拆分 + 资产追踪 | Phase C |

---

## 2. 输入

```yaml
inputs:
  # 构建产物（来自 shot_builder_combined）
  - path: "{runtime_dir}/prompt_built.yaml"
    desc: "合并构建产物（IR + Canonical + Enhanced + Assets + Temporal）"
  # 资产库
  - path: "{memory_dir}/asset_registry.yaml"
    desc: "全局资产注册表"
    required: false
  # 平台映射
  - path: "references/platform_mappings.yaml"
    desc: "平台参数映射"
    required: false
```

---

## 3. 输出

```yaml
outputs:
  # 最终 4 文件
  - path: "{output_dir}/video_prompts.yaml"
    desc: "视频生成请求"
  - path: "{output_dir}/image_prompts.yaml"
    desc: "参考图生成请求"
  - path: "{output_dir}/voice_prompts.yaml"
    desc: "配音生成请求"
  - path: "{output_dir}/asset_manifest.yaml"
    desc: "资产状态汇总"
  # 更新资产库（追加使用追踪）
  - path: "{memory_dir}/asset_registry.yaml"
    desc: "更新 used_in_chapters / used_in_shots"
```

---

## 4. 执行流程

### 全局初始化

```
1. 读取 prompt_built.yaml（一次性）
2. 解构各层数据：
   - ir ← prompt_built.ir
   - canonical ← prompt_built.canonical
   - enhanced ← prompt_built.enhanced
   - reusable_assets ← prompt_built.reusable_assets
   - assets ← prompt_built.assets
   - temporal ← prompt_built.temporal
3. 加载 asset_registry（如不存在则为空）
4. 加载 platform_mappings（默认 hailuo）
5. 初始化上下文：
   - asset_map: {}（asset_id → 资产）
   - repairs_applied: []
   - issues: []
   - video_prompts: []
   - pending_images: []
   - completed_images: []
   - voice_tasks: []
   - manifest_assets: []
```

---

### Phase A: Consistency Enforcer

遍历每个 shot，校验并修复一致性问题：

```
FOR EACH shot IN ir.shots:
  1. 构建 Asset Map：从 assets 层提取 character/location/object 的 asset_id → 数据

  2. 自动修复 1 — fingerprint 缺失：
     IF character 存在但 appearance_fingerprint 为空:
       → 从 asset_registry 提取
       → 或从 base_prompt 提取关键特征
       → 记录 repair: { type: "fingerprint_added", ... }

  3. 自动修复 2 — prompt 与 fingerprint 冲突：
     IF prompt 描述与 fingerprint 不一致:
       → fingerprint 优先，覆盖 prompt 文本
       → 记录 repair: { type: "prompt_overridden_by_fingerprint", ... }

  4. 自动修复 3 — reference 注入：
     IF registry 中有 face_image/scene_image 但 prompt 中未引用:
       → 注入 reference_image
       → 记录 repair: { type: "reference_injected", ... }

  5. 自动修复 4 — asset_id 纠正：
     IF shot 中 asset_id 与 registry 不匹配:
       → 以 registry 为准纠正
       → 记录 repair: { type: "asset_id_corrected", ... }

  6. 构建 bindings：
     - character_bindings: [{ character_id, asset_id, reference_image, fingerprint, must_keep, variant_locked }]
     - location_bindings: [{ location_id, asset_id, reference_image, anchors }]
     - object_bindings: [{ object_id, asset_id, state, reference_image }]

  7. 构建标签：
     - spatial_tags: [same_location, location_change, ...]
     - temporal_tags: [continuing_action, time_jump, ...]

  8. 存入 shot_consistency[shot_id] = { bindings, tags, repairs }
```

---

### Phase B: Prompt Resolver

遍历每个 shot，融合所有层 → 平台适配 → 生成最终 prompt：

```
FOR EACH shot IN ir.shots:
  # ── Phase B-1: Resolve（融合）──

  1. 融合 resolved_prompt：
     - subject ← assets 层的 final_prompt（身份 + 变体）
     - action ← canonical 层的 action semantic
     - environment ← canonical 层的 environment semantic
     - camera ← canonical 层的 camera semantic
     - style ← enhanced 层的增强关键词
     - quality ← enhanced 层的质量关键词
     - negative ← enhanced 层的负面关键词
     - temporal ← temporal 层的时序上下文

  2. 冲突优先级裁决（5 级，高优先级覆盖低优先级）：
     reference_image > seed > must_keep > appearance_fingerprint > final_prompt

     应用规则：
     - reference_image 存在 → 强制注入，覆盖 prompt 中的身份描述
     - seed 继承 → 同一角色的 seed 必须一致（从 temporal 继承）
     - must_keep 锚点 → 绝对保留（fingerprint 中的 face_shape, eye_color 等）
     - fingerprint vs prompt 冲突 → fingerprint 胜出
     - final_prompt → 最低优先级，可被上述所有规则覆盖

  3. 构建 continuity_bindings：
     - character_continuity: [{ character_id, seed, reference, must_keep }]
     - location_continuity: [{ location_id, reference, anchors }]

  4. 构建 dramatic_focus：
     - hook_type ← enhanced 层
     - opening_beat ← enhanced 层
     - payoff_target ← enhanced 层

  5. 多 reference 优先级排序：
     critical > high > medium > low
     （同一角色的 reference 优先级最高）

  6. 构建 resolver_trace（追踪哪些层被合并、哪些修复被应用）

  # ── Phase B-2: Adapt（平台适配）──

  7. 读取 target platform（默认 hailuo）的映射规则

  8. 转换抽象参数：
     - reference_strength → weight（hailuo）/ strength（runway）/ fidelity（kling）
     - prompt_detail → suffix / simplify / expand

  9. 应用平台规则：
     - hailuo: max_prompt_length=200, fast_generation=true
     - runway: max_prompt_length=300, camera_control=true
     - kling: max_prompt_length=250, chinese_support=true
     - sora: max_prompt_length=400, long_video=true
     - pika: max_prompt_length=200, fast_generation=true

  10. 处理 reference 限制：
      - max_refs per platform（hailuo=3, runway=2, kling=3, sora=4, pika=2）
      - 超出时按优先级截断

  11. Seed 参数映射：
      - seed_locked → 平台锁定标记
      - seed 值直接传递

  12. 组装 final_prompt：
      resolved_prompt 经过平台适配后的最终文本

  13. 存入 resolved_shots[shot_id] 和 final_prompts[shot_id]
```

---

### Phase C: Output Splitter

将 resolved + final 数据拆分为 4 个输出文件：

```
# ── video_prompts.yaml ──
video_prompts = {
  chapter_id: ...,
  platform: "hailuo",
  generation_strategy: {
    mode: "shot_per_video",
    batch_size: 5,
    auto_merge: false,
    output_for_edit: { enabled: true, transition_hints: true }
  },
  shots: []
}

FOR EACH shot IN final_prompts:
  video_entry = {
    shot_id: shot.shot_id,
    final_prompt: shot.final_prompt,
    negative_prompt: shot.negative_prompt,
    edit_metadata: {
      location_id: shot.location_id,
      sequence: shot.sequence,
      duration: 4,  // 默认
      transition_in: 从 temporal_tags 推导 (cut/smooth/match/dramatic),
      transition_out: 从 temporal_tags 推导
    },
    request: {
      duration: 4,
      aspect_ratio: "9:16",
      quality: "high",
      image_references: shot.references,  // [{ path, weight }]
      seed: shot.seed,
      seed_locked: shot.seed_locked
    }
  }
  video_prompts.shots.append(video_entry)

# ── image_prompts.yaml ──
pending_images = []
completed_images = []

FOR EACH asset IN all_assets:
  IF asset.generation_status.image == "pending":
    pending_images.append({
      asset_id: asset.asset_id,
      asset_type: "character|scene|object",
      final_prompt: asset.final_prompt,
      purpose: "character_reference|scene_reference|object_reference",
      priority: "critical|high|medium"  // character=critical, scene=high, object=medium
    })
  ELIF asset.generation_status.image == "approved":
    completed_images.append({...})

image_prompts = {
  chapter_id: ...,
  pending_images: sorted(pending_images, key=priority),
  completed_images: completed_images
}

# ── voice_prompts.yaml ──
voice_tasks = []

FOR EACH shot IN ir.shots:
  IF shot.dialogue 存在且非空:
    voice_tasks.append({
      shot_id: shot.shot_id,
      character_id: shot.subject.character_id,
      dialogue: shot.dialogue,
      voice_style: 从 character 定义推导,
      duration_estimate: len(dialogue) * 0.15,
      emotion_tags: [shot.emotion],
      volume: "normal",
      pace: "normal",
      timing: { start_after: previous_dialogue_end }
    })

voice_prompts = {
  chapter_id: ...,
  voice_tasks: voice_tasks
}

# ── asset_manifest.yaml ──
manifest_assets = []
generation_tasks = []

FOR EACH asset IN all_assets:
  status = determine_status(asset)
  manifest_assets.append({
    asset_id, asset_type, status,
    used_in_chapter: chapter_id,
    reference_available: asset.reference.face_image != null
  })

  IF status == "pending":
    generation_tasks.append({
      task_type: "image_generation",
      asset_id: asset.asset_id,
      priority: determine_priority(asset),
      depends_on: []
    })

# 视频依赖 pending 图片
FOR EACH video_task IN video_prompts.shots:
  generation_tasks.append({
    task_type: "video_generation",
    shot_id: video_task.shot_id,
    depends_on: [pending image assets for this shot]
  })

asset_manifest = {
  chapter_id: ...,
  assets: manifest_assets,
  generation_tasks: generation_tasks,
  dependency_graph: build_dependency_graph(generation_tasks)
}

# ── 更新 asset_registry ──
FOR EACH asset IN registry:
  IF chapter_id NOT IN asset.used_in_chapters:
    asset.used_in_chapters.append(chapter_id)
  FOR EACH shot_id WHERE asset IS used:
    IF shot_id NOT IN asset.used_in_shots:
      asset.used_in_shots.append(shot_id)
  asset.generation_status.last_used = today
```

---

## 5. 权限模型

| 阶段 | semantic | text | quality | negative | final | registry |
|------|----------|------|---------|----------|-------|----------|
| Phase A (Consistency) | READ ONLY | 可修复 | READ ONLY | READ ONLY | READ ONLY | READ ONLY |
| Phase B (Resolver) | READ ONLY | FULL | 可精炼 | 可精炼 | FULL | READ ONLY |
| Phase C (Splitter) | READ ONLY | READ ONLY | READ ONLY | READ ONLY | READ ONLY | 可更新追踪 |

---

## 6. 冲突裁决规则

5 级优先级（从高到低）：

```
1. reference_image  — 注册表中的 approved 图片，绝对优先
2. seed             — 同角色的种子继承，保证一致性
3. must_keep        — fingerprint 中的不可变特征（face_shape, eye_color 等）
4. appearance_fingerprint — 身份指纹，高于文本描述
5. final_prompt     — 文本描述，最低优先级，可被覆盖
```

裁决逻辑：

```
FOR EACH conflict:
  higher = max(left.priority, right.priority)
  winner = higher.source
  loser = lower.source
  IF loser != winner:
    override(loser, winner.value)
    trace.record("conflict_resolved", { field, winner, loser, reason })
```

---

## 7. 平台适配规则

### hailuo（默认）

```yaml
max_prompt_length: 200
max_references: 3
reference_param: weight  # 0.0-1.0
default_duration: 4
fast_generation: true
```

### runway

```yaml
max_prompt_length: 300
max_references: 2
reference_param: strength  # 0.0-1.0
default_duration: 5
camera_control: true
```

### kling

```yaml
max_prompt_length: 250
max_references: 3
reference_param: fidelity  # 0.0-1.0
default_duration: 5
chinese_support: true
```

### sora

```yaml
max_prompt_length: 400
max_references: 4
reference_param: weight  # 0.0-1.0
default_duration: 10
long_video: true
```

### pika

```yaml
max_prompt_length: 200
max_references: 2
reference_param: strength  # 0.0-1.0
default_duration: 3
fast_generation: true
```

---

## 8. 性能优化

### 相比原始 Pipeline 的优势

| 维度 | 原始 Pipeline | Combined Resolver |
|------|-------------|------------------|
| 文件读取次数 | 3 次 × 70K = 210K | 1 次 × 70K |
| Agent 启动开销 | 3 次 | 1 次 |
| 内存传递 | 无（文件中转） | 全程内存 |
| registry 更新 | 2 次（consistency + splitter） | 1 次 |

---

## 9. 错误处理

| 情况 | 处理 |
|------|------|
| prompt_built.yaml 不存在 | 报错，需先运行 shot_builder_combined |
| asset_registry 不存在 | 跳过 Phase A 的自动修复，所有 reference 为 null |
| platform_mappings 不存在 | 使用内置默认 hailuo 配置 |
| prompt 超过平台长度限制 | 自动截断，保留核心语义 |
| reference 数量超过限制 | 按优先级截断 |
| 无 dialogue 的 shot | voice_tasks 跳过该 shot |

---

## 10. 约束

1. **单次遍历**：每个 shot 只遍历一次，Phase A/B/C 在同一遍历中完成
2. **无文件中转**：Phase 之间通过内存传递
3. **最终输出 4 文件**：video_prompts + image_prompts + voice_prompts + asset_manifest
4. **registry 更新**：仅追加 used_in_chapters / used_in_shots，不修改已有数据
5. **确定性**：相同输入必须产生相同输出
6. **字段所有权不变**：各 Phase 的字段权限与独立 Agent 一致
