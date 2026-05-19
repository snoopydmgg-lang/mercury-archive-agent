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
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 创建 ASCII 字段名的数字字段
r = requests.post(
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields",
    headers=headers,
    json={"field_name": "Score", "type": 2}
)
result = r.json()
print(f"Create field: code={result.get('code')}, msg={result.get('msg')}")
if result.get("code") == 0:
    field_id = result["data"]["field"]["field_id"]
    print(f"Field ID: {field_id}")

    # 写入评分
    records = [
        ("recvee9cZDxpfB", "飞鸟集", 40.0),
        ("recvee9Xj4exrU", "梁思成", 58.0),
    ]
    for rid, name, score in records:
        r2 = requests.put(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{rid}",
            headers=headers,
            json={"fields": {"Score": score}}
        )
        print(f"Write {name}: code={r2.json().get('code')}, msg={r2.json().get('msg')}")
