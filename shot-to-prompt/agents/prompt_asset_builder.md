# Asset Prompt Builder v3.0 (Cross-Chapter Reuse Enabled)

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `asset` | Generates: prompt_asset.yaml + updates asset_registry.yaml
>
> ⭐ v0.4 升级：新增跨章节复用判断逻辑（依赖 reusable_assets.yaml）

---

## 🧠 Role

从 `prompt_ir.yaml` 中解析：

* character_id（身份）- 来自 IR
* variant_id（状态）- 来自 IR

**生成**：

* asset_id（视觉资产 ID）- **由本阶段决定**

输出：

* `prompt_asset.yaml`
  并维护：
* `asset_registry.yaml`（全局资产库）

---

## 🎯 Core Objective

构建一个：

* 可复用（reuse）- 跨章节完全复用已有资产
* 可派生（derive）- 继承身份创建新变体
* 可版本控制（versioning）
* 可锁定（locking）

的视觉资产系统，确保跨章节角色/场景/物品的一致性。

---

---

# ⚙️ Core Principles

---

## 1️⃣ Three-Layer Mapping

```text
IR 输出                  Asset Builder 输出
─────────────────────    ─────────────────────
character_id: shen_yan   → base_prompt（身份）
variant_id: work_v1      → variant_prompt（状态）
                         → asset_id: shen_yan_work_v1（资产）
```

**关键**：asset_id 由 asset_builder 决定，不是 IR。

---

## 2️⃣ Asset = Base + Variant

asset_prompt = base_prompt + variant_prompt

---

## 3️⃣ asset_id 生成规则

**默认规则**：
```yaml
asset_id = variant_id
```

**拆分规则**（根据上下文）：
```yaml
# 当需要区分同一服饰的不同场景时
variant_id: shenyan_work_clothes_v1
context:
  lighting: night
  scene: office
    → asset_id: shenyan_work_clothes_v1_night_office
```

**何时拆分**：

| 条件 | 是否拆分 |
|------|----------|
| 同一服饰，不同光照（day/night） | ✅ 可拆分 |
| 同一服饰，不同场景（office/outdoor） | ✅ 可拆分 |
| 同一服饰，同一环境 | ❌ 不拆分 |

---

## 4️⃣ Registry First（最重要）

在生成前必须：

* 查询 reusable_assets.yaml（⭐ v0.4 新增）
* 查询 registry
* 决定复用 / 派生 / 新建

---

## 5️⃣ ⭐ v0.4 新增：Cross-Chapter Reuse（跨章节复用）

**核心逻辑**：先查 reusable_assets.yaml，再决定是否新建。

```text
三种来源：
  source = "reused"     → 完全复用已有资产（不新建）
  source = "derived"    → 派生变体（继承身份，新建变体）
  source = "generated"  → 全新创建
```

---

---

# 📥 Input

```yaml
prompt_ir.yaml                # IR 层输出
prompt_canonical.yaml          # Canonical 层输出
reusable_assets.yaml           # ⭐ v0.4 新增：来自 Load Assets 阶段
asset_registry.yaml            # 全局资产注册表（memory 目录）
```

---

---

# 📦 Registry

```yaml
memory/asset_registry.yaml
```

---

---

# 🔁 Processing Pipeline

---

## Step 1️⃣ 收集输入

从 IR 收集：

```yaml
character_id: shen_yan        # 身份 ID
variant_id: shenyan_work_v1   # 变体 ID
face_id: shenyan_male_v1      # 面部 ID
appearance:                   # 外观信息
  outfit: "工作服"
  accessories: ["watch"]
```

**注意**：IR 不提供 asset_id，由本阶段生成。

---

## Step 2️⃣ ⭐ 复用判断（v0.4 核心升级）

### 2.1 角色复用判断

```text
FOR each character in prompt_ir.subject.characters:

  查找 reusable_assets.reusable.characters:
    IF character_id + variant_id 都匹配:
      → source = "reused"
      → 复用 asset_id（不新建）
      → 复用 reference_image（如有）
      → 复用 appearance_fingerprint（如有）
      → 跳过后续步骤，直接输出

    ELSE IF character_id 匹配但 variant_id 不同:
      → source = "derived"
      → 继承 base_prompt（身份不变）
      → 继承 reference.face_image（面部可用）
      → 创建新 variant_prompt
      → 生成新 asset_id

    ELSE:
      → source = "generated"
      → 全新创建
```

### 2.2 场景复用判断

```text
FOR each location in prompt_ir.locations:

  查找 reusable_assets.reusable.locations:
    IF location_id + variant_id 匹配:
      → source = "reused"
      → 复用 asset_id + anchors + reference_image

    ELSE:
      → source = "generated"
      → 全新创建
```

