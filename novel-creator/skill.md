---
name: "novel-creator"
description: "AI-powered novel writing system for long-form fiction (1000+ chapters). Invoke when user wants to create novels, initialize novel projects, write chapters, manage story continuity, or use commands like init/run/status/plan/test."
---

# AI 自动小说创作系统

本系统用于构建一个可持续运行的 **AI 自动写小说系统**，支持长篇小说（1000+章节）创作。

## 系统目标

- 稳定长篇写作
- 避免 AI 遗忘剧情
- 保持角色与世界观一致
- 自动维护剧情进度
- 自动优化文本质量

---

# 命令说明

本 Skill 支持以下命令：

| 命令 | 作用 | 详细文档 |
|------|------|----------|
| `init` | 初始化项目 | [commands/init.md](commands/init.md) |
| `list` | 列出所有小说 | [commands/list.md](commands/list.md) |
| `switch <novel_id>` | 切换当前小说 | [commands/switch.md](commands/switch.md) |
| `run [n]` | 生成 n 章小说 | [commands/run.md](commands/run.md) |
| `status` | 查看状态 | [commands/status.md](commands/status.md) |
| `plan` | 手动规划 | [commands/plan.md](commands/plan.md) |
| `revise <章节号>` | 修订章节 | [commands/revise.md](commands/revise.md) |
| `export` | 导出小说 | [commands/export.md](commands/export.md) |
| `validate` | 校验一致性 | [commands/validate.md](commands/validate.md) |
| `test` | 自动化测试 | [commands/test.md](commands/test.md) |

## 命令路由

解析用户命令后，读取对应的命令文档执行：

```
用户输入: /novel-creator init
      ↓
读取: commands/init.md
      ↓
执行: init 命令流程
```

## 可用 Agents

| Agent | 角色 | 职责 | 调用场景 |
|-------|------|------|----------|
| [creator.md](agents/creator.md) | 创作者 | 生成设定 | init 命令 |
| [plotter.md](agents/plotter.md) | 编剧 | 章节规划 | run/plan 命令 |
| [writer.md](agents/writer.md) | 作者 | 章节写作 | run/revise 命令 |
| [editor.md](agents/editor.md) **opus** | 编辑 | 质量检查 | run/revise 命令 |
| [recorder.md](agents/recorder.md) | 记录员 | 状态记录 | run/revise 命令 |
| [archivist.md](agents/archivist.md) | 归档员 | 记忆归档 | 按需触发 |

> **注**：Editor 使用 opus 模型以获得更强的检查能力，其他 Agent 使用默认模型。

---

# 路径约定

## 多小说支持

本系统支持在同一工程中管理多部小说。

### 目录结构

```
project-root/
├── novels/                       # 小说集合目录
│   └── {novel_id}/              # 小说ID作为目录名
│       ├── novel/               # 小说内容目录
│       │   ├── canon/           # 固定设定（AI只读）- init 创建
│       │   ├── state/           # 运行状态（AI动态更新）- run 创建
│       │   ├── chapters/        # 小说正文 - run 创建
│       │   └── system/          # 系统文件 - run 创建
│       └── output/              # 导出目录 - export 创建
│           └── novel/           # 导出的小说文件
├── novel.config.md              # 小说项目配置
└── .claude/skills/...
```

> **目录创建时机**：
> - `init` 命令：只创建 `novel/canon/` 目录
> - `plan` 命令：创建 `novel/state/` 目录和 `chapter_plan.md`
> - `run` 命令：首次运行时创建完整 `novel/state/`、`novel/chapters/`、`novel/system/` 目录
> - `export` 命令：创建 `output/novel/` 目录

### 路径解析规则

1. 读取 `novel.config.md` 获取 `current_novel_id` 字段
2. 当前小说路径为 `novels/{current_novel_id}/novel/`
3. 如果 `novel.config.md` 不存在，使用默认路径 `novel/`（单小说模式）

### novel_id 命名规范

