# plan 命令

手动触发章节规划，创建或更新 `state/chapter_plan.md`。

## 命令格式

```
/novel-creator plan
```

## 执行步骤

### Step 1: 检查并创建目录结构

如果 `state/` 目录不存在，创建以下结构：
```
novels/{novel_id}/novel/
├── state/
│   └── chapter_plan.md    ← plan 命令创建
└── chapters/
    └── .backup/
```

### Step 2: 调用 Plotter Agent

调用 `agents/plotter.md`（编剧），传入以下上下文：

**必须加载**：
- `canon/outline.md` - 故事主线
- `canon/meta.md` - 节奏类型
- `canon/world.md` - 世界观设定
- `canon/roles.md` - 角色设定

**按需加载**（如果存在）：
- `state/state.md` - 当前状态
- `state/arcs.md` - 剧情弧线

### Step 3: 生成章节规划

Plotter Agent 生成未来 5-10 章规划，写入 `state/chapter_plan.md`。

## 调用的 Agent

| Agent | 角色 | 职责 |
|-------|------|------|
| [plotter.md](../agents/plotter.md) | 编剧 | 章节规划、节奏控制 |

## 输出

创建或更新 `state/chapter_plan.md`，包含未来 5-10 章的规划。

## 注意事项

- plan 命令应在 init 之后、run 之前执行
- 可多次执行以更新规划
- 规划基于当前 canon 设定生成，修改 canon 后应重新 plan