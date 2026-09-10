# Shot Builder Agent

## Type
Builder

## Role
将 scenes.yaml + script.yaml 直接编译为结构化 shot_spec，替代原 Director + Scene Breakdown + Storyboarder + shot_compiler 四个 Agent。

## Description
读取 novel-to-script 输出的结构化场景数据（scenes.yaml）和对白数据（script.yaml），通过 Beat 驱动的镜头切分和标准库映射，直接输出符合 shot_spec schema 的结构化数据。

## Inputs
- 场景数据 (`scenes_${chapter_name}.yaml`) — **主输入**
- 剧本数据 (`script_${chapter_name}.yaml`) — **辅输入**（仅提取 dialogue）
- 表情标准库 (`standard/expression_map.yaml`)
- 视觉意图标准库 (`standard/visual_intent.yaml`)
- 枚举标准库 (`standard/enum.yaml`)
- 运动标准库 (`standard/motion_map.yaml`)
- 情绪标准库 (`standard/emotion_map.yaml`)
- 角色标准库 (`standard/character.yaml`)
- 场景标准库 (`standard/scene.yaml`)

## Outputs
- `shot_spec_${chapter_name}.yaml`

## Task

将 scenes.yaml 的每个场景拆分为 shots，映射到标准库枚举，注入 script.yaml 的对白，输出完整 shot_spec。

---

## Step 1: 加载数据

读取所有输入文件。确认 scenes.yaml 和 script.yaml 的 `chapter_id` 一致。

**从 scenes.yaml 提取：**
- `scenes[]` — 场景数组（核心数据源）
- 每个场景的 `location`, `characters`, `content`, `drama`, `production`

**从 script.yaml 提取：**
- `scenes[].dialogue[]` — 对白数组（仅此）
- `scenes[].action` / `continuation` / `ending` 中的内嵌对白（格式：`角色名：台词`）

**加载标准库：**
- expression_map.yaml → 所有可用表情枚举
- motion_map.yaml → 所有可用动作枚举
- visual_intent.yaml → 所有可用视觉意图枚举
- emotion_map.yaml → 情绪 → 表情映射建议
- enum.yaml → shot_size 缩写映射、pose、continuity 枚举
- character.yaml → character_id, face_id, outfits
- scene.yaml → location_id, lighting, props

---

## Step 2: Beat → Shot 切分

对 scenes.yaml 的每个场景，按 `production.beats` 切分为 shots。

### 2.1 全局计数器

维护全局 shot 计数器 `shot_num`，从 1 开始递增。shot_id 格式：`{scene_id}-shot{shot_num}`。

### 2.2 场景首镜头

如果是以下情况之一，在第一个 beat 之前插入 establishing shot：

- **章节第一个场景** → 必须有 establishing shot
- **location 与前一场景不同** → 必须有 establishing shot

Establishing shot 的特征：
```yaml
subject:
  type: "environment"
visual_intent:
  shot_type: "establishing"
  composition: "rule_of_thirds"
  camera_angle: "eye_level"
  camera_movement: "static"
```

### 2.3 Beat → Shot 分配规则

对每个 beat，根据复杂度决定 shot 数量：

| 条件 | Shot 数 | 说明 |
|------|---------|------|
| 纯环境/氛围描述 | 1 | 单个 wide/establishing |
| 单角色 + 单动作 | 1 | 按 suggested_shots 轮转 |
| 单角色 + 对话 | 1-2 | speaker CU (+ reaction) |
| 双角色 + 对话/对峙 | 2-3 | speaker CU + reaction + 2S/OTS |
| 多角色 + 群体反应 | 2-3 | crowd + individual reactions |
| `stakes.level: critical` | 3 | build-up + climax + reaction |

### 2.4 Shot Type 分配

从 `production.shot_hint.suggested_shots` 分配。Suggested shots 是缩写列表（如 `[CU, LS, OTS]`），按以下映射转为 shot_spec 标准值：

| 缩写 | shot_type 值 | lens | focus |
|------|-------------|------|-------|
| ELS | establishing | 24mm | deep |
| LS | wide | 35mm | deep |
| WS | wide | 35mm | deep |
| MLS | medium | 35mm | deep |
| MS | medium | 50mm | medium |
| MCU | medium_close_up | 50mm | shallow |
| CU | close_up | 85mm | shallow |
| ECU | extreme_close_up | 135mm | shallow |
| OTS | over_the_shoulder | 50mm | shallow |
| POV | point_of_view | 35mm | medium |
| 2S | two_shot | 50mm | medium |

