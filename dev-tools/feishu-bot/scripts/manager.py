#!/usr/bin/env python3
"""
Feishu Claude Code Bot 管理脚本

文件分布：
    ~/.claude/feishu.config.md    ← 共享配置
    ~/.claude/.feishu-bot.pid     ← 全局 PID
    ~/.claude/.feishu-bot.log     ← 全局日志
    {project}/.feishu-bot-pending.json  ← 任务文件
    {project}/.feishu-bot-reply.json    ← 回复文件

命令:
    python manager.py start              - 启动监听（使用当前工程目录）
    python manager.py start D:/project   - 启动监听（指定工程目录）
    python manager.py stop               - 停止监听
    python manager.py status            - 查看运行状态
    python manager.py logs N            - 查看最近 N 行日志 (默认 50)
"""

import io
import os
import subprocess
import sys
import time
import json
from pathlib import Path

# 强制 UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 全局文件（用户目录）
USER_DIR = Path.home() / ".claude"
PID_FILE = USER_DIR / ".feishu-bot.pid"
LOG_FILE = USER_DIR / ".feishu-bot.log"
CONFIG_FILE = USER_DIR / "feishu.config.md"

# 脚本路径
SCRIPTS_DIR = Path(__file__).parent
LISTENER_SCRIPT = SCRIPTS_DIR / "listener.py"

def check_config():
    """检查配置文件是否存在"""
    if not CONFIG_FILE.exists():
        print("[ERROR] 配置文件不存在: ~/.claude/feishu.config.md")
        print("        请创建配置文件，格式如下:")
        print("        ## APP_ID")
        print("        cli_xxx")
        print("        ## APP_SECRET")
        print("        xxx")
        return False
    return True

def get_pid():
    """读取 PID 和工程目录"""
    if PID_FILE.exists():
        try:
            data = json.loads(PID_FILE.read_text().strip())
            return data.get("pid"), data.get("project")
        except:
            # 兼容旧格式
            content = PID_FILE.read_text().strip()
            if ":" in content:
                pid, mode = content.split(":")
                return int(pid), None
            return int(content), None
    return None, None

def is_running(pid):
    """检查进程是否运行"""
    if pid is None:
        return False
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True
            )
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except:
        return False

def start(project_dir=None):
    """启动监听"""
    if not check_config():
        return 1

    pid, old_project = get_pid()
    if pid and is_running(pid):
        print(f"[WARN] 监听已在运行 (PID: {pid}, 工程: {old_project})")
        if old_project and project_dir and Path(old_project) != Path(project_dir):
            print(f"[WARN] 当前工程与运行中的工程不同，任务将写入 {old_project}")
        return 0

    # 清理旧 PID 文件
    if PID_FILE.exists():
        PID_FILE.unlink()

    # 清理旧日志
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    # 确定工程目录
    if project_dir:
        project_dir = Path(project_dir).resolve()
    else:
        # 默认使用当前工作目录
        project_dir = Path.cwd().resolve()

    print(f"[START] 启动飞书监听...")
    print(f"        工程目录: {project_dir}")
    print(f"        配置文件: {CONFIG_FILE}")

    # 后台启动
    cmd = ["python", str(LISTENER_SCRIPT), str(project_dir)]

    # Windows: 隐藏窗口
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        proc = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
            startupinfo=startupinfo,
        )
    else:
        proc = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
        )

    # 保存 PID 和工程目录
    PID_FILE.write_text(json.dumps({"pid": proc.pid, "project": str(project_dir)}))

    # 等待确认启动
    time.sleep(2)
    if is_running(proc.pid):
        print(f"[OK] 启动成功 (PID: {proc.pid})")
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")[:3]
            for line in lines:
                print(f"      {line}")
        print("")
        print("[提示] 如需在 Claude Code 内自动处理任务，请执行:")
        print("       /loop 10s 检查飞书任务文件，有任务时触发 /feishu-bot run，无任务时跳过")
        return 0
    else:
        print("[FAIL] 启动失败，请查看日志:")
        if LOG_FILE.exists():
            print(LOG_FILE.read_text(encoding="utf-8"))
        return 1

def stop():
    """停止监听"""
    pid, project = get_pid()
    if not pid:
        print("[WARN] 监听未运行")
        return 0

    if not is_running(pid):
        print("[WARN] 监听已停止 (PID 文件过期)")
        PID_FILE.unlink()
        return 0

    print(f"[STOP] 停止监听 (PID: {pid}, 工程: {project})...")

    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
        else:
            os.kill(pid, 9)

        time.sleep(1)
        if not is_running(pid):
            print("[OK] 已停止")
            PID_FILE.unlink()
            return 0
        else:
            print("[FAIL] 停止失败")
            return 1
    except Exception as e:
        print(f"[FAIL] 停止失败: {e}")
        return 1

def status():
    """查看运行状态"""
    pid, project = get_pid()

    print("=== 飞书 Claude Code 监听状态 ===")

    if not pid:
        print("状态: [ ] 未运行")
        print(f"配置: {CONFIG_FILE}")
        return 0

    if is_running(pid):
        print(f"状态: [X] 运行中")
        print(f"PID:  {pid}")
        print(f"工程: {project}")

        if LOG_FILE.exists():
            mtime = LOG_FILE.stat().st_mtime
            elapsed = time.time() - mtime
            hours = int(elapsed // 3600)
            mins = int((elapsed % 3600) // 60)
            print(f"时长: {hours}h {mins}m")

            size = LOG_FILE.stat().st_size
            print(f"日志: {size/1024:.1f} KB ({LOG_FILE})")

            content = LOG_FILE.read_text(encoding="utf-8", errors="replace")
            recv_count = content.count("收到消息")
            send_count = content.count("发送回复")
            print(f"消息: 收到 {recv_count} / 发送 {send_count}")
        return 0
    else:
        print("状态: [-] 已停止 (PID 文件过期)")
        print(f"PID:  {pid} (无效)")
        return 0

def logs(n=50):
    """查看日志"""
    if not LOG_FILE.exists():
        print("[WARN] 日志文件不存在")
        return 0

    # 使用 errors='replace' 处理非 UTF-8 字符
    content = LOG_FILE.read_text(encoding="utf-8", errors="replace")
    lines = content.strip().split("\n")

    print(f"=== 最近 {n} 行日志 ===")

    for line in lines[-n:]:
        print(line)

    return 0

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    cmd = sys.argv[1].lower()

    if cmd == "start":
        project_dir = sys.argv[2] if len(sys.argv) > 2 else None
        return start(project_dir)
    elif cmd == "stop":
        return stop()
    elif cmd == "status":
        return status()
    elif cmd == "logs":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        return logs(n)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())