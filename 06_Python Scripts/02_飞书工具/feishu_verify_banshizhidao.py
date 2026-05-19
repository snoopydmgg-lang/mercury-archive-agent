#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证版式之道三套文案是否成功上传到飞书
"""

import requests
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
APP_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
    raise Exception(f"获取 token 失败: {response.text}")

def list_records(token):
    """列出所有记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {}).get("items", [])
    raise Exception(f"获取记录失败: {response.text}")

def main():
    print("=" * 60)
    print("验证版式之道三套文案上传结果")
    print("=" * 60)

    # 获取 token
    print("\n[1/2] 获取飞书 access token...")
    token = get_tenant_access_token()
    print("✓ Token 获取成功")

    # 获取记录
    print("\n[2/2] 读取飞书表格记录...")
    records = list_records(token)
    print(f"✓ 共找到 {len(records)} 条记录")

    # 筛选版式之道相关记录
    print("\n" + "=" * 60)
    print("版式之道相关记录：")
    print("=" * 60)

    banshi_records = []
    for record in records:
        fields = record.get("fields", {})
        title = fields.get("选题标题", "")
        if "版式之道" in title:
            banshi_records.append(record)
            print(f"\n记录ID: {record.get('record_id')}")
            print(f"  选题标题: {fields.get('选题标题', 'N/A')}")
            print(f"  标题: {fields.get('标题', 'N/A')}")
            print(f"  商品短标题: {fields.get('商品短标题', 'N/A')}")
            print(f"  状态: {fields.get('状态', 'N/A')}")
            print(f"  简介: {fields.get('简介', 'N/A')[:50]}...")

    print("\n" + "=" * 60)
    print(f"总计：{len(banshi_records)} 条版式之道记录")
    print("=" * 60)

if __name__ == "__main__":
    main()
