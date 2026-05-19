# -*- coding: utf-8 -*-
import sys, io, os, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

SCRIPT = """你有没有等过一个人，等到连时间都变慢了？

等一条消息等到翻来覆去，等一个人等到站酸了腿，等一个约定好的见面，等到心里又甜又慌？

今天想给你介绍一本书，它讲的就是这种感觉。

它就是法国绘本天后海贝卡的纸雕巅峰之作，《我等你》。

故事从一个约定开始，我们约定好中午12点见面，可是现在9点20，我已经开始等你了。

小兔子雅各在码头等待他的小甜心。他幻想着她可能会经过的地方，从卧室到花园，从面包店到市集。

200多页的纸雕，每翻一页就是一个全新的世界。立体的透视感让你感觉不是在看书，而是在看一部可以手动播放的电影。

短短3个小时的等待，前2小时55分钟全是他的想象。她会不会被邻居拦住，会不会赶不上，会不会忘了这个约定。只有最后5分钟，才是真实的故事。

这种叙事方式在电影里叫一镜到底，但这里是用纸雕做到的。

你知道吗，这本书的法文店名全部原文保留，翻到背面才有中文翻译。这是译者故意为之，让你可以先沉浸在法国小镇的氛围里，再慢慢读懂它。

豆瓣9.8分，读者说，这大概就是纸质书存在的意义。

一句我等你，远比我爱你更需要勇气。

把它递过去，什么都不用说，对方翻到最后一页，就会懂你的心意。"""

def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    print(f"获取token失败: {data}")
    return None

def get_records(token):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    resp = requests.get(url, headers=headers, params={"page_size": 100})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("data", {}).get("items", [])
    print(f"获取记录失败: {data}")
    return []

def update_record(token, record_id, fields):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    payload = {"fields": fields}
    resp = requests.put(url, headers=headers, json=payload)
    data = resp.json()
    if data.get("code") == 0:
        return True
    print(f"更新失败: {data}")
    return False

def main():
    print("=== 上传我等你文案到飞书 ===\n")

    # 获取 token
    token = get_access_token()
    if not token:
        return

    # 获取记录
    records = get_records(token)
    print(f"当前表格共有 {len(records)} 条记录\n")

    # 查找"我等你"记录
    wodayi_record = None
    for r in records:
        fields = r.get("fields", {})
        title = fields.get("选题标题", "")
        if "我等你" in str(title):
            wodayi_record = r
            print(f"找到记录: {title} (ID: {r.get('record_id')})")
            break

    if not wodayi_record:
        print("未找到'我等你'记录，请先在飞书中创建选题")
        return

    record_id = wodayi_record.get("record_id")

    # 更新口播文案
    print(f"\n上传口播文案到记录 {record_id}...")
    success = update_record(token, record_id, {"口播文案": SCRIPT})

    if success:
        print("✓ 口播文案上传成功！")
    else:
        print("✗ 口播文案上传失败")

if __name__ == "__main__":
    main()
