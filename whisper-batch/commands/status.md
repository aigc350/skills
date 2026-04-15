# status 命令 - 检查环境

执行 `/whisper-batch status` 时，检查当前环境状态。

## 执行步骤

### Step 1: 检查 Python 版本

```bash
python --version
```

需要 Python 3.8+。

### Step 2: 检查依赖

逐个检查：

```bash
python -c "from faster_whisper import WhisperModel; print('faster-whisper:', WhisperModel.__module__)"
python -c "from opencc import OpenCC; print('opencc: OK')"
```

### Step 3: 检查 CUDA 可用性

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')" 2>/dev/null || echo "PyTorch not installed (CPU mode only)"
```

### Step 4: 检查脚本

确认 `.claude/skills/whisper-batch/scripts/whisper_batch.py` 存在。

### Step 5: 汇报

展示环境摘要：

```
Whisper Batch 环境状态
─────────────────────
Python:        3.x.x
faster-whisper: ✓ 已安装
opencc:        ✓ 已安装
CUDA:          ✓ 可用 (GPU名称) / ✗ 仅 CPU
脚本:          ✓ whisper_batch.py

建议:
  - GPU 可用时使用 --device cuda 加速
  - 中文推荐 -m small 或 -m medium
  - 高精度推荐 -m large-v3
```
