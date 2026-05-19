"""
解析飞书内容追踪表格，提取待发布的视频信息
"""
import json
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def get_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params={"page_size": 100})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    return []

token = get_token()
if not token:
    print("获取token失败")
    sys.exit(1)

records = get_records(token)
data = {"data": {"data": [r["fields"] for r in records]}}

# Field order: 0:状态, 1:日期, 2:画面脚本, 3:视频文件名, 4:口播文案, 5:配音链接, 6:选题标题, 7:BGM建议, 8:标题, 9:商品短标题, 10:辅助信息, 11:音效建议, 12:简介
records = data['data']['data']

print(f"=== 飞书内容追踪表格 - 共 {len(records)} 条记录 ===\n")

for i, r in enumerate(records):
    status = r.get('状态', '无状态')
    if isinstance(status, list):
        status = status[0] if status else '无状态'
    topic = r.get('选题标题', '无选题')  # 选题标题
    title = r.get('标题', '无标题')  # 标题
    video = r.get('视频文件名', '无视频')  # 视频文件名
    caption = r.get('简介', '')  # 简介

    print(f"{i+1}. [{status}] {topic}")
    print(f"   标题: {title}")
    print(f"   视频: {video}")
    # 提取话题
    hashtags = [w for w in caption.split() if w.startswith('#')]
    if hashtags:
        print(f"   话题: {' '.join(hashtags)}")
    print()