```
- 仅使用小写字母、数字、下划线
- 建议格式：{题材缩写}_{三位序号}
- 示例：xuanhuan_001, scifi_002, urban_003
```

| 题材 | 缩写建议 |
|------|----------|
| 玄幻 | xuanhuan |
| 科幻 | scifi |
| 都市 | urban |
| 历史 | history |
| 悬疑 | mystery |
| 其他 | other |

---

# 配置文件格式

## novel.config.md

**格式约束**：此文件格式固定，AI 生成时必须严格遵循，不可增减字段或改变结构。

```yaml
---
version: "1.0"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---

# 小说项目配置

## 当前小说

current_novel_id: {novel_id}

## 小说列表

| novel_id | name | genre | status | created |
|----------|------|-------|--------|---------|
| xuanhuan_001 | 小说名 | 玄幻 | 连载中 | 2026-03-20 |
```

**强制约束**：
- frontmatter 只含 `version`、`created`、`updated` 三个字段
- 正文只含 `## 当前小说` 和 `## 小说列表` 两个章节
- 表格列固定：`novel_id`、`name`、`genre`、`status`、`created`
- 不可添加额外字段、说明、注释

---

# 文件结构说明

## novel/canon/ - 固定设定（AI只读）

| 文件 | 说明 |
|------|------|
| `meta.md` | 小说元数据（信息、配置、写作规则） |
| `world.md` | 世界观设定 |
| `roles.md` | 角色设定 |
| `outline.md` | 故事主线 |

## novel/state/ - 运行状态（AI动态更新）

| 文件 | 说明 |
|------|------|
| `state.md` | 当前剧情快照 |
| `memory.md` | 剧情记忆（最近20章） |
| `summary.md` | 长期剧情总结 |
| `arcs.md` | 剧情弧线 |
| `chapter_plan.md` | 未来章节规划 |
| `canon_ext.md` | 扩展设定（新角色/势力/地点） |
| `checkpoint.md` | 运行检查点 |

## novel/chapters/ - 小说正文

| 目录/文件 | 说明 |
|-----------|------|
| `第{N}章_{标题}.md` | 章节文件 |
| `.backup/` | 章节备份目录 |

## novel/system/ - 系统文件

| 文件 | 说明 |
|------|------|
| `run_log.md` | 运行日志 |
| `error_log.md` | 异常日志 |

## output/novel/ - 导出文件

| 文件 | 说明 |
|------|------|
| `{书名}.md` | Markdown 格式全量导出 |
| `{书名}.txt` | TXT 格式全量导出 |
| `第{N}章_{标题}.md` | 增量导出章节文件 |
| `export_manifest.json` | 导出清单 |

---

# 约束优先级

当出现冲突时，按以下优先级处理：

```
1. canon/*               ← 最高
2. state/canon_ext.md
3. state/arcs.md
4. state/state.md
5. canon/meta.md         ← 最低
```

---

# 错误处理

| 异常场景 | 处理方式 |
|----------|----------|
| writer 输出与 canon 冲突 | 返回 writer 重写 |
| 重写超过 2 次仍不通过 | 暂停，记录 error_log |
| memory.md 超过大小上限 | 压缩到 summary.md |
| 系统崩溃/中断 | 从 checkpoint.md 恢复 |

---

# 使用示例

```
# 初始化第一部小说
/novel-creator init

# 初始化第二部小说（自动生成新ID）
/novel-creator init

# 列出所有小说
/novel-creator list

# 切换小说
/novel-creator switch scifi_002

# 生成一章
/novel-creator run

# 批量生成 10 章
/novel-creator run 10

# 持续运行到完成
/novel-creator run --continuous

# 查看状态
/novel-creator status

# 修订第 21 章
/novel-creator revise 21

# 导出小说
/novel-creator export

# 增量导出第 1-50 章
/novel-creator export --start 1 --end 50

# 执行自动化测试
/novel-creator test
```