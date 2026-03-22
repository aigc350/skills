---
name: "record"
description: "记录与 Claude Code 的对话，分析思考过程并归类形成习惯模式，最终生成可导入的课程格式。当用户想要保存有价值的对话、记录交互过程、或回顾学习内容时触发此技能。触发词：record、记录、保存对话、学习记录。"
---

# 对话记录与学习系统

将您与 Claude Code 的对话进行记录、分析、归类，形成个人习惯模式，最终可转化为课程。

## 触发命令

```
/record              # 记录当前对话
/record --category <类别>  # 指定分类记录
/record --review     # 回顾最近记录
```

## 工作流程

### 步骤 1：对话采集

首先，收集当前会话的关键对话内容：

1. **识别关键交互** - 回顾本次会话，找出：
   - 用户提出的核心问题/任务
   - Claude 的解决思路和方法
   - 关键的决策点和转折
   - 最终达成的成果

2. **确认记录范围** - 向用户确认：
   ```
   📝 我识别到以下关键对话片段：
   1. [片段摘要1]
   2. [片段摘要2]
   ...

   确认记录这些内容？(y/n)
   或指定具体范围（如：只记录第2-5轮对话）
   ```

### 步骤 2：思考过程分析

深入分析对话中的思维模式：

**分析维度：**

| 维度 | 分析内容 |
|------|----------|
| 问题定义 | 用户如何描述问题？关键词是什么？ |
| 思考路径 | 从问题到解决方案经历了哪些步骤？ |
| 决策节点 | 哪些地方需要做出选择？依据是什么？ |
| 试错过程 | 遇到什么障碍？如何克服？ |
| 知识迁移 | 用到了哪些已有知识/经验？ |
| 模式提炼 | 是否形成了可复用的模式？ |

**输出分析报告：**
```markdown
## 思考过程分析

### 问题定义
[用户如何理解和描述问题]

### 思考路径
1. [步骤1]
2. [步骤2]
3. [步骤3]

### 关键决策
- 决策点1: [描述] → 选择: [结果] → 理由: [原因]
- 决策点2: ...

### 经验提炼
[可复用的经验或模式]
```

### 步骤 3：归类整理

按技能领域归类存储：

**分类体系：**

```
learning/
├── records/                    # 原始记录（按时间）
│   └── 2026-03-22_xxx.md
│
├── categories/                 # 分类汇总
│   ├── programming/           # 编程相关
│   │   ├── debugging.md       # 调试技巧
│   │   ├── refactoring.md     # 重构方法
│   │   └── architecture.md    # 架构设计
│   │
│   ├── workflow/              # 工作流程
│   │   ├── git-workflow.md    # Git 操作
│   │   └── task-management.md # 任务管理
│   │
│   ├── writing/               # 写作相关
│   │   ├── prompt-engineering.md
│   │   └── documentation.md
│   │
│   ├── thinking/              # 思维方法
│   │   ├── problem-solving.md
│   │   └── decision-making.md
│   │
│   └── tools/                 # 工具使用
│       ├── claude-code.md
│       └── other-tools.md
│
├── patterns/                   # 习惯模式库
│   ├── coding-patterns.md     # 编程习惯
│   ├── thinking-patterns.md   # 思维习惯
│   └── workflow-patterns.md   # 工作习惯
│
├── courses/                    # 课程输出
│   └── course-templates/
│
└── index.json                  # 全局索引
```

**自动归类逻辑：**

根据对话内容关键词自动判断类别：

| 关键词示例 | 归类 |
|-----------|------|
| bug, error, 调试, 修复 | programming/debugging |
| 重构, 优化, refactor | programming/refactoring |
| git, commit, push, auto-git | workflow/git-workflow |
| prompt, 提示词, 指令 | writing/prompt-engineering |
| 分析, 思考, 决策 | thinking/problem-solving |

**用户确认归类：**
```
📂 建议归类到: programming/debugging

确认？或选择其他分类：
1. 确认
2. 改为其他分类（请输入）
```

### 步骤 4：模式提炼

识别并记录用户的习惯模式：

**模式记录格式：**

