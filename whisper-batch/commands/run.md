# run 命令 - 执行转录

执行 `/whisper-batch run` 时，按以下步骤处理。

## 命令格式

```
/whisper-batch run <input> [options]
```

## 参数解析

从用户输入中提取以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input` | (必填) | 输入文件路径或目录 |
| `-m / --model` | `small` | 模型: tiny, base, small, medium, large-v3 |
| `-l / --language` | `zh` | 语言代码，设 `auto` 自动检测 |
| `-o / --output` | 源文件同目录 | 输出目录 |
| `--device` | `cpu` | 设备: cpu, cuda |
| `--compute-type` | 自动 | 计算精度: int8(cpu), float16(cuda) |

## 执行步骤

### Step 1: 前置检查

运行前先确认环境：

```bash
python -c "from faster_whisper import WhisperModel; print('faster-whisper OK')"
python -c "from opencc import OpenCC; print('opencc OK')"
```

如果任一依赖缺失，提示用户安装：

```
缺少依赖，请运行：
pip install faster-whisper opencc-python-reimplemented
```

### Step 2: 确认输入

检查用户提供的 input 路径：
- 如果是文件：检查文件是否存在、格式是否支持
- 如果是目录：统计支持的文件数量
- 如果路径不存在：提示错误

支持的格式：`.mp4 .mkv .avi .mov .mp3 .wav .flac .m4a .webm`

### Step 3: 确认参数并向用户展示计划

展示将要执行的操作摘要：

```
转录计划：
  输入: <路径> (N 个文件)
  模型: <model> (<device>, <compute_type>)
  语言: <language>
  输出: <output_dir>
```

**仅在用户确认后继续执行。**

### Step 4: 执行转录

调用核心脚本：

```bash
python .claude/skills/whisper-batch/scripts/whisper_batch.py "<input>" -m <model> -l <language> [-o <output>] [--device <device>] [--compute-type <type>]
```

注意事项：
- 如果是单文件，直接传文件路径
- 如果是目录，传目录路径（脚本内部会递归搜索）
- 大模型或大文件转录时间较长，使用较长 timeout（最多 10 分钟）

### Step 5: 汇报结果

执行完成后，展示：
- 成功/失败文件数
- 输出文件列表（.srt 和 .txt）
- 如有失败，展示失败原因

## 示例

```
用户: /whisper-batch run ./videos
     → 转录 ./videos 下所有视频文件

用户: /whisper-batch run meeting.mp3 -m medium -o ./subtitles
     → 用 medium 模型转录 meeting.mp3，输出到 ./subtitles

用户: /whisper-batch run ./recordings --device cuda -m large-v3
     → GPU 加速，使用 large-v3 模型转录
```
