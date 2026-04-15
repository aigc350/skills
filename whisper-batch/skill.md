---
name: whisper-batch
description: "Batch audio/video transcription tool using faster-whisper. Converts speech to SRT subtitles and plain text. Supports mp4/mkv/avi/mov/mp3/wav/flac/m4a/webm. Commands: run/status."
---

# Whisper Batch - 批量语音转录

使用 faster-whisper 对视频/音频文件进行批量语音转录，生成 SRT 字幕和纯文本。

## 快速开始

```
/whisper-batch run <input>              # 转录文件或目录
/whisper-batch run <input> -m medium    # 指定模型
/whisper-batch run <input> --device cuda # 使用 GPU
/whisper-batch status                   # 查看环境状态
```

---

## 命令路由

解析用户命令后，读取对应文档执行：

| 命令 | 作用 | 详细文档 |
|------|------|----------|
| `run <input> [options]` | 执行转录 | [commands/run.md](commands/run.md) |
| `status` | 检查环境 | [commands/status.md](commands/status.md) |

---

## 依赖

- Python 3.8+
- faster-whisper
- opencc-python-reimplemented

---

## 核心脚本

工具脚本位于：`.claude/skills/whisper-batch/scripts/whisper_batch.py`

调用时使用相对路径：
```bash
python .claude/skills/whisper-batch/scripts/whisper_batch.py ...
```
