"""
飞书待办事项删除脚本
用法:
  python feishu_todo_delete.py all          # 删除所有待办
  python feishu_todo_delete.py pending      # 删除待处理的
  python feishu_todo_delete.py completed   # 删除已完成的
  python feishu_todo_delete.py paused      # 删除搁置的
"""
import requests
import json
import sys
import io

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 待办表格配置
BITABLE_TOKEN = "JkK5bAxKIaOlAZsgDLWcbkXznGh"
TABLE_ID = "tblMbieB62YUn7f4"


def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    else:
        print(f"获取token失败: {data}")
        return None


def get_all_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}

    all_records = []
    page_token = None

    while True:
        params = {"page_size": 100}
        if page_token:
            params["page_token"] = page_token

        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()

        if data.get("code") == 0:
            all_records.extend(data.get("data", {}).get("items", []))
            page_token = data.get("data", {}).get("page_token")
            if not page_token:
                break
        else:
            print(f"获取记录失败: {data.get('msg')}")
            return None

    return all_records


def delete_record(token, record_id):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    data = resp.json()
    return data.get("code") == 0


def main():
    if len(sys.argv) < 2:
        print("用法: python feishu_todo_delete.py [all|pending|completed|paused]")
        print("  all        - 删除所有待办")
        print("  pending    - 删除待处理的")
        print("  completed  - 删除已完成的")
        print("  paused     - 删除搁置的")
        sys.exit(1)

    delete_type = sys.argv[1].lower()

    # 状态映射
    status_map = {
        "pending": "待处理",
        "completed": "已完成",
        "paused": "搁置"
    }

    target_status = status_map.get(delete_type)

    # 获取token
    token = get_tenant_access_token()
    if not token:
        sys.exit(1)

    # 获取所有记录
    print("获取所有记录...")
    records = get_all_records(token)
    if not records:
        print("没有记录需要删除")
        return

    # 根据类型筛选
    if delete_type == "all":
        target_records = records
    else:
        target_records = [r for r in records if r.get("fields", {}).get("状态") == target_status]

    if not target_records:
        print(f"没有需要删除的待办（类型: {delete_type}）")
        return

    print(f"找到 {len(target_records)} 条记录，开始删除...\n")

    # 逐个删除
    for i, record in enumerate(target_records, 1):
        record_id = record.get("record_id")
        fields = record.get("fields", {})
        content = fields.get("待办内容", "未知")
        status = fields.get("状态", "")
        print(f"[{i}/{len(target_records)}] 删除: {content} [{status}]", end=" ")
        if delete_record(token, record_id):
            print("✓")
        else:
            print("✗")

    print("\n完成!")


if __name__ == "__main__":
    main()
