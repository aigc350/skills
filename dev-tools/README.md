# dev-tools / 开发与协作工具

> 作者主页: [github.com/aigc350/skills](https://github.com/aigc350/skills)

辅助日常开发与协作的 Skill 集合。

## 工具一览

| Skill | 触发命令 | 作用 |
|---|---|---|
| auto-git | `/auto-git [--no-push]` | 自动分析代码改动 → 生成中文 commit → add → commit → push |
| feishu-bot | 飞书消息触发 | 通过飞书消息远程调用 Claude Code 进行编程 |
| record | `/record [--category \| --review]` | 记录与 Claude Code 的对话，归类形成习惯模式，最终生成课程 |

## auto-git — 自动化 Git 工作流
- 自动分析代码改动
- 生成简洁中文提交信息
- 一键 add → commit → push
- 检查远程状态避免冲突
- 通过 `git-config.md` 保存仓库配置

## feishu-bot — 飞书 Claude Code 远程控制
- 通过飞书消息远程触发编程任务
- 两种启动方式：Claude Code 内部 / CMD 命令行
- 全局 PID + 工程级任务文件隔离多项目

## record — 对话记录与学习系统
- 采集与 Claude Code 的对话
- 分析思考过程并归类形成习惯模式
- 最终导出为可导入的课程格式
