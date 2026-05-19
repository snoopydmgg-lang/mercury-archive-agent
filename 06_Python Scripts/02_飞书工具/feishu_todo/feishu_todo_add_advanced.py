"""
飞书待办高级添加脚本 - 支持设置截止日期和优先级
用法:
  python feishu_todo_add_advanced.py "待办内容" -d "2026-03-20" -p "重要且紧急"
  python feishu_todo_add_advanced.py "待办1" "待办2" -d "2026-03-20"
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


def add_todo(token, content, deadline=None, priority=None, remark=None):
    """添加待办"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    fields = {
        "待办内容": content,
        "状态": "待处理"
    }

    if deadline:
        # 转换为Unix时间戳（毫秒）
        try:
            dt = datetime.strptime(deadline, "%Y-%m-%d")
            fields["截止日期"] = int(dt.timestamp() * 1000)
        except:
            fields["截止日期"] = deadline
    if priority:
        fields["优先级"] = priority
    if remark:
        fields["备注"] = remark

    data = {"fields": fields}
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()

    if result.get("code") == 0:
        print(f"✓ 添加成功: {content}", end="")
        if priority:
            print(f" [{priority}]", end="")
        if deadline:
            print(f" 截止:{deadline}", end="")
        print()
        return True
    else:
        print(f"✗ 添加失败: {result.get('msg')}: {content}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python feishu_todo_add_advanced.py \"待办1\" \"待办2\" -d \"2026-03-20\" -p \"重要且紧急\" -r \"备注\"")
        print("  -d, --deadline 截止日期 (格式: 2026-03-20)")
        print("  -p, --priority 优先级 (重要且紧急/重要不紧急/紧急不重要/不重要不紧急)")
        print("  -r, --remark   备注")
        sys.exit(1)

    # 解析参数
    args = sys.argv[1:]
    todos = []
    deadline = None
    priority = None
    remark = None

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ["-d", "--deadline"]:
            if i + 1 < len(args):
                deadline = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ["-p", "--priority"]:
            if i + 1 < len(args):
                priority = args[i + 1]
                i += 2
            else:
                i += 1
        elif arg in ["-r", "--remark"]:
            if i + 1 < len(args):
                remark = args[i + 1]
                i += 2
            else:
                i += 1
        else:
            # 认为是待办内容
            todos.append(arg)
            i += 1

    if not todos:
        print("请输入待办内容")
        sys.exit(1)

    # 获取token
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        sys.exit(1)

    print(f"开始添加 {len(todos)} 个待办...\n")

    for todo in todos:
        add_todo(token, todo, deadline, priority, remark)


if __name__ == "__main__":
    main()
