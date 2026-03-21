# export 命令

导出已完成章节。

## 命令格式

```
/novel-creator export [--format <format>] [--start <n>] [--end <n>]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--format` | md | 导出格式（md/txt/epub） |
| `--start` | 1 | 起始章节 |
| `--end` | 最新 | 结束章节 |

## 执行步骤

1. 读取 `chapters/` 下所有章节
2. 按章节号排序
3. 根据参数筛选章节范围
4. 合并为指定格式
5. 输出到小说目录下

## 输出路径

```
novels/{小说ID}/
├── {书名}.md              # 默认导出（Markdown 格式）
├── {书名}.txt             # TXT 格式导出
└── {书名}.epub            # EPUB 格式导出
```

**示例**：
```
novels/other_007/
└── 我曾拒绝变成他们.md    # 导出文件
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

## 示例

```
/novel-creator export                           # 导出全部为 Markdown
/novel-creator export --format txt              # 导出全部为 txt
/novel-creator export --format epub             # 导出全部为 epub
/novel-creator export --start 1 --end 100       # 导出第 1-100 章
```