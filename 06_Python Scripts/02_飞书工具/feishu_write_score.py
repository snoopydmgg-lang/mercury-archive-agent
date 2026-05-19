# -*- coding: utf-8 -*-
import requests
import json
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
print(f"Token: {token[:20]}...")
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

FIELD_NAME = "选品评分_Final"

records = [
    ("recvee9cZDxpfB", "飞鸟集", 40.0),
    ("recvee9Xj4exrU", "梁思成", 58.0),
]

for rid, name, score in records:
    r = requests.put(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{rid}",
        headers=headers,
        json={"fields": {FIELD_NAME: score}}
    )
    result = r.json()
    code = result.get("code")
    msg = result.get("msg")
    print(f"{name}: code={code}, msg={msg}")
