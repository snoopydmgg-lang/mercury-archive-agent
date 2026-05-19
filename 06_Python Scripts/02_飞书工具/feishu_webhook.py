"""
飞书对话机器人 - Web 服务器版本
使用 Flask 处理飞书回调
"""
import json
import requests
import io
import sys
from flask import Flask, request, jsonify

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BOT_OPEN_ID = "ou_2a4e28e9b4e4c9f76f21a5e2994ac99d"

app = Flask(__name__)


def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    return None


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

    if command == "帮助":
        return """可用命令:
1. 帮助 - 显示此帮助信息
2. 时间 - 显示当前时间
3. 状态 - 显示系统状态
4. 你好 - 打招呼
5. 执行 <命令> - 执行系统命令
6. 读取飞书表格 - 读取飞书多维表格数据"""

    elif command == "时间":
        from datetime import datetime
        return f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    elif command == "状态":
        return "系统状态: 正常运行中 ✅"

    elif command == "你好":
        return "你好！我是 Claude Code 飞书助手，很高兴为你服务！"

    elif command == "读取飞书表格":
        return "读取飞书表格功能开发中..."

    elif command.startswith("执行 "):
        cmd = command[3:]
        return f"收到命令: {cmd}\n\n(本地执行命令功能需要额外开发)"

    else:
        return f"收到消息: {command}\n\n如需帮助，请发送 帮助 查看可用命令。"


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    """飞书回调处理"""
    # 验证 URL 时飞书会发送 GET 请求
    if request.method == 'GET':
        # 飞书验证会发送 challenge 参数
        challenge = request.args.get('challenge')
        if challenge:
            print(f"收到验证请求，challenge: {challenge}")
            return jsonify({"challenge": challenge})

    # 处理消息事件
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"收到飞书回调: {json.dumps(data, ensure_ascii=False)[:500]}")

            # 检查是否是验证请求
            challenge = data.get("challenge")
            if challenge:
                print(f"收到验证请求(POST)，challenge: {challenge}")
                return jsonify({"challenge": challenge})

            # 获取 token
            token = get_tenant_access_token()
            if not token:
                return jsonify({"code": -1, "msg": "token error"})

            # 解析消息事件
            event = data.get("event", {})
            event_type = event.get("type")

            if event_type == "im.message.receive_v1":
                # 处理接收到的消息
                message = event.get("message", {})
                sender_id = message.get("sender_id", {}).get("open_id")
                body = message.get("body", {})
                content = body.get("content", {})

                # 解析消息内容
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        pass

                text = content.get("text", "")

                if text and sender_id:
                    print(f"收到消息 from {sender_id}: {text}")

                    # 执行命令
                    response = execute_command(text)
                    print(f"回复: {response}")

                    # 发送回复
                    send_message(token, sender_id, response)

            return jsonify({"code": 0})

        except Exception as e:
            print(f"处理回调出错: {e}")
            return jsonify({"code": -1, "msg": str(e)})

    return jsonify({"code": 0})


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    print("=" * 50)
    print("飞书对话机器人启动中...")
    print("回调地址: http://216d0e84.r24.cpolar.top/callback")
    print("请确保已在飞书开放平台配置好回调 URL")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000)