```markdown
## [模式名称]

### 触发场景
[什么情况下会用到这个模式]

### 行为特征
1. [特征1]
2. [特征2]

### 典型案例
[链接到具体记录]

### 进化轨迹
| 时间 | 变化 |
|------|------|
| 2026-03-22 | 初次记录 |
| ... | ... |
```

**模式类型：**

1. **编程习惯模式**
   - 命名风格偏好
   - 错误处理习惯
   - 代码组织方式

2. **思考习惯模式**
   - 问题分解方式
   - 决策依据偏好
   - 验证思路习惯

3. **工作流习惯模式**
   - 任务启动方式
   - 检查点设置
   - 收尾确认流程

### 步骤 5：生成输出

同时生成 Markdown 和 JSON 两种格式：

**Markdown 输出** (人类可读):

```markdown
# [记录标题]

> 记录时间: 2026-03-22
> 分类: programming/debugging
> 标签: #git #workflow #automation

## 背景
[问题/任务背景]

## 对话精华

### 用户意图
[用户想要做什么]

### 思考过程
[分析后的思考路径]

### 解决方案
[最终方案]

### 经验总结
[可复用的经验]

## 相关记录
- [[2026-03-21-xxx]] 相关记录1
- [[2026-03-20-xxx]] 相关记录2
```

**JSON 输出** (程序可处理):

```json
{
  "id": "rec-20260322-001",
  "title": "auto-git 流程优化",
  "timestamp": "2026-03-22T11:30:00Z",
  "category": "programming/workflow",
  "tags": ["git", "workflow", "automation"],
  "summary": {
    "intent": "优化 auto-git 技能的工作流程",
    "problem": "使用 cd 切换目录会导致后续找不到配置文件",
    "solution": "改用 git -C 参数指定路径",
    "outcome": "success"
  },
  "thinking_process": {
    "problem_definition": "...",
    "steps": [...],
    "decisions": [...],
    "lessons_learned": [...]
  },
  "patterns_identified": ["prefer-non-destructive-approach"],
  "related_records": ["rec-20260322-000"],
  "course_potential": true
}
```

---

## 目录结构初始化

首次使用时，创建 learning 目录结构：

```bash
mkdir -p learning/{records,categories/{programming,workflow,writing,thinking,tools},patterns,courses/course-templates}
```

并创建初始索引文件 `learning/index.json`：

```json
{
  "version": "1.0",
  "created": "2026-03-22",
  "stats": {
    "total_records": 0,
    "categories": {
      "programming": 0,
      "workflow": 0,
      "writing": 0,
      "thinking": 0,
      "tools": 0
    }
  },
  "recent_records": [],
  "frequent_tags": {}
}
```

---

## 索引维护

每次记录后更新 `index.json`：

```json
{
  "version": "1.0",
  "updated": "2026-03-22T11:30:00Z",
  "stats": {
    "total_records": 5,
    "categories": {
      "programming": 3,
      "workflow": 2,
      "writing": 0,
      "thinking": 0,
      "tools": 0
    }
  },
  "recent_records": [
    {"id": "rec-20260322-005", "title": "...", "category": "..."},
    {"id": "rec-20260322-004", "title": "...", "category": "..."}
  ],
  "frequent_tags": {
    "git": 3,
    "workflow": 2,
    "automation": 2
  }
}
```

---

## 课程生成

当积累足够记录后，可生成课程：

### 课程模板

```markdown
# 课程：[课程名称]

## 课程概述
- 目标学员：
- 预计时长：
- 前置知识：

## 学习目标
1. [目标1]
2. [目标2]

## 课程内容

### 第一章：[章节名]
> 来源：记录 xxx, xxx

**知识点**
- [要点1]
- [要点2]

**实践案例**
[来自实际对话的案例]

**练习**
[基于案例设计的练习]

---

### 第二章：[章节名]
...

## 附录
- 相关记录链接
- 参考资料
```

### 生成命令

```
/record --generate-course <分类>
```

系统会：
1. 汇总该分类下的所有记录
2. 提取共性知识点
3. 按逻辑顺序组织章节
4. 生成课程文档

---

## 注意事项

1. **隐私保护** - 记录前确认不包含敏感信息（密码、密钥等）
2. **去重合并** - 相似内容建议合并而非重复记录
3. **定期回顾** - 建议每周回顾一次，更新模式库
4. **持续优化** - 分类体系和模式库应随使用不断演进