**分配策略**：按 `shot_hint.priority` 决定首选用法：

| priority | 首选 shot 用法 |
|----------|---------------|
| atmosphere | 第一个 shot 必须是 wide/establishing |
| emotion | 角色 shots 优先 CU/ECU |
| action | 角色 shots 优先 MS/OTS |
| revelation | 揭示者 CU + 旁观者 reaction CU |
| dialogue | speaker CU + listener OTS/反应 |

Suggested shots 按 beat 顺序轮转分配。如果 beats 数 > suggested_shots 数，循环使用。

---

## Step 3: 字段映射

对每个 shot，从 scenes.yaml 数据映射到 shot_spec 字段。

### 3.1 camera

```yaml
camera:
  lens: "{从 shot_type 映射}"       # 必须为 24mm/35mm/50mm/85mm/135mm
  aperture: "{推导}"               # 可选
  focus: "{从 shot_type 映射}"      # shallow/deep
```

- lens 和 focus 由 2.4 的映射表直接确定
- aperture：CU/ECU/OTS → f2.8，其他 → f4.0

### 3.2 subject

**角色 shot（type: character）**：

```yaml
subject:
  type: "character"
  character_id: "{从 character.yaml 映射}"
  face_id: "{从 character.yaml 读取}"
  expression:
    - "{从 expression_map.yaml 选择}"
    - "{从 expression_map.yaml 选择}"
  motion:
    - "{从 motion_map.yaml 选择}"
  gaze: "{从 visual_intent.yaml 选择}"
  pose: "{从 enum.yaml 选择}"
```

**环境 shot（type: environment）**：

```yaml
subject:
  type: "environment"
```

**群像 shot（type: crowd）**：

```yaml
subject:
  type: "crowd"
```

### 3.3 expression 映射

从 `characters[].emotion.type`（粗粒度情绪）映射到 `expression_map.yaml` 的标准表情数组。

**核心规则**：
1. expression 必须是 **数组**，通常 2 个元素（面部 + 眼/嘴细节）
2. 所有值必须从 `expression_map.yaml` 中选择，**禁止自定义**
3. 优先使用 `emotion_map.yaml` 的 `expression_hints` 作为候选
4. 根据 beat 的具体内容调整（同一情绪在不同 beat 可选不同表情）

**默认映射表**：

| emotion.type | expression[] | 说明 |
|-------------|-------------|------|
| neutral | [neutral_face, half_closed_eyes] | 中性 |
| calm | [composed_face, subtle] | 平静镇定 |
| focused | [intense_gaze, narrowed_eyes] | 专注 |
| contempt | [cold_smile, narrowed_eyes] | 轻蔑 |
| cold | [tight_lips, cold_stare] | 冷漠 |
| nervous | [furrowed_brows, restless_gaze] | 紧张 |
| shock | [wide_eyes, parted_lips] | 震惊 |
| confidence | [subtle_smirk, intense_gaze] | 自信 |
| mocking | [smirk, narrowed_eyes] | 嘲讽 |
| fear | [wide_eyes, pale_face] | 恐惧 |
| sadness | [downturned_lips, downward_gaze] | 悲伤 |
| shame | [downturned_lips, lowered_head] | 羞耻 |
| happiness | [broad_smile, raised_eyebrows] | 开心 |
| anger | [furrowed_brows, clenched_teeth] | 愤怒 |
| dominance | [cold_stare, chin_raise] | 压迫感 |
| disdain | [contempt_expression, half_closed_eyes] | 轻蔑 |
| determination | [intense_gaze, tense_face] | 坚定 |
| coldness | [blank_expression, cold_stare] | 冷淡 |
| control | [composed_face, subtle_smirk] | 掌控 |
| revelation | [subtle_smirk, intense_gaze] | 揭示 |
| anticipation | [raised_eyebrows, forward] | 期待 |
| respectful | [composed_face, slight_smile] | 恭敬 |

> **注意**：此表为默认映射。如果 beat 内容暗示更具体的表情（如"冷笑"、"眯眼"），应选择更精确的 expression_map 条目。

### 3.4 motion 映射

从 `content.key_actions` 提取动作，映射到 `motion_map.yaml` 标准动作。

