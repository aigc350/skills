# export 命令

导出已完成章节，支持全量导出和增量导出。

## 命令格式

```
/novel-creator export [--format <format>] [--start <n>] [--end <n>]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--format` | md | 导出格式（md/txt/epub） |
| `--start` | 1 | 起始章节 |
| `--end` | 最新 | 结束章节 |

## 导出模式

| 命令 | 模式 | 说明 |
|------|------|------|
| `export` | 全量导出 | 合并所有章节为一个文件 |
| `export --start N --end M` | 增量导出 | 按章节范围逐章输出 |

**规则**：
- 无参数：全量导出所有章节
- 有 `--start` 或 `--end`：增量导出指定范围

## 执行步骤

### 全量导出

1. 读取 `novel/chapters/` 下所有章节
2. 按章节号排序
3. 合并为指定格式
4. 输出到 `output/novel/{书名}.md`

### 增量导出

1. 读取 `novel/chapters/` 下指定范围章节
2. 按章节号排序
3. **检查文件是否需要更新**：
   - 对比源文件与目标文件的修改时间
   - 如果目标文件不存在 → 导出
   - 如果源文件更新时间 > 目标文件更新时间 → 导出
   - 如果源文件更新时间 ≤ 目标文件更新时间 → 跳过（内容未变化）
4. 逐章输出到 `output/novel/` 目录
5. 更新导出清单 `export_manifest.json`

## 输出路径

```
novels/{novel_id}/
└── output/
    └── novel/                    # 导出目录
        ├── {书名}.md              # 全量导出（Markdown 格式）
        ├── {书名}.txt             # 全量导出（TXT 格式）
        ├── {书名}.epub            # 全量导出（EPUB 格式）
        ├── 第001章_{标题}.md      # 增量导出章节文件
        ├── 第002章_{标题}.md
        └── export_manifest.json   # 导出清单
```

**示例**：
```
novels/other_009/
└── output/
    └── novel/
        ├── 我曾拒绝变成他们.md    # 全量导出
        ├── 第1章_逃离.md          # 增量导出
        ├── 第2章_城市.md
        └── export_manifest.json
```

## 导出清单格式

`export_manifest.json` 记录增量导出状态：

```json
{
  "novel_id": "other_009",
  "novel_name": "我曾拒绝变成他们",
  "last_export": "2026-03-23T12:00:00Z",
  "total_chapters": 11,
  "exported_chapters": [1, 2, 3],
  "format": "md"
}
```

## 输出格式

### Markdown 格式（默认）

```markdown
# {书名}

---

## 第1章：{章节标题}

{章节内容}

---

## 第2章：{章节标题}

{章节内容}
```

### TXT 格式

```
第一章 章节标题

章节内容...

第二章 章节标题

章节内容...
```

### EPUB 格式

- 自动生成目录
- 按卷/章节分组
- 支持元数据（书名、作者等）

## 增量导出用途

- 外部编辑器查看单章
- 部分章节审核/修改
- 与其他系统集成
- 断点续导（只导出新章节/有变化的章节）

## 增量导出优化

增量导出会自动跳过未变化的章节：

| 情况 | 处理 |
|------|------|
| 目标文件不存在 | 导出 |
| 源文件有更新 | 导出 |
| 源文件未变化 | 跳过 |

**判断依据**：对比源文件（`novel/chapters/`）与目标文件（`output/novel/`）的修改时间。

## 示例

```
/novel-creator export                           # 全量导出所有章节
/novel-creator export --format txt              # 全量导出为 TXT
/novel-creator export --format epub             # 全量导出为 EPUB
/novel-creator export --start 1 --end 50        # 增量导出第 1-50 章
/novel-creator export --start 51                # 增量导出第 51 章起
/novel-creator export --start 1 --end 1         # 增量导出第 1 章
```