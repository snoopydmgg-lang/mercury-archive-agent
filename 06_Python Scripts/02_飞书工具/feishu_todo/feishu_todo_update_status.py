"""
飞书待办更新状态脚本
用法:
  python feishu_todo_update_status.py pending   # 改为待处理
  python feishu_todo_update_status.py completed # 改为已完成
  python feishu_todo_update_status.py paused   # 改为搁置
"""
import requests
import io
import sys

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 待办表格配置
BITABLE_TOKEN = "JkK5bAxKIaOlAZsgDLWcbkXznGh"
TABLE_ID = "tblMbieB62YUn7f4"

# 状态映射
STATUS_MAP = {
    "pending": "待处理",
    "completed": "已完成",
    "paused": "搁置"
}


def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
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


def update_record_status(token, record_id, new_status):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "fields": {
            "状态": new_status
        }
    }

    resp = requests.put(url, headers=headers, json=data)
    result = resp.json()
    return result.get("code") == 0


def main():
    if len(sys.argv) < 2:
        print("用法: python feishu_todo_update_status.py [pending|completed|paused]")
        sys.exit(1)

    status_type = sys.argv[1].lower()
    new_status = STATUS_MAP.get(status_type)

    if not new_status:
        print("无效的状态类型")
        sys.exit(1)

    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        sys.exit(1)

    records = get_all_records(token)
    if not records:
        print("没有待办")
        return

    # 找出需要更新的记录（状态不是目标的）
    target_records = [r for r in records if r.get("fields", {}).get("状态") != new_status]

    if not target_records:
        print(f"所有待办已经是 '{new_status}' 状态")
        return

    print(f"找到 {len(target_records)} 条待办，开始更新为 '{new_status}'...\n")

    for i, record in enumerate(target_records, 1):
        record_id = record.get("record_id")
        content = record.get("fields", {}).get("待办内容", "未知")
        old_status = record.get("fields", {}).get("状态", "")
        print(f"[{i}/{len(target_records)}] {content} [{old_status} -> {new_status}]", end=" ")

        if update_record_status(token, record_id, new_status):
            print("✓")
        else:
            print("✗")

    print("\n完成!")


if __name__ == "__main__":
    main()