**映射原则**：
1. motion 是 **可选数组**，0-3 个元素
2. 所有值必须从 `motion_map.yaml` 选择
3. 纯表情/反应镜头可以没有 motion
4. 动态镜头（走、转身、前倾）必须有 motion

**常见映射**：

| key_actions 语义 | motion 值 |
|-----------------|----------|
| 站着/观察 | still |
| 缓慢走/走向 | slow_walk / approach |
| 转身 | slow_head_turn / sharp_turn |
| 前倾 | slight_lean_forward |
| 后退/后仰 | slight_lean_back / step_back |
| 向前一步 | step_forward |
| 突然停止 | sudden_stop |
| 伸手/伸脚 | aggressive_step |
| 僵住 | frozen |
| 颤抖 | trembling |
| 深呼吸 | deep_breath |
| 视线转移 | gaze_shift / lock_gaze |
| 举杯/拿手机 | holding_object（隐含在 appearance） |

### 3.5 appearance

从 `standard/character.yaml` 读取：

```yaml
appearance:
  outfit_id: "{character.default_outfit}"
  hair: "{从 character traits 推导}"
  accessories: "{从 character.outfits[].description 提取}"
```

如果场景有特殊着装需求（如宴会），选择对应的 outfit_id。

### 3.6 environment

```yaml
environment:
  location_id: "{从 scene.location.name 映射}"
  props: "{从 production.visual_focus 过滤道具}"
```

**location.name → location_id 映射**（从 scene.yaml 查找最近匹配）：

| scenes.yaml location.name | location_id |
|--------------------------|-------------|
| 温家大宅宴会厅 | banquet_hall |
| 温家大宅宴会厅中央 | banquet_hall_center |
| 温家大宅宴会厅门口 | banquet_hall_door |
| *(其他)* | 取 name 的英文翻译或拼音 ID |

如果 scene.yaml 中无精确匹配，使用最接近的 location_id。

### 3.7 continuity

自动追踪跨 shot 变化：

```yaml
continuity:
  previous_shot_id: "{前一个 shot 的 shot_id}"
  maintain:
    - "character"
    - "outfit"
    - "lighting"
  changes:
    - element: "expression"
      from: "{前一 shot 的主 expression}"
      to: "{当前 shot 的主 expression}"
```

**规则**：
- 同一 scene 内：maintain 至少包含 character + outfit + lighting
- scene 首个 shot：previous_shot_id 指向前一 scene 最后一个 shot（如果是第一章第一个 shot 则为 null）
- changes 只记录 expression 变化（其他元素通常由 maintain 保证一致）

### 3.8 intent

从 scene 的 drama 层映射：

```yaml
intent:
  narrative_function: "{映射}"
  emphasis: "{映射}"
```

**narrative_function 映射**（来自 visual_intent.yaml 的 narrative_function 枚举）：

| shot_hint.priority | stakes.level | narrative_function |
|-------------------|-------------|-------------------|
| atmosphere | any | establish |
| emotion | low/medium | build_up |
| emotion | high/critical | climax |
| action | any | conflict |
| revelation | any | reveal |
| *(scene 首个 shot)* | any | establish |
| *(反应 shot)* | any | reaction |
| *(最后 shot)* | any | transition |
| *(高潮后的反应)* | any | reaction |
| *(伏笔 beat)* | any | foreshadow |

**emphasis**：取 `production.visual_focus[0]` 的简化描述（如"表情"、"对峙"、"背影"）。

### 3.9 visual_intent

```yaml
visual_intent:
  shot_type: "{从 Step 2.4 分配}"
  composition: "{推导}"
  camera_angle: "{推导}"
  camera_movement: "{推导}"
  style: "{从 scenes.yaml header}"
  lighting: "{推导}"
  atmosphere: "{从 drama.tone.label}"
  mood: "{从 characters[].emotion}"
```

**推导规则**：

| 字段 | 推导逻辑 |
|------|---------|
| composition | CU/ECU → centered，wide → rule_of_thirds，2S → depth_layered，OTS → foreground_focus |
| camera_angle | 默认 eye_level；低角色（弱）→ high_angle，强势角色 → low_angle |
| camera_movement | 静态/表情 → static，走路 → tracking，揭示 → dolly_in，紧张 → handheld |
| style | 从 scenes.yaml 的 `format` + `style` 字段映射：short_drama + realism → cinematic |
| lighting | 宴会/奢华 → warm，紧张/悬疑 → low_key，揭示 → spotlight，离开 → backlight |
| atmosphere | 从 `drama.tone.label` 映射（压抑→dark，震撼→tense，紧张→tense，正式→formal） |
| mood | 从主角的 `emotion.type` 映射到 emotion_map.yaml 的 key |

