"""
飞书待办表格查看脚本 - 查看表格字段
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


def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    return None


def get_table_fields(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return None


def main():
    token = get_tenant_access_token()
    if not token:
        print("获取token失败")
        return

    fields = get_table_fields(token)
    if fields:
        print("表格字段列表：")
        print("-" * 40)
        for f in fields:
            field_name = f.get("field_name")
            field_type = f.get("type")
            # 字段类型映射
            type_map = {
                1: "单行文本",
                2: "多行文本",
                3: "数字",
                4: "单选",
                5: "多选",
                6: "日期",
                7: "复选框",
                10: "链接",
                11: "成员",
                12: "文件",
                13: "图片",
                15: "地理位置",
                17: "关联",
                18: "公式",
                20: "统计",
                21: "分段器"
            }
            type_name = type_map.get(field_type, str(field_type))
            print(f"• {field_name} ({type_name})")
    else:
        print("获取字段失败")


if __name__ == "__main__":
    main()
