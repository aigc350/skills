---
name: "auto-git"
description: "自动化 Git 工作流 - 自动分析代码改动、生成简洁中文提交信息、执行 add → commit → push 完整流程。支持检查远程状态、避免冲突。需要手动触发 /auto-git 命令。"
---

# Auto-Git 自动化 Git 工作流

本技能自动化日常 Git 操作，简化开发流程。

## 主流程入口

执行 `/auto-git` 时，按以下顺序处理：

### 第一步：检查 git-config.md

检查当前工程根目录是否存在 `git-config.md`：

```bash
ls -la git-config.md 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
```

**如果文件存在：**
→ **立即使用 Read 工具读取配置文件**
→ 提取仓库路径（从 `- **仓库路径**：` 行提取）
→ 使用 `git -C <仓库路径>` 执行所有 Git 操作
→ 跳转到 [工作流程](#工作流程) 章节执行 Git 操作

**如果文件不存在（首次使用）：**
→ 跳转到 [首次使用 - 初始化配置](#首次使用---初始化配置) 章节

---

## 已有配置时的执行步骤

当 `git-config.md` 存在时，**必须严格按以下步骤执行**：

### 步骤 1：读取配置文件

**使用 Read 工具**读取 `git-config.md`，解析以下内容：

```
- **仓库路径**：`D:\kevin\source\my-project`  ← 从此行提取
```

以及配置表中的：
- user.name
- user.email
- remote.origin

### 步骤 2：显示配置摘要

```
📖 读取到配置：
   仓库路径：D:\kevin\source\my-project
   用户名：YourName
   邮箱：your.email@gmail.com
   远程仓库：https://github.com/username/repo.git
```

### 步骤 3：验证仓库路径

**关键步骤**：使用 `git -C` 验证仓库路径是否有效：

```bash
git -C <从配置提取的仓库路径> status
```

如果目录不存在或不是 Git 仓库：
```
❌ 配置的仓库路径不存在或不是 Git 仓库：<path>
请检查 git-config.md 中的配置是否正确，或删除该文件重新初始化。
```

### 步骤 4：执行 Git 工作流

验证通过后，继续执行 [工作流程](#工作流程) 章节。

**重要**：所有 Git 命令都使用 `git -C <仓库路径>` 格式，无需切换目录。

---

## 首次使用 - 初始化配置

当检测不到 `git-config.md` 时，引导用户完成初始化。

### 1.1 确定 Git 仓库路径

首先确定要操作的 Git 仓库路径：

```
📁 当前工作目录：{current_working_directory}
```

如果用户想指定其他路径，可以使用参数：
- `/auto-git /path/to/repo` - 指定 Git 仓库路径
- `/auto-git D:/my-project` - 指定 Windows 路径示例

获取用户指定的路径后，转换为完整路径：
```bash
# Windows 示例
realpath "D:/my-project"
# 或 pwd -W 处理 Windows 路径
```

### 1.2 检查 Git 仓库是否存在

检查指定路径是否为有效的 Git 仓库：

```bash
git -C <repo-path> status
```

如果目录不是 Git 仓库，提示用户：
```
❌ 目录 <full-path> 不是 Git 仓库
是否要在该目录初始化 Git 仓库？(y/n)
```

- 如果用户确认，执行 `git init <repo-path>`
- 如果用户否定，结束操作

### 1.3 检查当前配置

在确定仓库路径后，检查当前配置：

```bash
git -C <repo-path> config --get user.name
git -C <repo-path> config --get user.email
git -C <repo-path> remote get-url origin 2>/dev/null || echo "NOT_SET"
```

### 1.4 缺失配置的引导

**获取当前工作目录的完整路径并展示给用户确认：**

```bash
pwd
```

显示路径供用户确认：
```
📁 Git 仓库路径（将保存到 git-config.md）：
   E:\path\to\your\project

确认请输入 'y'，或输入新路径：
```

- **如果用户直接回车确认**：使用当前目录
- **如果用户输入新路径**：使用用户指定的路径

**如果 `user.name` 未配置，提示用户输入：**
```
👤 请输入你的 Git 用户名（user.name）：
（例如：YourName 或 YourName <email@example.com>）
```

**如果 `user.email` 未配置，提示用户输入：**
```
📧 请输入你的 Git 邮箱（user.email）：
（例如：your.email@gmail.com）
```

**如果 `origin` 远程仓库未配置，提示用户输入：**
```
🔗 请输入远程仓库地址（git remote add origin）：
（例如：https://github.com/username/repo.git）
```

### 1.5 保存配置到 git-config.md

将配置保存到当前工程根目录的 `git-config.md` 文件：

```markdown
# Git 配置

## 本地仓库信息

- **仓库路径**：`E:\path\to\your\project`
- **初始化时间**：`2024-01-01 12:00:00`

## Git 配置

| 配置项 | 值 |
|--------|-----|
| user.name | YourName |
| user.email | your.email@gmail.com |
| remote.origin | https://github.com/username/repo.git |

## 远程仓库

- **默认分支**：main
- **远程仓库**：origin
```

写入文件：
```bash
cat > <repo-path>/git-config.md << 'EOF'
# Git 配置

## 本地仓库信息

- **仓库路径**：`{full-path}`
- **初始化时间**：`{timestamp}`

## Git 配置

| 配置项 | 值 |
|--------|-----|
| user.name | {user-name} |
| user.email | {user-email} |
| remote.origin | {repo-url} |

## 远程仓库

- **默认分支**：main
- **远程仓库**：origin
EOF
```

### 1.6 执行本地 Git 配置

获取用户输入后，在本地仓库执行配置命令：

```bash
# 配置用户名
git -C <repo-path> config user.name "<user-name>"

# 配置邮箱
git -C <repo-path> config user.email "<user-email>"

# 添加远程仓库（如果还没有 origin）
if ! git -C <repo-path> remote get-url origin >/dev/null 2>&1; then
    git -C <repo-path> remote add origin <repo-url>
else
    # 或更新远程仓库地址
    git -C <repo-path> remote set-url origin <repo-url>
fi
```

配置完成后，显示配置摘要并继续执行正常的 Git 工作流：

```
✅ Git 配置完成！

📁 仓库路径：E:\path\to\your\project
👤 用户名：YourName
📧 邮箱：your.email@gmail.com
🔗 远程仓库：https://github.com/username/repo.git

📄 配置已保存到：git-config.md
```

---

## 工作流程

**前置变量**：设 `<REPO>` 为从 git-config.md 提取的仓库路径。

所有 Git 命令使用 `git -C <REPO>` 格式执行，无需切换目录。

### 1. 检查 Git 仓库状态

```bash
git -C <REPO> status
git -C <REPO> branch --show-current
git -C <REPO> remote -v
```

### 2. 分析文件改动

```bash
git -C <REPO> diff --staged    # 已暂存的改动
git -C <REPO> diff             # 未暂存的改动
```

根据改动内容判断：
- 哪些文件应该提交
- 改动的性质（新功能、修复、文档等）

### 3. 生成提交信息

使用**简洁中文**风格，格式：`[类型] 描述`

常见类型：
- `feat` - 新功能
- `fix` - 修复 bug
- `refactor` - 重构
- `docs` - 文档
- `style` - 样式调整
- `chore` - 辅助工具、构建等

**示例**：
- `feat(auth): 添加用户登录功能`
- `fix: 修复列表翻页bug`
- `docs: 更新README`

如果改动包含多种类型，选择最主要的。

### 4. 执行提交

#### 4.1 检查远程状态（严格模式）

```bash
git -C <REPO> fetch origin
git -C <REPO> status
```

如果远程有新提交，提示用户：
```
⚠️ 远程有新提交，是否先 pull 再推送？
输入 'y' 继续 pull 后推送，输入 'n' 只本地提交不推送
```

#### 4.2 添加文件

```bash
git -C <REPO> add -A
# 或只添加特定文件
git -C <REPO> add <file-path>
```

#### 4.3 提交

```bash
git -C <REPO> commit -m "<提交信息>"
```

### 5. 推送到远程

```bash
git -C <REPO> push origin main
```

如果当前分支不是 main：

```bash
git -C <REPO> push -u origin <current-branch>
```

## 输出格式

执行过程中实时输出进度：

```
🔍 分析改动中...
📝 生成提交信息: [feat] 添加用户登录功能
📦 执行 git add...
✅ 提交成功: abc1234
🚀 推送到 origin/main...
✅ 推送完成!
```

## 错误处理

| 情况 | 处理方式 |
|------|----------|
| 非 Git 仓库 | 提示用户执行 `git init` 初始化 |
| 首次使用（未配置 user.name） | 提示用户输入用户名 |
| 首次使用（未配置 user.email） | 提示用户输入邮箱 |
| 首次使用（未配置 origin） | 提示用户输入远程仓库地址 |
| 没有改动 | 提示用户 "没有需要提交的改动" |
| 远程有新提交 | 严格检查，询问用户是否先 pull |
| 推送失败 | 显示错误信息，询问是否重试 |
| 提交信息为空 | 提示用户输入提交描述 |

## 用户确认

对于以下情况，执行前需要用户确认：
- Git 仓库路径（首次使用或指定路径时）
- 远程有新提交（是否 pull）
- 推送失败（是否重试）
- 多个分支存在（确认推送到哪个）

## 注意事项

1. **安全优先**：不执行强制推送 `git push -f`
2. **保持简洁**：提交信息用简洁中文，不超过 50 字
3. **小步提交**：建议多次少量提交，而非一次大量
4. **保留分支**：不删除或合并分支

---

## 可选参数

- `/auto-git` - 使用当前目录（检查 git-config.md）
- `/auto-git --no-push` - 只提交，不推送
- `/auto-git --amend` - 修改最后一次提交
- `/auto-git <消息>` - 直接使用指定的提交信息

---

**提示**：如果用户只是想写提交信息而不想执行操作，可以只执行前几步并展示提交信息供用户确认。