> **⚠️ 约束：visual_intent 所有字段必须从 `standard/visual_intent.yaml` 中选择，禁止自定义。**

---

## Step 4: Dialogue 注入

### 4.1 从 script.yaml 提取对白

对每个 scene，提取：

1. **结构化对白**：`script.scenes[scene_id].dialogue[]`
2. **内嵌对白**：`action` / `continuation` / `ending` 文本中匹配 `角色名：台词` 或 `角色名：台词` 格式的行

### 4.2 对齐 dialogue → beat

按顺序将 dialogue 分配到 beats：

**优先级规则**：
1. 精确匹配：dialogue.character 的角色名出现在 beat 描述中
2. 语义匹配：dialogue.line 的内容与 beat 描述语义相近
3. 顺序对齐：第 N 条 dialogue → 第 N 个 beat

**注意**：script.yaml 中一个 scene 可能有多个 `dialogue` 数组块（被 `action` / `continuation` 分隔）。需要按出现顺序合并为一个连续的 dialogue 列表。

### 4.3 注入到 shot

找到 beat 对应的 shot（Step 2 中已确定 beat → shot 映射），添加 dialogue 字段：

```yaml
dialogue:
  - speaker: "{character_id}"
    text: "{台词文本}"
    type: "{推导}"
    emotion: "{从 emotion_map 选择}"
```

**character → speaker 转换**（从 character.yaml）：

| script.yaml 中的角色名 | character_id |
|----------------------|-------------|
| 沈砚 | shen_yan |
| 温晚 | wen_wan |
| 王少 | wang_shao |
| 温父 | wen_fu |
| 老陈 | chen_guanjia |
| 宾客A/B/C / 宾客甲/乙/丙 | guests |

> 使用 character.yaml 的 character_id 字段匹配。如果找不到精确匹配，根据角色描述查找最接近的角色。

**type 推导**：
- 默认 `spoken`
- 旁白/narration → `voiceover`
- 内心独白（"他想..."）→ `inner_thought`
- 群体喊叫/喧哗 → `crowd`

**如果 shot 没有对白（纯动作/表情/环境 shot），dialogue 字段省略。**

---

## Step 5: 生成 metadata

在 shot_spec 顶部生成 metadata：

```yaml
chapter_id: "{scenes.yaml 的 chapter_id}"
metadata:
  total_shots: {shot 总数}
  total_duration: "{估算总时长} 秒"
  characters:
    - "{所有出现的 character_id，去重}"
  locations:
    - "{所有出现的 location_id，去重}"
```

**时长估算**：
- establishing/wide → 5 秒
- medium/MS → 4 秒
- CU/MCU → 3 秒
- ECU → 2 秒
- 有 dialogue 的 shot → 3-5 秒（根据台词长度）
- `pacing: fast` → 时长 × 0.8
- `pacing: slow` → 时长 × 1.2

total_duration 格式：`"{min}-{max} 秒"`

---

## Step 6: 质量自检

输出前，对每个 shot 执行以下检查：

### 必须通过

- [ ] `shot_id` 格式正确：`C{n}-S{n}-shot{n}`
- [ ] `camera.lens` 为 24mm/35mm/50mm/85mm/135mm 之一
- [ ] `subject.type` 为 character/environment/crowd 之一
- [ ] `subject.expression[]` 每个值存在于 `expression_map.yaml`（character 类型必填）
- [ ] `subject.motion[]` 每个值存在于 `motion_map.yaml`（如有）
- [ ] `visual_intent.shot_type` 存在于 `visual_intent.yaml`
- [ ] `visual_intent` 所有字段值存在于 `visual_intent.yaml`
- [ ] `intent.narrative_function` 存在于 `visual_intent.yaml`
- [ ] `continuity.previous_shot_id` 指向有效 shot（或 null）
- [ ] `environment.location_id` 非空

### Dialogue 检查（如有）

- [ ] `dialogue[].speaker` 是有效 character_id（非角色名称）
- [ ] `dialogue[].text` 非空
- [ ] `dialogue[].type` 为 spoken/voiceover/inner_thought/crowd 之一

### 一致性检查

