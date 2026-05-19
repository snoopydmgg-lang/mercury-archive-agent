"""
飞书选品表格管理脚本 - 删除测试数据
用法: python feishu_selection_delete.py
"""
import requests
import json
import sys
import io

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 选品追踪表格配置
BITABLE_TOKEN = "DS65bww0Kazokosc3AXcITPsnUf"
TABLE_ID = "tblZP96FGm0KpTjR"


def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        print(f"获取token失败: {data}")
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


def delete_record(token, record_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    data = resp.json()
    return data.get("code") == 0


def main():
    print("=== 飞书选品追踪表格管理 ===\n")

    # 获取token
    token = get_tenant_access_token()
    if not token:
        sys.exit(1)
    print("Token获取成功\n")

    # 获取所有记录
    print("获取记录...")
    records = get_all_records(token)
    if not records:
        print("表格中没有记录")
        sys.exit(1)

    print(f"共有 {len(records)} 条记录:\n")

    # 显示所有记录
    for i, record in enumerate(records, 1):
        fields = record.get("fields", {})
        name = fields.get("产品名称", "未命名")
        record_id = record.get("record_id")
        print(f"{i}. [{record_id}] {name}")

    # 删除前2条
    print(f"\n删除前2条记录...")
    for i, record in enumerate(records[:2], 1):
        record_id = record.get("record_id")
        fields = record.get("fields", {})
        name = fields.get("产品名称", "未命名")
        print(f"删除: {name}", end=" ")
        if delete_record(token, record_id):
            print("✓")
        else:
            print("✗")

    print("\n完成!")


if __name__ == "__main__":
    main()
