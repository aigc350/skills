#!/usr/bin/env python3
"""
Feishu Bot Listener - 飞书 Claude Code 远程控制监听脚本

启动方式：
    python listener.py                  # 使用脚本所在工程目录
    python listener.py D:/project1      # 指定工程目录

双向监听：
1. WebSocket 接收飞书消息 → 写入任务文件
2. 监听回复文件 → 发送到飞书

文件分布：
    ~/.claude/feishu.config.md    ← 共享配置
    ~/.claude/.feishu-bot.pid     ← 全局 PID
    ~/.claude/.feishu-bot.log     ← 全局日志
    {project}/.feishu-bot-pending.json  ← 任务文件
    {project}/.feishu-bot-reply.json    ← 回复文件
"""

import json
import os
import re
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

# 禁用代理（飞书 WebSocket 连接不需要代理）
os.environ["NO_PROXY"] = "open.feishu.cn,lark.oapi.cn"
if "HTTP_PROXY" in os.environ:
    del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ:
    del os.environ["HTTPS_PROXY"]

# lark_oapi 导入
from lark_oapi import Client as LarkClient, LogLevel
from lark_oapi.api.im.v1 import *
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws import Client as WsClient

# =========== 路径配置 ===========
USER_DIR = Path.home() / ".claude"

# 工程目录：从命令行参数获取，或使用脚本所在位置向上查找
def get_project_dir():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    else:
        # 脚本在 .claude/skills/feishu-bot/scripts/，向上5层是工程根目录
        return Path(__file__).parent.parent.parent.parent.parent.resolve()

PROJECT_DIR = get_project_dir()

# 全局文件（用户目录）
CONFIG_FILE = USER_DIR / "feishu.config.md"
PID_FILE = USER_DIR / ".feishu-bot.pid"
LOG_FILE = USER_DIR / ".feishu-bot.log"

# 工程文件（工程目录）
TASK_FILE = PROJECT_DIR / ".feishu-bot-pending.json"
REPLY_FILE = PROJECT_DIR / ".feishu-bot-reply.json"

# =========== 配置加载 ===========
def load_config():
    """从用户目录读取共享配置"""
    config_path = CONFIG_FILE
    if not config_path.exists():
        # 尝试工程目录（兼容旧版）
        local_config = PROJECT_DIR / "feishu.config.md"
        if local_config.exists():
            config_path = local_config
        else:
            raise RuntimeError(f"配置文件不存在: {CONFIG_FILE}\n请创建配置文件，格式如下:\n## APP_ID\ncli_xxx\n## APP_SECRET\nxxx")

    content = config_path.read_text(encoding="utf-8")
    app_id = re.search(r"## APP_ID\s*\n\s*([^\s]+)", content)
    app_secret = re.search(r"## APP_SECRET\s*\n\s*([^\s]+)", content)

    if not app_id or not app_secret:
        raise RuntimeError("配置文件格式错误，需要 ## APP_ID 和 ## APP_SECRET")

    return app_id.group(1).strip(), app_secret.group(1).strip()

APP_ID, APP_SECRET = load_config()

# =========== 飞书客户端 ===========
lark = LarkClient.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(LogLevel.INFO) \
    .build()

BOT_OPEN_ID = None

# =========== 日志 ===========
def log(msg):
    """写入日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{PROJECT_DIR.name}] {msg}"
    # 直接写入文件，不依赖 stdout
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()

# =========== 飞书 API ===========
def get_bot_info():
    try:
        resp = lark.im.v1.bot_info.get()
        if resp.success():
            return resp.data.bot.open_id
    except Exception as e:
        log(f"获取机器人信息失败: {e}")
    return None

def send_feishu_msg(chat_id, text):
    try:
        req = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(json.dumps({"text": text[:4000]}))
                .build()
            ).build()
        lark.im.v1.message.create(req)
        log(f"发送回复: {text[:50]}...")
    except Exception as e:
        log(f"发送失败: {e}")

# =========== 消息处理 ===========
def on_message_receive(data: P2ImMessageReceiveV1):
    try:
        msg = data.event.message
        sender = data.event.sender

        if msg.message_type != "text":
            return

        sender_open_id = sender.sender_id.open_id if sender and sender.sender_id else ""
        if sender_open_id == BOT_OPEN_ID:
            log("跳过机器人自身消息")
            return

        content = json.loads(msg.content)
        text = content.get("text", "").strip()
        if not text:
            return

        log(f"收到消息 [{sender_open_id}]: {text}")

        # 写入任务文件
        task = {
            "chat_id": msg.chat_id,
            "sender_id": sender_open_id,
            "text": text,
            "project": str(PROJECT_DIR),
            "timestamp": int(time.time())
        }
        TASK_FILE.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
        log(f"写入任务文件: {TASK_FILE}")

        send_feishu_msg(msg.chat_id, f"✅ 已接收任务（工程: {PROJECT_DIR.name}），正在处理...")

    except Exception as e:
        log(f"处理消息失败: {e}")
        import traceback
        traceback.print_exc()

# =========== 回复监听 ===========
def reply_watcher():
    log("回复监听线程启动")
    last_mtime = 0

    while True:
        try:
            if REPLY_FILE.exists():
                mtime = REPLY_FILE.stat().st_mtime

                if mtime > last_mtime:
                    last_mtime = mtime

                    content = REPLY_FILE.read_text(encoding="utf-8")
                    if content.strip():
                        reply = json.loads(content)
                        chat_id = reply.get("chat_id")
                        text = reply.get("text", "")

                        if chat_id and text:
                            send_feishu_msg(chat_id, text)

                        REPLY_FILE.unlink()
                        log(f"删除回复文件: {REPLY_FILE}")

            time.sleep(1)
        except Exception as e:
            log(f"回复监听异常: {e}")
            time.sleep(5)

# =========== WebSocket 监听 ===========
def ws_listen():
    while True:
        try:
            event_handler = EventDispatcherHandler.builder("", "") \
                .register_p2_im_message_receive_v1(on_message_receive) \
                .build()

            ws = WsClient(
                app_id=APP_ID,
                app_secret=APP_SECRET,
                event_handler=event_handler,
            )
            log("WS 连接启动...")
            ws.start()
        except Exception as e:
            log(f"WS 连接异常: {e}, 5秒后重连...")
            time.sleep(5)

# =========== 主程序 ===========
if __name__ == "__main__":
    # 写启动日志
    log(f"工程目录: {PROJECT_DIR}")
    log(f"配置文件: {CONFIG_FILE}")
    log(f"APP_ID: {APP_ID}")
    log("飞书 Bot Listener 启动...")

    # 启动线程
    threading.Thread(target=ws_listen, daemon=True).start()
    threading.Thread(target=reply_watcher, daemon=True).start()

    log("所有线程启动完成，等待消息...")

    while True:
        time.sleep(1)