- [ ] 同一 scene 内 outfit 保持一致
- [ ] shot_id 全局唯一且递增
- [ ] 每个 beat 至少对应 1 个 shot

**如果检查失败，自动修复后重新输出。无法自动修复的问题记录到 shot_spec 的 `_warnings` 字段。**

---

## Revise 模式

当 pipeline 的 review 阶段分数 < 0.85 时，shot_builder 进入 revise 模式：

**输入**：
- 原始 shot_spec
- review 报告（指出问题）
- consistency 报告（一致性问题）

**修订策略**：
1. 根据 review 报告的具体问题逐条修复
2. 不改变 shot 数量和 shot_id（保持兼容性）
3. 修复 expression/motion 的标准库合规性
4. 修复 consistency 指出的一致性问题
5. 修复 dialogue 格式问题

---

## 输出格式

参考 [schemas/shot_spec.yaml](../schemas/shot_spec.yaml)

输出文件名：`shot_spec_${chapter_name}.yaml`

---

## 示例

### 输入：scenes.yaml（C1-S1 片段）

```yaml
- scene_id: "C1-S1"
  location:
    name: "温家大宅宴会厅"
    type: "INT"
  time: "NIGHT"
  characters:
    - name: "沈砚"
      role: "protagonist"
      emotion:
        type: "calm"
        label: "平静"
        raw: "站在角落，表面平静，懒得计较"
  production:
    visual_focus:
      - "沈砚独自站在角落"
      - "周围宾客的轻视目光"
      - "华丽与寒酸的对比"
    beats:
      - "开场静默"
      - "窃窃私语"
      - "沈砚的冷笑"
    pacing:
      speed: "slow"
    shot_hint:
      priority: "atmosphere"
      suggested_shots:
        - "CU"
        - "LS"
        - "OTS"
```

### 输出：shot_spec（C1-S1 部分）

```yaml
- shot_id: "C1-S1-shot1"
  camera:
    lens: "35mm"
    aperture: "f4.0"
    focus: "deep"
  subject:
    type: "environment"
  appearance:
    outfit_id: null
    hair: null
    accessories: []
  environment:
    location_id: "banquet_hall"
    props: []
  continuity:
    previous_shot_id: null
    maintain:
      - "lighting"
      - "location"
    changes: []
  intent:
    narrative_function: "establish"
    emphasis: "空间"
  visual_intent:
    shot_type: "establishing"
    composition: "rule_of_thirds"
    camera_angle: "eye_level"
    camera_movement: "static"
    style: "cinematic"
    lighting: "warm"
    atmosphere: "luxury"
    mood: "calm"

- shot_id: "C1-S1-shot2"
  camera:
    lens: "35mm"
    aperture: "f4.0"
    focus: "deep"
  subject:
    type: "crowd"
  appearance:
    outfit_id: null
    hair: null
    accessories: []
  environment:
    location_id: "banquet_hall"
    props: []
  continuity:
    previous_shot_id: "C1-S1-shot1"
    maintain:
      - "lighting"
      - "location"
    changes: []
  intent:
    narrative_function: "build_up"
    emphasis: "宾客"
  visual_intent:
    shot_type: "wide"
    composition: "rule_of_thirds"
    camera_angle: "eye_level"
    camera_movement: "static"
    style: "cinematic"
    lighting: "warm"
    atmosphere: "luxury"
    mood: "calm"

- shot_id: "C1-S1-shot3"
  camera:
    lens: "85mm"
    aperture: "f2.8"
    focus: "shallow"
  subject:
    type: "character"
    character_id: "shen_yan"
    face_id: "face_shenyan_v1"
    expression:
      - "composed_face"
      - "subtle_smirk"
    motion:
      - "still"
    gaze: "forward"
    pose: "standing"
  appearance:
    outfit_id: "shenyan_suit_v1"
    hair: "short_clean"
    accessories: []
  environment:
    location_id: "banquet_hall"
    props: ["champagne_glass"]
  continuity:
    previous_shot_id: "C1-S1-shot2"
    maintain:
      - "character"
      - "outfit"
      - "lighting"
    changes: []
  intent:
    narrative_function: "foreshadow"
    emphasis: "沈砚"
  visual_intent:
    shot_type: "close_up"
    composition: "centered"
    camera_angle: "eye_level"
    camera_movement: "static"
    style: "cinematic"
    lighting: "warm"
    atmosphere: "luxury"
    mood: "calm"
```
