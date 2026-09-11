# novel-pipeline / 创作流水线

> 作者主页: [github.com/aigc350/skills](https://github.com/aigc350/skills)

把小说想法一路推到 AI 视频生成 Prompt 的完整工作流。

## 流水线

```
novel-creator → novel-to-script → script-to-shot → shot-to-prompt
   ① 写小说        ② 改剧本          ③ 出分镜        ④ 生视频 Prompt
                                                            │
                                                            ▼
                                              视频生成 (Sora / Runway / Kling)
                                                            │
                                                            ▼
                                              whisper-batch ⑤ 反向转字幕
```

## 阶段说明

### ① novel-creator — 长篇小说自动创作
- 1000+ 章节可持续创作
- 多级记忆机制，避免剧情遗忘
- 角色与世界观一致性校验
- 伏笔追踪、支线管理、节奏控制
- 命令：`/novel-creator init|run|status|plan|revise|validate`

### ② novel-to-script — 小说转剧本
- 三层记忆系统（章节 / 场景 / 角色）
- 自动质量校验闭环
- 命令：`/novel-to-script run|status|export`

### ③ script-to-shot — 剧本转分镜
- 输入：novel-to-script 输出的 `scenes.yaml` + `script.yaml`
- 输出：标准化 `shot_spec` + `characters` + `scenes`
- 命令：`/script-to-shot run|status|export`

### ④ shot-to-prompt — 分镜转 AI 视频 Prompt
- 输入：上一阶段的 `shot_spec`
- 输出：Sora / Runway / Pika / Kling 等模型可直接使用的 Prompt
- 命令：`/shot-to-prompt run|status|export`

### ⑤ whisper-batch — 视频/音频批量转字幕
- 使用 faster-whisper
- 支持 mp4 / mkv / avi / mov / mp3 / wav / flac / m4a / webm
- 输出 SRT 字幕 + 纯文本
- 命令：`/whisper-batch run|status`

## 数据流向

```
novel-creator/output/chapters/*.md
        ↓ (章节级)
novel-to-script/output/script.yaml + scenes.yaml
        ↓ (场景级)
script-to-shot/output/shot_spec.yaml + characters/ + scenes/
        ↓ (镜头级)
shot-to-prompt/output/prompts/*.md
        ↓
外部 AI 视频模型生成片段
        ↓
whisper-batch 处理成片字幕
```

每个 Skill 独立运行、目录互不耦合，可单独使用或按顺序串联。