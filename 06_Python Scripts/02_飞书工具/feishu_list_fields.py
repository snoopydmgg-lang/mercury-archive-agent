#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出飞书多维表格的所有字段名
"""
import sys
import os
import traceback

# 修复 Windows 控制台编码问题
sys.stdout.reconfigure(encoding='utf-8')

from lark_oapi import Client
from lark_oapi.api.bitable.v1 import ListAppTableFieldRequest

# 飞书配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

print("=" * 60)
print("  飞书多维表格字段列表")
print("=" * 60)
print()

# 初始化客户端
try:
    print("🔧 正在初始化飞书客户端...")
    client = Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .build()
    print("✅ 客户端初始化成功")
    print()
except Exception as e:
    print(f"❌ 客户端初始化失败：{e}")
    print(traceback.format_exc())
    sys.exit(1)

# 获取字段列表
try:
    print("📡 正在获取字段列表...")
    request = ListAppTableFieldRequest.builder() \
        .app_token(BITABLE_TOKEN) \
        .table_id(TABLE_ID) \
        .page_size(100) \
        .build()

    response = client.bitable.v1.app_table_field.list(request)

    if not response.success():
        print(f"❌ 获取失败")
        print(f"   错误码: {response.code}")
        print(f"   错误信息: {response.msg}")
        sys.exit(1)

    print("✅ 获取成功")
    print()
    print("=" * 60)
    print("字段列表：")
    print("=" * 60)

    if response.data and response.data.items:
        for idx, field in enumerate(response.data.items, 1):
            print(f"{idx}. 字段名: {field.field_name}")
            print(f"   字段ID: {field.field_id}")
            print(f"   字段类型: {field.type}")
            print()
    else:
        print("⚠️  未找到任何字段")

except Exception as e:
    print(f"❌ 发生异常：{e}")
    print(traceback.format_exc())
    sys.exit(1)

print("=" * 60)
print("✅ 完成")
print("=" * 60)
