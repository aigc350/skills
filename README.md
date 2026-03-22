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