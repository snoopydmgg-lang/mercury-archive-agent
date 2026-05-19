# -*- coding: utf-8 -*-
import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "DS65bww0Kazokosc3AXcITPsnUf"
TABLE_ID = "tblZP96FGm0KpTjR"

resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
token = resp.json().get("tenant_access_token")
headers = {"Authorization": f"Bearer {token}"}

resp = requests.get(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields",
    headers=headers)
data = resp.json()
print(f"Code: {data.get('code')}")
print(f"Fields:")
for f in data.get("data", {}).get("items", []):
    print(f"  ID: {f.get('field_id')} | Name: {f.get('field_name')} | Type: {f.get('type')}")