### 2.3 物品复用判断

```text
FOR each object in prompt_ir.locations[].objects:

  查找 reusable_assets.reusable.objects:
    IF object_id 匹配 AND object_state 匹配:
      → source = "reused"

    ELSE IF object_id 匹配但 object_state 不同:
      → source = "derived"
      → 创建新 variant（如 ring_1_intact_v1 → ring_1_broken_v1）

    ELSE:
      → source = "generated"
```

---

## Step 3️⃣ 决定 asset_id（仅 source != "reused" 时执行）

### 3.1 默认情况

```yaml
asset_id = variant_id
```

### 3.2 需要拆分时

```yaml
# 判断逻辑
IF context.lighting == "night" AND registry.has(variant_id + "_night"):
    asset_id = variant_id + "_night"
ELSE:
    asset_id = variant_id
```

### 3.3 查询 Registry 二次确认

```text
情况 A：registry 中存在 + locked = true
  → 直接复用（即使 reusable_assets 没标记）

情况 B：registry 中存在 + locked = false
  → 对比 prompt：
     IF 相同 → 复用
     IF 不同 → version +1，更新 registry

情况 C：registry 中不存在
  → 新建 asset（source = "generated"）
```

---

## Step 4️⃣ 构建 Base Prompt（仅 source != "reused" 时执行）

来源：

* appearance（face / hair）
* traits
* visual_keywords

规则：

* ❌ 去 emotion
* ❌ 去动作
* ✔ 强化 identity

**derived 时**：继承已有 base_prompt，只更新 variant 部分。

---

## Step 5️⃣ 构建 Variant Prompt（仅 source != "reused" 时执行）

来源：

* outfit
* accessories
* variant_id 语义

---

## Step 6️⃣ 合成 Final Prompt（仅 source != "reused" 时执行）

```text
base + variant + cinematic + high detail + consistency
```

---

## Step 7️⃣ ⭐ 写回 Registry（v0.4 增强）

### 7.1 新建资产时写入

```yaml
characters:
  {asset_id}:
    character_id: string
    variant_id: string
    asset_id: string
    base_prompt: string
    variant_prompt: string
    final_prompt: string
    negative_prompt: string

    # v0.4 新增字段
    source: "generated" | "derived"
    version: 1
    locked: false

    reference:                        # 初始为空，由 prompt-to-video 回写
      face_image: null
      seed: null

    appearance_fingerprint: []        # Asset Builder 生成
      # 从 base_prompt 提取的关键特征
      # 示例: ["short_black_hair", "dark_suit", "calm_face"]

    generation_status:
      image: "pending"                # 等待 prompt-to-video 生成
      video_count: 0
      last_used: null

    used_in_chapters: []
    used_in_shots: []
```

### 7.2 复用资产时不写入

```text
IF source == "reused":
  → 不修改 registry（资产已存在且 locked）
  → 直接输出已有信息
```

### 7.3 派生资产时写入

```text
IF source == "derived":
  → 创建新条目（新 asset_id）
  → 继承 reference.face_image（面部图可复用）
  → 标记 source = "derived"
  → 初始化 generation_status.image = "pending"
```

---

## Step 8️⃣ 输出 prompt_asset.yaml

```yaml
characters:
  - character_id: string
    asset_id: string
    variant_id: string
    version: integer
    locked: boolean
    source: string              # "reused" / "derived" / "generated"
    base_prompt: string
    variant_prompt: string
    final_prompt: string
    negative_prompt: string

    # v0.4 新增
    reference:
      face_image: string | null
    appearance_fingerprint: string[]

locations:
  - location_id: string
    asset_id: string
    variant_id: string
    source: string
    final_prompt: string
    anchors: string[]

props:
  - prop_id: string
    asset_id: string
    final_prompt: string

objects:
  - object_id: string
    asset_id: string
    state: string
    holder: string | null
    source: string
```

---

---

# 🚫 Anti-Patterns

---

❌ 每次重复生成 asset（应该先查 reusable_assets.yaml）
❌ variant 写进 base（身份和变体必须分离）
❌ 输出动作 / 镜头（这些由其他阶段处理）
❌ 修改已有 locked 资产的 base_prompt（身份不可变）
❌ 忽略 reusable_assets.yaml 直接新建（破坏跨章节一致性）

---

---

# 🧩 Final Note

---

> Asset Builder v3.0 的核心升级：
>
> 👉 **从"每次新建"升级为"先查再建"**
>
> 通过 reusable_assets.yaml 实现跨章节资产复用，确保：
> - 第 1 章创建的角色，第 2 章能直接复用
> - 角色 variant 变化时，身份（base）保持不变
> - 物品状态变化时，创建新 variant 而非覆盖
