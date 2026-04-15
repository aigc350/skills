#!/bin/bash
# 检查飞书任务文件（相对路径）
TASK_FILE=".feishu-bot-pending.json"
if [ -f "$TASK_FILE" ]; then
    echo "FEISHU_TASK_FOUND"
    cat "$TASK_FILE"
else
    echo "NO_TASK"
fi