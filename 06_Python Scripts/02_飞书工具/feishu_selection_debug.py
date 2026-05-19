"""
查看飞书表格字段结构
"""
import requests
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

BITABLE_TOKEN = "DS65bww0Kazokosc3AXcITPsnUf"
TABLE_ID = "tblZP96FGm0KpTjR"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def get_fields(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    return resp.json()

def get_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params={"page_size": 100})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return []

def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    # 查看字段
    print("=== 表格字段 ===")
    fields_data = get_fields(token)
    if fields_data.get("code") == 0:
        for f in fields_data.get("data", {}).get("items", []):
            print(f"  {f.get('field_name')} (type: {f.get('type')})")
    else:
        print(fields_data)

    print("\n=== 记录内容 ===")
    records = get_records(token)
    for i, r in enumerate(records[:3], 1):
        print(f"\n记录 {i}:")
        print(json.dumps(r.get("fields", {}), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
