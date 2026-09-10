import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path

# 禁用代理（飞书 WebSocket 连接不需要代理）
os.environ["NO_PROXY"] = "open.feishu.cn,lark.oapi.cn"
if "HTTP_PROXY" in os.environ:
    del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ:
    del os.environ["HTTPS_PROXY"]

from lark_oapi import Client as LarkClient, LogLevel
from lark_oapi.api.im.v1 import *
from lark_oapi.event.dispatcher_handler import EventDispatcherHandler
from lark_oapi.ws import Client as WsClient

# =========== 从配置文件读取 ===========
CONFIG_FILE = Path(__file__).parent / "feishu.config.md"

def load_config():
    """从 feishu.config.md 解析 APP_ID 和 APP_SECRET"""
    if not CONFIG_FILE.exists():
        raise RuntimeError(f"配置文件不存在: {CONFIG_FILE}")

    content = CONFIG_FILE.read_text(encoding="utf-8")
    app_id = re.search(r"## APP_ID\s*\n\s*([^\s]+)", content)
    app_secret = re.search(r"## APP_SECRET\s*\n\s*([^\s]+)", content)

    if not app_id or not app_secret:
        raise RuntimeError("配置文件格式错误，需要 ## APP_ID 和 ## APP_SECRET 两个标题")

    return app_id.group(1).strip(), app_secret.group(1).strip()

APP_ID, APP_SECRET = load_config()
# ======================================

# 初始化飞书客户端
lark = LarkClient.builder() \
    .app_id(APP_ID) \
    .app_secret(APP_SECRET) \
    .log_level(LogLevel.INFO) \
    .build()

# 获取机器人自身的 open_id（用于过滤自己发的消息）
BOT_OPEN_ID = None

def get_bot_info():
    """获取机器人信息，返回 open_id"""
    try:
        # 调用 getBotInfo 接口获取机器人信息
        resp = lark.im.v1.bot_info.get()
        if resp.success():
            return resp.data.bot.open_id
    except Exception as e:
        print(f"获取机器人信息失败: {e}")
    return None

# 发送消息回飞书
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
    except Exception as e:
        print(f"发送失败: {e}")

# 调用 Claude Code
def ask_claude(prompt):
    try:
        print(f"调用 Claude Code: {prompt}")
        result = subprocess.run(
            [
                "claude", "-p",
                "--dangerously-skip-permissions",
                prompt,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
        )
        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip()
        if not output:
            output = "(无输出)"
        print(f"Claude Code 返回: {output[:200]}...")
        return output
    except subprocess.TimeoutExpired:
        return "Claude Code 超时（300秒），请稍后重试"
    except Exception as e:
        return f"Claude Code 出错: {str(e)}"

# 处理收到的消息事件
def on_message_receive(data: P2ImMessageReceiveV1):
    try:
        msg = data.event.message
        sender = data.event.sender

        # 过滤非文本消息
        if msg.message_type != "text":
            return

        # 过滤机器人自己发的消息（防止无限循环）
        sender_open_id = sender.sender_id.open_id if sender and sender.sender_id else ""
        if sender_open_id == BOT_OPEN_ID:
            print(f"跳过机器人自身消息")
            return

        content = json.loads(msg.content)
        text = content.get("text", "").strip()
        if not text:
            return

        print(f"收到消息 [{sender_open_id}]: {text}")
        send_feishu_msg(msg.chat_id, "处理中...")
        reply = ask_claude(text)
        send_feishu_msg(msg.chat_id, reply)
    except Exception as e:
        print(f"处理消息失败: {e}")
        import traceback
        traceback.print_exc()

# WS 长连接监听飞书消息（带重连）
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
            print("WS 连接启动...")
            ws.start()
        except Exception as e:
            print(f"WS 连接异常: {e}, 5秒后重连...")
            time.sleep(5)

# 启动服务
if __name__ == "__main__":
    print("飞书 Claude Code 机器人启动...", flush=True)

    # 不获取 bot_info，直接启动（API 已变更）
    print("警告: 跳过 bot_info 获取", flush=True)

    print("飞书 Claude Code 机器人启动成功！等待消息...", flush=True)
    threading.Thread(target=ws_listen, daemon=True).start()
    while True:
        time.sleep(1)