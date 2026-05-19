"""
飞书待办表格读取脚本 - 读取待办事项
"""
import requests
import io
import sys
from datetime import datetime, timedelta

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


def format_date(date_str):
    """格式化日期"""
    if not date_str:
        return ""
    try:
        # 处理飞书日期格式
        if isinstance(date_str, str):
            return date_str[:10]  # 取前10位日期
        return str(date_str)
    except:
        return ""


def main(query_type="all"):
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        return []

    records = get_all_records(token)
    if not records:
        print("没有待办事项")
        return []

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    results = []

    for record in records:
        fields = record.get("fields", {})
        content = fields.get("待办内容", "")
        status = fields.get("状态")
        priority = fields.get("优先级")
        deadline = fields.get("截止日期")
        create_time = fields.get("创建时间")
        complete_time = fields.get("完成时间")

        # 跳过已完成的
        if status == "已完成":
            continue

        deadline_str = format_date(deadline)
        create_str = format_date(create_time)

        # 根据查询类型筛选
        if query_type == "today":
            # 查找今天截止或创建的
            if deadline_str and deadline_str[:10] == str(today):
                results.append({
                    "content": content,
                    "priority": priority,
                    "deadline": deadline_str,
                    "type": "今日截止"
                })
            elif create_str and create_str[:10] == str(today):
                results.append({
                    "content": content,
                    "priority": priority,
                    "deadline": deadline_str,
                    "type": "今日创建"
                })
        elif query_type == "tomorrow":
            if deadline_str and deadline_str[:10] == str(tomorrow):
                results.append({
                    "content": content,
                    "priority": priority,
                    "deadline": deadline_str,
                    "type": "明日截止"
                })
        elif query_type == "all":
            # 返回所有未完成的
            results.append({
                "content": content,
                "priority": priority,
                "deadline": deadline_str,
                "create_time": create_str
            })

    return results


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = main(query)

    if query == "all":
        print(f"所有待办事项 ({len(results)}条)：")
        print("-" * 50)
        for r in results:
            priority = r.get("priority", "")
            deadline = r.get("deadline", "无截止日期")
            print(f"• {r['content']} [{priority}] 截止:{deadline}")
    elif query == "today":
        print(f"今日待办 ({len(results)}条)：")
        for r in results:
            print(f"• {r['content']} [{r['type']}]")
    elif query == "tomorrow":
        print(f"明日待办 ({len(results)}条)：")
        for r in results:
            print(f"• {r['content']}")
