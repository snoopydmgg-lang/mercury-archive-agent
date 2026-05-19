"""
飞书消息发送脚本
用法: python feishu_sender.py "消息内容"
或: python feishu_sender.py -m "消息内容" -r "ou_xxxxx"
"""
import requests
import json
import sys
import io
import argparse

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 默认接收者 (刘锦程)
DEFAULT_RECEIVE_ID = "ou_67cb815e7f856d8239d036d94bc471e7"


def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        raise Exception(f"获取token失败: {data}")


def get_my_user_id(token):
    """获取当前应用对应用户的 user_id"""
    url = "https://open.feishu.cn/open-apis/authen/v1/index_info"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"响应状态码: {resp.status_code}")

    if resp.status_code != 200:
        print(f"API 返回错误，自动跳过")
        return None

    try:
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("user_id")
        else:
            print(f"获取用户信息失败，错误码: {data.get('code')}，请手动输入你的 user_id")
            return None
    except Exception as e:
        print(f"解析响应失败: {e}，请手动输入你的 user_id")
        return None


def get_user_id_manual(token):
    """通过手机号或邮箱获取用户ID"""
    print("\n请选择获取 user_id 的方式:")
    print("1. 输入手机号")
    print("2. 输入邮箱")
    print("3. 手动输入 user_id")
    choice = input("请选择 (1/2/3): ").strip()

    if choice == "1":
        phone = input("请输入手机号: ").strip()
        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json={"phones": [phone]})
        data = resp.json()
        if data.get("code") == 0 and data.get("data", {}).get("user_list"):
            return data["data"]["user_list"][0]["user_id"]
    elif choice == "2":
        email = input("请输入邮箱: ").strip()
        url = "https://open.feishu.cn/open-apis/contact/v3/users/batch_get_id"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json={"emails": [email]})
        data = resp.json()
        if data.get("code") == 0 and data.get("data", {}).get("user_list"):
            return data["data"]["user_list"][0]["user_id"]
    elif choice == "3":
        return input("请输入 user_id (格式如 ou_xxxxx): ").strip()

    print("获取失败，请重试或手动输入 user_id")
    return None


def send_message(token, receive_id, msg_type="text", content=""):
    """
    发送消息给用户

    Args:
        token: tenant_access_token
        receive_id: 接收者的 open_id 或 user_id
        msg_type: 消息类型 (text, post, image 等)
        content: 消息内容
    """
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {
        "receive_id_type": "open_id"
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 根据消息类型处理 content
    if msg_type == "text":
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": content})
        }
    elif msg_type == "post":
        payload = {
            "receive_id": receive_id,
            "msg_type": "post",
            "content": json.dumps(content)  # content 应该是富文本 JSON
        }
    else:
        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }

    resp = requests.post(url, params=params, headers=headers, json=payload)
    data = resp.json()
    if data.get("code") == 0:
        print(f"消息发送成功! message_id: {data.get('data', {}).get('message_id')}")
        return True
    else:
        print(f"消息发送失败: {data}")
        return False


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="飞书消息发送工具")
    parser.add_argument("-m", "--message", type=str, help="要发送的消息内容")
    parser.add_argument("-r", "--receive_id", type=str, help="接收者的 user_id (格式: ou_xxxxx)")
    args = parser.parse_args()

    print("=== 飞书消息发送工具 ===")

    # 1. 获取 token
    print("\n[1] 获取 tenant_access_token...")
    token = get_tenant_access_token()
    print("Token 获取成功!")

    # 2. 获取接收者的 user_id
    print("\n[2] 获取接收者信息...")
    user_id = args.receive_id
    if not user_id:
        # 使用默认接收者
        user_id = DEFAULT_RECEIVE_ID
        print(f"使用默认接收者: {user_id}")
    else:
        print(f"接收者 user_id: {user_id}")

    # 3. 发送消息
    print("\n[3] 发送消息...")
    message = args.message
    if not message:
        print("请使用 -m 参数指定消息内容")
        print("用法: python feishu_sender.py -m \"你好\" -r \"ou_xxxxx\"")
        return

    print(f"消息内容: {message}")

    success = send_message(token, user_id, msg_type="text", content=message)

    if success:
        print("\n✅ 消息发送成功!")
    else:
        print("\n❌ 消息发送失败!")


if __name__ == "__main__":
    main()
