# 小说元数据

控制 AI 写作行为的配置文件，包含小说基本信息和写作配置。

---

## 基本信息

- 小说名：{{novel_name}}
- 简介：{{synopsis}}
- 题材：{{genre}}
- 目标字数：{{target_words}}
- 目标章节：{{target_chapters}}
- 章节字数：{{chapter_words}}

---

## 写作配置

- 节奏类型：{{pace_type}}
- 叙事视角：{{narrative_perspective}}
- 写作风格：{{writing_style}}
- 目标读者：{{target_readers}}
- 更新频率：{{update_frequency}}
- 约束级别：{{constraint_level}}

---

## 约束优先级

当出现冲突时，必须按照以下优先级处理：

```
1. canon/*（世界规则 / 角色约束 / 剧情锁）   ← 最高
2. state/canon_ext.md（扩展设定）
3. state/arcs.md（剧情结构）
4. state/state.md（当前状态）
5. 本文件（写作配置）                        ← 最低
```

---

## 写作约束

> 以下为本小说的特定约束。通用写作规范见 agents/writer.md。

### 字数要求

按照基本信息中的章节字数执行，允许上下浮动 10%。

### 风格约束

根据写作配置中的风格设定调整叙事节奏：
- **爽文流**：保持快节奏，减少铺垫
- **正剧流**：可放慢节奏，深入刻画
- **轻松流**：保持轻松基调，可增加日常互动