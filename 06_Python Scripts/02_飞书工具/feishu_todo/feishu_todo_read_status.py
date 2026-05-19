"""
飞书待办表格查看脚本 - 查看状态字段选项
"""
import requests
import io
import sys

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 待办表格配置
BITABLE_TOKEN = "JkK5bAxKIaOlAZsgDLWcbkXznGh"
TABLE_ID = "tblMbieB62YUn7f4"


def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    return None


def get_table_fields(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return None


def get_field_options(token, field_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields/{field_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("options", [])
    return []


def main():
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        return

    fields = get_table_fields(token)
    if not fields:
        print("获取字段失败")
        return

    # 查找状态字段
    for f in fields:
        if f.get("field_name") == "状态":
            print("状态字段选项：")
            options = get_field_options(token, f.get("field_id"))
            for opt in options:
                print(f"• {opt.get('name')} (ID: {opt.get('id')})")
            return

    print("未找到状态字段")


if __name__ == "__main__":
    main()
