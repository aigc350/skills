# revise 命令

修订指定章节。

## 命令格式

```
/novel-creator revise <章节号>
```

| 参数 | 说明 |
|------|------|
| `<章节号>` | 要修订的章节编号（必填） |

## 执行步骤

1. **备份原章节**
   - 将原章节文件复制到 `chapters/.backup/`
   - 文件名格式：`第{N}章_backup_{时间戳}.md`

2. **重置状态**
   - 从 `state/checkpoint.md` 读取该章节之前的状态
   - 或从 `state/summary.md` 重建状态

3. **调用 Writer Agent（作者）**
   - 读取 `agents/writer.md`
   - 使用重置后的状态重新生成章节

4. **调用 Editor Agent（编辑）**
   - 读取 `agents/editor.md`
   - 检查新章节质量
   - 不通过则返回 Writer 重写（最多 2 次）

5. **调用 Recorder Agent（记录员）**
   - 读取 `agents/recorder.md`
   - 更新 `state/state.md`
   - 更新 `state/memory.md`
   - 更新 `state/arcs.md`

6. **检查后续章节一致性**
   - 如有后续章节，提示用户是否需要重新生成

## 调用的 Agents

| Agent | 角色 | 职责 |
|-------|------|------|
| [writer.md](../agents/writer.md) | 作者 | 章节写作 |
| [editor.md](../agents/editor.md) | 编辑 | 质量检查 |
| [recorder.md](../agents/recorder.md) | 记录员 | 状态更新 |

## 示例

```
/novel-creator revise 21
/novel-creator revise 1
```

## 注意事项

- 修订章节可能导致后续章节出现不一致
- 建议修订后检查后续章节是否需要调整
- 备份文件保留在 `.backup/` 目录，可手动恢复