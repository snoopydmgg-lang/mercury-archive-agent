"""
飞书选品追踪表格创建脚本
用法: python feishu_create_selection_table.py
"""
import requests
import json
import sys

# 飞书应用配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"

# 获取 tenant_access_token
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=data)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        print(f"获取token失败: {result}")
        sys.exit(1)

# 创建多维表格
def create_bitable(token, name):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "default_view_name": "默认视图"
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    print(f"创建多维表格响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    if result.get("code") == 0:
        # 多维表格创建成功，返回的 app_token 在 data.app.app_token
        return result.get("data", {}).get("app", {}).get("app_token")
    else:
        print(f"创建表格失败: {result}")
        sys.exit(1)

# 创建表格字段
def create_fields(token, app_token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
    headers = {"Authorization": f"Bearer {token}"}

    # 定义字段
    fields = [
        {"field_name": "产品名称", "type": 1},  # 文本
        {"field_name": "商品链接", "type": 10},  # 链接
        {"field_name": "客单价", "type": 2},  # 数字
        {"field_name": "佣金率", "type": 2},  # 数字
        {"field_name": "近30天销量", "type": 2},  # 数字
        {"field_name": "短视频出单占比", "type": 2},  # 数字
        {"field_name": "商家体验分", "type": 2},  # 数字
        {"field_name": "好评率", "type": 2},  # 数字
        {"field_name": "达人榜前三占比", "type": 2},  # 数字
        {"field_name": "昨日转化率", "type": 2},  # 数字
        {"field_name": "出单达人数", "type": 2},  # 数字
        {"field_name": "综合评分", "type": 2},  # 数字（公式）
        {"field_name": "数据来源", "type": 3, "options": {"options": [{"name": "灰豚数据"}, {"name": "精选联盟"}]}},  # 单选
        {"field_name": "跟进状态", "type": 3, "options": {"options": [{"name": "待筛选"}, {"name": "待下单"}, {"name": "已下单"}, {"name": "已拍摄"}, {"name": "已发布"}, {"name": "已放弃"}]}},  # 单选
        {"field_name": "选品理由", "type": 1},  # 文本
        {"field_name": "备注", "type": 1},  # 文本
        {"field_name": "创建时间", "type": 5},  # 日期
    ]

    # 创建表格
    table_data = {
        "table_name": "选品追踪"
    }
    response = requests.post(url, headers=headers, json=table_data)
    result = response.json()
    print(f"创建表格响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if result.get("code") == 0:
        table_id = result.get("data", {}).get("table_id")
        print(f"表格创建成功，table_id: {table_id}")
    else:
        print(f"创建表格失败: {result}")
        # 尝试获取已存在的表格
        get_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
        response = requests.get(get_url, headers=headers)
        result = response.json()
        if result.get("code") == 0 and result.get("data", {}).get("items"):
            table_id = result["data"]["items"][0]["table_id"]
            print(f"使用已有表格，table_id: {table_id}")
        else:
            sys.exit(1)

    # 添加字段
    base_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"

    field_definitions = [
        {"name": "产品名称", "type": 1},
        {"name": "商品链接", "type": 10},
        {"name": "客单价", "type": 2},
        {"name": "佣金率", "type": 2},
        {"name": "近30天销量", "type": 2},
        {"name": "短视频出单占比", "type": 2},
        {"name": "商家体验分", "type": 2},
        {"name": "好评率", "type": 2},
        {"name": "达人榜前三占比", "type": 2},
        {"name": "昨日转化率", "type": 2},
        {"name": "出单达人数", "type": 2},
        {"name": "数据来源", "type": 3, "options": ["灰豚数据", "精选联盟"]},
        {"name": "跟进状态", "type": 3, "options": ["待筛选", "待下单", "已下单", "已拍摄", "已发布", "已放弃"]},
        {"name": "选品理由", "type": 1},
        {"name": "备注", "type": 1},
        {"name": "创建时间", "type": 5},
    ]

    for field in field_definitions:
        field_data = {"field_name": field["name"], "type": field["type"]}

        if "options" in field:
            # 单选字段
            options_list = [{"name": opt} for opt in field["options"]]
            field_data["properties"] = {"options": options_list}

        response = requests.post(base_url, headers=headers, json=field_data)
        result = response.json()
        if result.get("code") == 0:
            print(f"  添加字段成功: {field['name']}")
        else:
            print(f"  添加字段失败: {field['name']} - {result.get('msg')}")

    return table_id

# 添加公式字段
def add_formula_field(token, app_token, table_id):
    """添加综合评分公式字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}

    # 公式：基于必填项和加分项计算综合评分
    # 飞书公式语法使用字段名
    formula = '''IF(AND({近30天销量}>=5000,{短视频出单占比}>=50,{商家体验分}>=85),IF({佣金率}>=20,2,0)+IF(AND({客单价}>=9.9,{客单价}<=29.9),1,0)+IF({好评率}>=85,1,0)+IF({达人榜前三占比}<80,1,0)+IF({昨日转化率}>=15,1,0)+IF({出单达人数}<500,1,0),0)'''

    field_data = {
        "field_name": "综合评分",
        "type": 4,  # 公式
        "properties": {
            "formula": formula,
            "result_type": 2  # 返回数字
        }
    }

    response = requests.post(url, headers=headers, json=field_data)
    result = response.json()
    print(f"添加公式字段响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if result.get("code") == 0:
        print("公式字段添加成功")
    else:
        print(f"公式字段添加失败: {result.get('msg')}")

def main():
    print("=== 飞书选品追踪表格创建工具 ===\n")

    # 1. 获取token
    print("1. 获取 tenant_access_token...")
    token = get_tenant_token()
    print(f"   Token获取成功\n")

    # 2. 创建多维表格
    print("2. 创建多维表格...")
    app_token = create_bitable(token, "选品追踪")
    print(f"   多维表格创建成功，app_token: {app_token}\n")

    # 3. 创建表格和字段
    print("3. 创建表格和字段...")
    table_id = create_fields(token, app_token)
    print(f"   表格创建成功，table_id: {table_id}\n")

    # 4. 添加公式字段
    print("4. 添加公式字段...")
    add_formula_field(token, app_token, table_id)

    # 5. 输出结果
    print("\n=== 创建完成 ===")
    print(f"多维表格链接: https://my.feishu.cn/base/HfMebjb5Va2Z0ws4ZiDcOSMmnmb?table={app_token}&view=vewxxx")
    print(f"App Token: {app_token}")
    print(f"Table ID: {table_id}")

if __name__ == "__main__":
    main()
