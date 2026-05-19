"""
飞书待办编辑脚本 - 修改待办内容、备注、截止日期、优先级
用法:
  python feishu_todo_edit.py "原内容" "新内容"           # 修改内容
  python feishu_todo_edit.py "内容" --remark "备注"      # 添加备注
  python feishu_todo_edit.py "内容" --deadline "2026-03-20"  # 设置截止日期
  python feishu_todo_edit.py "内容" --priority "重要且紧急"  # 设置优先级
"""
import requests
import io
import sys
import re
from datetime import datetime

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


def find_record_by_content(token, content_keyword):
    """根据关键词查找记录"""
    records = get_all_records(token)
    if not records:
        return None

    # 精确匹配或模糊匹配
    for record in records:
        fields = record.get("fields", {})
        todo_content = fields.get("待办内容", "")
        if todo_content == content_keyword or content_keyword in todo_content:
            return record

    return None


def update_record(token, record_id, fields_data):
    """更新记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {"fields": fields_data}
    resp = requests.put(url, headers=headers, json=data)
    result = resp.json()

    if result.get("code") == 0:
        return True
    else:
        print(f"更新失败: {result.get('msg')}")
        return False


def list_todos(token):
    """列出所有待办供选择"""
    records = get_all_records(token)
    if not records:
        print("没有待办")
        return []

    print("\n当前待办列表：")
    print("-" * 60)
    for i, record in enumerate(records, 1):
        fields = record.get("fields", {})
        content = fields.get("待办内容", "")
        status = fields.get("状态", "待处理")
        priority = fields.get("优先级", "")
        deadline = fields.get("截止日期", "")
        print(f"{i}. {content} [{status}] 优先级:{priority} 截止:{deadline}")

    return records


def main():
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        sys.exit(1)

    # 解析参数
    args = sys.argv[1:]

    if not args:
        # 显示所有待办
        list_todos(token)
        return

    # 第一个参数是待办内容关键词
    content_keyword = args[0]

    # 查找记录
    record = find_record_by_content(token, content_keyword)
    if not record:
        print(f"未找到包含 '{content_keyword}' 的待办")
        # 显示所有待办供选择
        records = list_todos(token)
        if records:
            print(f"\n请使用完整待办内容或编号来指定")
        return

    record_id = record.get("record_id")
    fields = record.get("fields", {})
    current_content = fields.get("待办内容", "")

    print(f"找到待办: {current_content}")

    # 解析其他参数
    update_fields = {}

    i = 1
    while i < len(args):
        arg = args[i]

        if arg == "--remark" or arg == "-r":
            if i + 1 < len(args):
                update_fields["备注"] = args[i + 1]
                i += 2
            else:
                print("缺少备注内容")
                i += 1
        elif arg == "--deadline" or arg == "-d":
            if i + 1 < len(args):
                update_fields["截止日期"] = args[i + 1]
                i += 2
            else:
                print("缺少截止日期")
                i += 1
        elif arg == "--priority" or arg == "-p":
            if i + 1 < len(args):
                update_fields["优先级"] = args[i + 1]
                i += 2
            else:
                print("缺少优先级")
                i += 1
        else:
            # 认为是新内容
            update_fields["待办内容"] = arg
            i += 1

    if not update_fields:
        # 显示当前待办详情
        print("\n待办详情：")
        for k, v in fields.items():
            print(f"  {k}: {v}")
    else:
        # 执行更新
        print(f"更新内容: {update_fields}")
        if update_record(token, record_id, update_fields):
            print("✓ 更新成功")
        else:
            print("✗ 更新失败")


if __name__ == "__main__":
    main()
