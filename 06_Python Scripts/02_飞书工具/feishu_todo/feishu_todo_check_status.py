"""
飞书待办表格查看脚本 - 查看所有记录的状态
"""
import requests
import io
import sys
import json

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


def get_all_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}

    all_records = []
    page_token = None

    while True:
        params = {"page_size": 100}
        if page_token:
            params["page_token"] = page_token

        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()

        if data.get("code") == 0:
            all_records.extend(data.get("data", {}).get("items", []))
            page_token = data.get("data", {}).get("page_token")
            if not page_token:
                break
        else:
            print(f"获取记录失败: {data.get('msg')}")
            return None

    return all_records


def main():
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        return

    records = get_all_records(token)
    if not records:
        print("没有记录")
        return

    print(f"共 {len(records)} 条记录\n")

    # 查看状态字段的所有值
    status_values = set()
    for record in records:
        fields = record.get("fields", {})
        status = fields.get("状态")
        status_values.add(str(status))

    print("状态字段的所有值：")
    for s in status_values:
        print(f"• {s}")

    # 显示几条记录的详细信息
    print("\n前3条记录详情：")
    for i, record in enumerate(records[:3], 1):
        fields = record.get("fields", {})
        print(f"\n--- 记录 {i} ---")
        for k, v in fields.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
