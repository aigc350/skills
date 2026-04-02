# Load Assets Agent v1.0（跨章节资产加载器）

> ⚠️ **MUST READ**: [Common Rules](../references/rules/common.rule.md)
>
> Stage: `load_assets` | Permission: 只读（不修改任何 prompt 内容）
>
> ⭐ **执行时机**：Enhancer 之后、Asset Builder 之前（关键顺序约束）

---

## 🧠 Role

将输入：

* asset_registry.yaml（全局资产注册表）

输出：

* reusable_assets.yaml（可复用资产清单 + 需新建资产清单）

---

## 🎯 Core Objective

从全局资产注册表中提取可复用资产，为 Asset Builder 提供"先查再建"的数据基础，避免重复创建已有资产。

---

## ⚙️ Core Principles

### 1️⃣ Registry First（注册表优先）

所有复用判断必须基于 asset_registry.yaml 中的数据，不允许猜测。

### 2️⃣ Approved Only（只复用已验证的资产）

只有 `generation_status.image = "approved"` 且 `locked = true` 的资产才可被复用。

### 3️⃣ Exact Match First（精确匹配优先）

复用判断优先级：`character_id + variant_id` 完全匹配 > `character_id` 身份匹配 > 全新创建。

---

## 📥 Input

```yaml
input:
  - {memory_dir}/asset_registry.yaml    # 全局资产注册表
  - {runtime_dir}/prompt_ir.yaml        # 当前章节的 IR（用于判断需要什么资产）
```

---

## 📤 Output

```yaml
output:
  - {runtime_dir}/reusable_assets.yaml  # 可复用 + 需新建清单
```

---

## 🔁 Processing Pipeline

```text
Step 1: 读取 asset_registry.yaml
Step 2: 提取所有已验证可复用的资产
Step 3: 对照 prompt_ir.yaml 判断哪些资产可复用
Step 4: 输出 reusable_assets.yaml
```

---

## 📋 详细处理规则

### Step 1：读取注册表

```yaml
读取: {memory_dir}/asset_registry.yaml

IF 文件不存在:
  → 输出空的 reusable_assets.yaml（首次运行）
  → 标记 loaded = false

IF 文件存在但格式错误:
  → 报错，中断 Pipeline
```

---

### Step 2：提取可复用资产

```text
FOR each asset in asset_registry:

  # ===== 角色资产 =====
  IF asset 是 character 类型:
    IF generation_status.image == "approved" AND locked == true:
      → 加入 reusable.characters

  # ===== 场景资产 =====
  IF asset 是 location 类型:
    IF generation_status.image == "approved":
      → 加入 reusable.locations

  # ===== 物品资产 =====
  IF asset 是 object 类型:
    IF generation_status.image == "approved":
      → 加入 reusable.objects
```

---

### Step 3：对照 IR 判断复用

```text
FOR each shot in prompt_ir.yaml:

  # ===== 角色判断 =====
  FOR each character in shot.subject.characters:

    查找 reusable.characters 中是否存在:
      - character_id == IR.character_id
      - variant_id == IR.variant_id

    IF 完全匹配（character_id + variant_id）:
      → 标记 source = "reused"
      → 记录 asset_id 和 reference_image

    ELSE IF 身份匹配（character_id 存在但 variant_id 不同）:
      → 标记 source = "derived"
      → 记录可继承的 base_prompt 和 reference_image

    ELSE:
      → 标记 source = "new_needed"
      → 加入 new_needed.characters

  # ===== 场景判断 =====
  FOR shot.location:
    查找 reusable.locations 中是否存在:
      - location_id == IR.location.location_id

    IF 存在:
      → 标记 source = "reused"
    ELSE:
      → 标记 source = "new_needed"

  # ===== 物品判断 =====
  FOR each object in shot.location.objects:
    查找 reusable.objects 中是否存在:
      - object_id == IR.object.object_id

    IF 存在:
      → 标记 source = "reused"
    ELSE:
      → 标记 source = "new_needed"
```

---

### Step 4：输出 reusable_assets.yaml

```yaml
# ===== 输出结构 =====
chapter_id: string            # 当前章节 ID
loaded_from: string           # 来源文件路径
loaded_at: string             # 加载时间

# ===== 可复用资产 =====
reusable:
  characters:
    - character_id: string
      variants:
        - variant_id: string
          asset_id: string
          reference_image: string     # 参考图路径
          appearance_fingerprint: []  # 外观指纹
          generation_status: string   # "approved"
          source: string              # "reused" / "derived"

  locations:
    - location_id: string
      variants:
        - variant_id: string
          asset_id: string
          reference_image: string
          anchors: []                 # 场景锚点
          generation_status: string

  objects:
    - object_id: string
      variants:
        - variant_id: string
          asset_id: string
          generation_status: string

# ===== 需要新建的资产 =====
new_needed:
  characters:
    - character_id: string
      variant_id: string
      reason: string                  # "首次出场" / "新服装"

  locations:
    - location_id: string
      reason: string                  # "新场景"

  objects:
    - object_id: string
      reason: string                  # "首次出现" / "状态变化"
```

---

## 📤 Output Schema

输出必须符合 `references/schemas/reusable_assets.yaml` 定义。

---

## 🚫 Anti-Patterns

❌ 不修改 asset_registry.yaml（只读取）
❌ 不生成任何 prompt 文本（只做资产查找）
❌ 不判断 asset_id 的上下文拆分（由 Asset Builder 决定）
❌ 不跳过 IR 对照直接标记复用

---

## 🔧 扩展性设计

### 新增资产类型

当需要支持新的资产类型（如音乐、音效）时：
1. 在 asset_registry.yaml 中新增类型分区
2. 在 Step 2 中新增提取逻辑
3. 在 Step 3 中新增对照逻辑
4. 在输出结构中新增对应分区

### 首次运行处理

```yaml
# 首次运行时 asset_registry.yaml 不存在
# 输出空的 reusable_assets.yaml：
chapter_id: "1"
loaded_from: null
reusable:
  characters: []
  locations: []
  objects: []
new_needed: []  # 由 Asset Builder 填充
```

---

## 🧩 Final Note

> Load Assets 的本质是：
>
> 👉 **跨章节资产查找器（不是资产创建器）**
>
> ⭐ 它必须在 Asset Builder 之前执行，否则 Asset Builder 无法判断哪些资产可以复用，会导致重复创建已有资产，破坏跨章节一致性。
