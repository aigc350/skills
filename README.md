# Claude & Codex 通用 Skill 集合

日常工作沉淀的 Claude / Codex 通用 Skill，按场景归档即用即取。

> 作者主页: [github.com/aigc350/skills](https://github.com/aigc350/skills)
>
> 常用工具:
> - [runninghub.ai](https://www.runninghub.ai/) — 各家 AI 模型 API 聚合调用（部分 Skill 依赖）
> - [video.quantv.com](https://video.quantv.com/) — 跨境电商 AI 工具
>
> 如有问题或合作: WeChat `aigc350`

## 目录速览

| 板块 | 适用场景 |
|---|---|
| **[novel-pipeline/](novel-pipeline/)** | 把一个小说想法，一路推到 AI 视频生成的 Prompt |
| **[dev-tools/](dev-tools/)** | 提交代码、远程控制 Claude、复盘对话 |
| **[commerce/](commerce/)** | 电商运营与商品数据处理（建设中） |

## novel-pipeline · 小说到视频

```
novel-creator → novel-to-script → script-to-shot → shot-to-prompt
                                              ↓
                                       视频生成 (Sora/Runway/Kling)
                                              ↓
                                       whisper-batch 转字幕
```

- **novel-creator** — 想稳定写 1000 章长篇不烂尾
- **novel-to-script** — 想把已有小说改成可拍的剧本
- **script-to-shot** — 想把剧本拆成镜头表交给剧组
- **shot-to-prompt** — 想让 Sora / Runway / Kling / 可灵直接出片
- **whisper-batch** — 想把成片或素材批量转字幕稿

## dev-tools · 日常开发

- **auto-git** — 写完代码不想手动 `add` 一堆命令、还想让 commit message 写得漂亮
- **feishu-bot** — 通勤路上用飞书消息，让家里电脑上的 Claude Code 继续搬砖
- **record** — 一次对话很有价值，想归档成可复习的笔记或课程

## commerce · 跨境电商与 TikTok Shop

- **commerce_selection** — 想系统化做跨境选品判断，不想只凭榜单和直觉拍脑袋
- **kalodata** — 想快速查 TikTok Shop 商品 / 达人 / 店铺 / 视频的销量和趋势

> 选品思路：`kalodata` 拉数据 → `commerce_selection` 套用 SOP 输出候选商品与下一步验证动作。

---

详细命令与使用方式见各子目录 `README.md`。
