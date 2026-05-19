"""
飞书选品表格评分调试脚本
"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

BITABLE_TOKEN = "DS65bww0Kazokosc3AXcITPsnUf"
TABLE_ID = "tblZP96FGm0KpTjR"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def get_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params={"page_size": 100})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return []

def update_record_test(token, record_id):
    """测试更新"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.put(url, headers=headers, json={
        "fields": {"综合评分": 85.5}
    })
    print(f"Response: {resp.status_code} - {resp.text}")
    return resp.json().get("code") == 0

def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    records = get_records(token)
    if not records:
        print("未获取到任何记录")
        return

    print(f"共 {len(records)} 条记录\n")

    # 看第一条的完整字段
    if records:
        r = records[0]
        print(f"Record ID: {r.get('record_id')}")
        print(f"Fields: {r.get('fields', {}).keys()}")
        print()
        print("第一条记录的完整数据:")
        for k, v in r.get("fields", {}).items():
            print(f"  {k}: {v} (type: {type(v).__name__})")

        # 测试更新
        print(f"\n测试更新第一条记录...")
        update_record_test(token, r.get('record_id'))

if __name__ == "__main__":
    main()
