"""
飞书对话助手
功能：读取飞书消息，执行命令，返回结果
"""
import requests
import json
import sys
import io
import time

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 机器人 open_id
BOT_OPEN_ID = "ou_2a4e28e9b4e4c9f76f21a5e2994ac99d"

# 默认接收者
DEFAULT_RECEIVE_ID = "ou_67cb815e7f856d8239d036d94bc471e7"

# 存储上次的 message_id，避免重复处理
LAST_MESSAGE_ID = None


def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        print(f"获取token失败: {data}")
        return None


def get_chat_messages(token, chat_id):
    """获取群聊消息"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size=20"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    print(f"获取消息失败: {data}")
    return []


def get_chats(token):
    """获取机器人所在的群聊列表"""
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return []


def send_message(token, receive_id, content):
    """发送消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    resp = requests.post(url, params=params, headers=headers, json=payload)
    return resp.json()


def execute_command(command):
    """执行命令并返回结果"""
    command = command.strip()

    # 简单命令示例
    if command == "帮助":
        return """可用命令:
1. 帮助 - 显示此帮助信息
2. 时间 - 显示当前时间
3. 状态 - 显示系统状态
4. 你好 - 打招呼
5. 执行 <命令> - 执行系统命令

其他问题我会尽力回答！"""

    elif command == "时间":
        from datetime import datetime
        return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    elif command == "状态":
        return "系统状态: 正常运行中 ✅"

    elif command == "你好":
        return "你好！我是 Claude Code 飞书助手，很高兴为你服务！"

    elif command.startswith("执行 "):
        # 注意：这里有安全风险，实际使用需要限制命令
        cmd = command[3:]
        return f"收到命令: {cmd}\n\n(本地执行命令功能需要额外开发)"

    else:
        return f"收到消息: {command}\n\n如需帮助，请发送 帮助 查看可用命令。"


def process_messages(token, chat_id):
    """处理群聊中的消息"""
    global LAST_MESSAGE_ID

    messages = get_chat_messages(token, chat_id)

    # 按时间倒序，最新的在前面
    messages = sorted(messages, key=lambda x: x.get("create_time", ""), reverse=True)

    for msg in messages:
        msg_id = msg.get("message_id")
        sender = msg.get("sender", {})
        sender_id = sender.get("id")
        sender_type = sender.get("sender_type")

        # 跳过已处理的消息
        if msg_id == LAST_MESSAGE_ID:
            continue

        # 只处理来自用户的消息（不是机器人自己发的）
        if sender_type != "app" and sender_id != BOT_OPEN_ID:
            # 获取消息内容
            body = msg.get("body", {})
            if body:
                content = body.get("content", {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        pass

                text = content.get("text", "")
                # 如果 content 是字符串，尝试解析
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                        text = content.get("text", "")
                    except:
                        text = content

                if text:
                    print(f"\n收到消息: {text}")
                    LAST_MESSAGE_ID = msg_id

                    # 执行命令
                    response = execute_command(text)

                    # 发送回复
                    # 获取发送者的 open_id
                    sender_open_id = msg.get("sender", {}).get("id")
                    print(f"回复: {response}")
                    result = send_message(token, sender_open_id, response)
                    print(f"发送结果: {result.get('code')}")


def main():
    print("=== 飞书对话助手 ===", flush=True)
    print("按 Ctrl+C 退出\n", flush=True)

    # 获取 token
    token = get_tenant_access_token()
    if not token:
        print("获取 token 失败", flush=True)
        return

    print(f"Token 获取成功")

    # 获取群聊
    chats = get_chats(token)
    if not chats:
        print("未找到群聊，请先在飞书中创建一个群并把机器人拉进去")
        return

    chat = chats[0]
    chat_id = chat.get("chat_id")
    chat_name = chat.get("name")
    print(f"监听群聊: {chat_name} ({chat_id})")

    print("\n等待消息...\n")

    # 轮询检查新消息
    while True:
        try:
            process_messages(token, chat_id)
            time.sleep(2)  # 每2秒检查一次
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
