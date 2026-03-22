# Claude Skills 技能集合

本目录包含项目自定义的 Claude Code 技能。

## 技能列表

### novel-creator (小说创作系统)

AI 驱动的长篇小说自动创作系统，支持 1000+ 章节的持续创作。

**主要功能：**
- 稳定长篇写作 - 多级记忆机制避免 AI 遗忘剧情
- 角色一致性 - 角色行为约束，防止角色崩坏
- 世界观一致 - 严格遵守 canon 设定
- 自动剧情管理 - 伏笔追踪、支线管理、节奏控制

**命令：**
- `/novel-creator init` - 初始化小说项目
- `/novel-creator run [n]` - 生成 n 章
- `/novel-creator status` - 查看状态
- `/novel-creator plan` - 规划章节
- `/novel-creator revise <章节号>` - 修订章节
- `/novel-creator validate` - 校验一致性

---

### auto-git (自动化 Git 工作流)

自动化 Git 操作，简化日常开发流程。

**主要功能：**
- 自动分析代码改动
- 生成简洁中文提交信息
- 执行 add → commit → push 完整流程
- 检查远程状态，避免冲突
- 配置文件 git-config.md 保存仓库配置

**命令：**
- `/auto-git` - 执行自动提交流程
- `/auto-git --no-push` - 只提交，不推送

**配置：**
首次使用时会引导配置：
- Git 仓库路径
- user.name
- user.email
- remote origin

配置会保存到 `git-config.md` 文件。