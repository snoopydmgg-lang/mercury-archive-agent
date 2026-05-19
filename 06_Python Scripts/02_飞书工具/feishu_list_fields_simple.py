#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 requests 直接调用飞书 API 获取字段列表
"""
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

# 飞书配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

print("=" * 60)
print("  飞书多维表格字段列表（直接 API 调用）")
print("=" * 60)
print()

# 1. 获取 tenant_access_token
print("🔧 正在获取 tenant_access_token...")
try:
    auth_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    auth_data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    auth_response = requests.post(auth_url, json=auth_data, verify=False)
    auth_result = auth_response.json()

    if auth_result.get("code") != 0:
        print(f"❌ 获取 token 失败：{auth_result}")
        sys.exit(1)

    tenant_access_token = auth_result["tenant_access_token"]
    print(f"✅ Token 获取成功")
    print()
except Exception as e:
    print(f"❌ 获取 token 失败：{e}")
    sys.exit(1)

# 2. 获取字段列表
print("📡 正在获取字段列表...")
try:
    fields_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }

    fields_response = requests.get(fields_url, headers=headers, verify=False)
    fields_result = fields_response.json()

    if fields_result.get("code") != 0:
        print(f"❌ 获取字段失败：{fields_result}")
        sys.exit(1)

    print("✅ 获取成功")
    print()
    print("=" * 60)
    print("字段列表：")
    print("=" * 60)

    items = fields_result.get("data", {}).get("items", [])
    if items:
        for idx, field in enumerate(items, 1):
            print(f"{idx}. 字段名: {field.get('field_name')}")
            print(f"   字段ID: {field.get('field_id')}")
            print(f"   字段类型: {field.get('type')}")
            print()
    else:
        print("⚠️  未找到任何字段")

except Exception as e:
    print(f"❌ 发生异常：{e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

print("=" * 60)
print("✅ 完成")
print("=" * 60)
