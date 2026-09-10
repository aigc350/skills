# Memory Updater Agent

## Type
Tool Wrapper

## Role
更新三层记忆系统。

## Description
维护三层记忆系统：小说记忆（人物、剧情）、剧本记忆（连续性）、审查记忆（质量历史）。在 pipeline 的不同阶段调用。

---

## 记忆层

### 小说记忆 (Novel Memory)
- `characters.yaml` - 人物特征、关系
- `plot_state.yaml` - 剧情状态、谜题、伏笔

### 剧本记忆 (Script Memory)
- `script_state.yaml` - 角色位置、连续性

### 审查记忆 (Reviewer Memory)
- `review_log.yaml` - 评分历史、模式

---

## 更新任务

### 更新小说记忆

**触发时机**：场景提取之后（Step 3）

**任务**：基于提取的场景更新人物特征、关系、剧情状态。

**输入**：
- 场景数据 (`runtime/scenes_${chapter_name}.yaml`)
- 现有 `characters.yaml`
- 现有 `plot_state.yaml`

**输出**：
- 更新的 `characters.yaml`
- 更新的 `plot_state.yaml`

**模板**：
- [templates/memory/characters.yaml](../templates/memory/characters.yaml)
- [templates/memory/plot_state.yaml](../templates/memory/plot_state.yaml)

**为何此顺序**：场景提取后才更新小说记忆，因为：
1. 场景提取先分析章节内容
2. 记忆更新需要结构化场景数据
3. 剧本写作使用更新后的记忆

**增长限制**（防止膨胀）：

| 记忆文件 | 字段 | 限制 | 策略 |
|---------|------|------|------|
| characters.yaml | characters | 最多30 | 保留主要+活跃，归档次要 |
| plot_state.yaml | timeline | 最多20 | 保留最近章节 |
| plot_state.yaml | active_mysteries | 最多5 | 归档已解开的谜题 |
| plot_state.yaml | open_loops | 最多10 | 关闭已解决的伏笔 |

---

### 更新剧本记忆

**触发时机**：剧本定稿之后（Step 9）

**任务**：更新角色位置、场景状态、连续性数据。

**输入**：
- 定稿剧本
- 现有 `script_state.yaml`

**输出**：
- 更新的 `script_state.yaml`

**模板**：[templates/memory/script_state.yaml](../templates/memory/script_state.yaml)

**增长限制**：

| 字段 | 限制 | 策略 |
|------|------|------|
| `continuity_notes` | 最多10 | 保留最新，丢弃最旧 |
| `pending_hooks` | 最多5 | 移除已解决，保留未解决 |
| `character_positions` | 最多10 | 保留主要角色+最近活跃 |

---

### 更新审查记忆

**触发时机**：审查完成后（Step 10）

**任务**：记录审查分数，识别模式，跟踪改进。

**输入**：
- 审查结果
- 现有 `review_log.yaml`

**输出**：
- 更新的 `review_log.yaml`

**模板**：[templates/memory/review_log.yaml](../templates/memory/review_log.yaml)

**增长限制**：

| 字段 | 限制 | 策略 |
|------|------|------|
| `history` | 最多20 | 保留最近审查 |
| `recurring_issues` | 最多5 | 保留最频繁问题 |
| `quality_trend` | 最多10 | 保留最近10集 |

---

## 更新触发时机

| 记忆 | 触发 | Pipeline Step |
|------|------|-------------|
| Novel | 场景提取后 | Step 3 |
| Script | 剧本定前后 | Step 9 |
| Reviewer | 审查完成后 | Step 10 |

---

## 核心原则

1. **从不重建** - 始终追加/更新
2. **跟踪变化** - 添加时间戳
3. **保持一致性** - 交叉引用其他记忆层
4. **保留历史** - 不删除，需要时归档

---

## 质量检查清单

- [ ] 新角色添加了完整特征
- [ ] 剧情状态反映当前章节
- [ ] 连续性数据与剧本匹配
- [ ] 审查日志显示分数趋势
