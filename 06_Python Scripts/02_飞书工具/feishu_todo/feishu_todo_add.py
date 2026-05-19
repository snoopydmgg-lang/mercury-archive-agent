"""
飞书待办事项添加脚本
用法: python feishu_todo_add.py "待办内容1" "待办内容2" "待办内容3"
"""
import requests
import json
import sys
import io
import os

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 待办表格配置
BITABLE_TOKEN = "JkK5bAxKIaOlAZsgDLWcbkXznGh"
TABLE_ID = "tblMbieB62YUn7f4"


def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        print(f"获取token失败: {data}")
        return None


def add_todo(token, todo_content):
    """添加待办事项"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 构建记录数据
    # 字段名需要根据实际创建的多维表格字段名来设置
    # 假设字段名为：待办内容、状态、创建时间
    record = {
        "fields": {
            "待办内容": todo_content,
            "状态": "待处理"
        }
    }

    resp = requests.post(url, headers=headers, json=record)
    data = resp.json()

    if data.get("code") == 0:
        print(f"✓ 添加成功: {todo_content}")
        return True
    else:
        print(f"✗ 添加失败: {data.get('msg')}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python feishu_todo_add.py \"待办内容1\" \"待办内容2\" ...")
        sys.exit(1)

    # 获取token
    token = get_tenant_access_token()
    if not token:
        sys.exit(1)

    # 逐个添加待办
    todos = sys.argv[1:]
    print(f"开始添加 {len(todos)} 个待办事项...\n")

    for i, todo in enumerate(todos, 1):
        print(f"[{i}/{len(todos)}]", end=" ")
        add_todo(token, todo)


if __name__ == "__main__":
    main()
