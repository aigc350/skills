#!/usr/bin/env python3
"""
视频批量语音转录工具 (faster-whisper)
- 支持 mp4/mkv/avi/mov/mp3/wav/flac 等格式
- 输出 SRT 字幕文件
- 低内存模式: CPU + int8 量化
"""

import argparse
import glob
import os
import sys
import time

from faster_whisper import WhisperModel
from opencc import OpenCC

# 繁体转简体
_t2s = OpenCC("t2s")


SUPPORTED_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".flac", ".m4a", ".webm")


def format_time(s):
    """秒数转 SRT 时间格式"""
    h = int(s // 3600)
    m = int(s % 3600 // 60)
    sec = int(s % 60)
    ms = int((s % 1) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def transcribe_file(model, filepath, language, output_dir=None):
    """转录单个文件，生成 SRT"""
    basename = os.path.splitext(os.path.basename(filepath))[0]
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        srt_path = os.path.join(output_dir, basename + ".srt")
        txt_path = os.path.join(output_dir, basename + ".txt")
    else:
        srt_path = os.path.splitext(filepath)[0] + ".srt"
        txt_path = os.path.splitext(filepath)[0] + ".txt"

    print(f"  转录中: {filepath}")
    start = time.time()

    segments, info = model.transcribe(
        filepath,
        language=language,
        beam_size=5,
        vad_filter=True,  # 语音活动检测，跳过静音段
    )

    srt_lines = []
    txt_lines = []
    for i, seg in enumerate(segments, 1):
        text = _t2s.convert(seg.text.strip())
        srt_lines.append(f"{i}")
        srt_lines.append(f"{format_time(seg.start)} --> {format_time(seg.end)}")
        srt_lines.append(text)
        srt_lines.append("")
        txt_lines.append(text)

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines))

    elapsed = time.time() - start
    duration = info.duration
    print(f"  完成: 时长 {duration:.1f}s, 耗时 {elapsed:.1f}s")
    print(f"  输出: {srt_path}")
    return srt_path


def main():
    parser = argparse.ArgumentParser(description="批量视频语音转录")
    parser.add_argument("input", help="输入: 文件路径或目录")
    parser.add_argument("-m", "--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="模型大小 (默认: small)")
    parser.add_argument("-l", "--language", default="zh",
                        help="语言代码 (默认: zh, 设 auto 自动检测)")
    parser.add_argument("-o", "--output", default=None,
                        help="输出目录 (默认: 和源文件同目录)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"],
                        help="设备 (默认: cpu)")
    parser.add_argument("--compute-type", default=None,
                        help="计算类型 (默认: int8 for cpu, float16 for cuda)")
    args = parser.parse_args()

    compute_type = args.compute_type or ("int8" if args.device == "cpu" else "float16")

    # 加载模型
    print(f"加载模型: {args.model} ({args.device}, {compute_type})")
    model = WhisperModel(args.model, device=args.device, compute_type=compute_type)
    print("模型加载完成\n")

    # 收集文件
    if os.path.isfile(args.input):
        files = [args.input]
    elif os.path.isdir(args.input):
        files = []
        for ext in SUPPORTED_EXTS:
            files.extend(glob.glob(os.path.join(args.input, "**", f"*{ext}"), recursive=True))
        files.sort()
    else:
        # 当作 glob 模式
        files = sorted(glob.glob(args.input, recursive=True))

    if not files:
        print("未找到可处理的文件")
        sys.exit(1)

    print(f"找到 {len(files)} 个文件\n")

    success, failed = 0, 0
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {os.path.basename(f)}")
        try:
            transcribe_file(model, f, args.language, args.output)
            success += 1
        except Exception as e:
            print(f"  失败: {e}")
            failed += 1
        print()

    print(f"全部完成: 成功 {success}, 失败 {failed}")


if __name__ == "__main__":
    main()
