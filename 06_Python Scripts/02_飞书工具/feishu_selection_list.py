"""
飞书选品表格读取脚本
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

def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    records = get_records(token)
    print(f"=== 选品追踪表格 - 共 {len(records)} 条记录 ===\n")

    for i, r in enumerate(records, 1):
        fields = r.get("fields", {})
        name = fields.get("产品名称", "未命名")
        status = fields.get("跟进状态", "")
        price = fields.get("客单价", "")
        print(f"{i}. {name} | 状态: {status} | 客单价: {price}")

if __name__ == "__main__":
    main()
