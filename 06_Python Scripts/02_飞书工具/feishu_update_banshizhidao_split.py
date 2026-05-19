#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
版式之道 - 三套文案分别上传到飞书
将三套文案拆分为三条独立记录
"""

import requests
import json
import time
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 飞书配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
APP_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
    raise Exception(f"获取 token 失败: {response.text}")

def add_record(token, fields):
    """添加一条记录到飞书多维表格"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {"fields": fields}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            # 修复：正确提取 record_id
            record_data = result.get("data", {})
            if isinstance(record_data, dict):
                record = record_data.get("record", {})
                return record.get("record_id")
            return record_data
    raise Exception(f"添加记录失败: {response.text}")

# 三套文案数据
copywriting_data = [
    {
        "style": "余上沅风格",
        "title": "留白九成的海报，才是最难的部分",
        "intro": "18位日本设计大师，把版式逻辑拆成77种可复用策略。留白空间感、网格系统、CRAP原则——版式是方法论，不是灵感集。#版式设计 #平面设计 #留白美学 #日本设计 #设计师必备",
        "product_title": "版式之道",
        "script": """一张海报，留白占了九成——你觉得没设计完，大师说这是最难的部分。

18位日本设计大师，古平正义、平野甲贺、服部一成……把版式逻辑拆成了77种可复用的策略，锁进这本《版式之道》。

留白空间感——日本设计师的留白比例高达60%到70%，那些"空"的地方，恰恰是按秒计费的。

网格系统——不是创意决定你的报价，是网格系统。6大创意风格，77种版式策略，每一种都是可以复刻的方法论。

CRAP原则——对比、重复、对齐、亲密性，四把钥匙，打开视觉层级的秘密。

212页，70余个经典设计案例，留白哲学、几何交错感、复古意向感、秩序明镜感。

平面设计最大的谎言是：越满越用心。

这本书告诉你的是——版式，从来都是方法论，不是灵感集。

《版式之道》，善本图书出品，18位大师亲自指导。""",
        "visual_script": """| 时间轴 | 画面描述 | 字幕 | BGM/音效 |
|--------|----------|------|----------|
| 0-3s | 黑底白字大字幕冲击出现："留白九成，才是最难的部分" | 一张海报留白占了九成 | 低频Boom音效 |
| 3-8s | 书籍封面特写，镜头缓慢推进 | 《版式之道》 | 钢琴单音轻入 |
| 8-15s | 大师名字依次出现，配合日式极简版面 | 18位日本设计大师 / 77种可复用策略 | 钢琴旋律 |
| 15-25s | 三个核心概念依次展示：留白/网格/CRAP | 留白空间感 / 网格系统 / CRAP原则 | 木鱼音效（间隔） |
| 25-35s | 快速翻页展示内页案例 | 212页 / 70余个经典案例 | 翻页声加快 |
| 35-45s | 白底黑字金句定格 | 平面设计最大的谎言：越满越用心 | 音乐降至30% |
| 45-55s | 书籍封面正面特写 | 版式是方法论，不是灵感集 | 钢琴渐强 |
| 55-60s | 善本图书logo + 引导文字 | 善本图书出品 / 18位大师亲自指导 | 淡出 |""",
        "bgm": "Satie - Gymnopédie No. 1（极简钢琴，BPM约72）"
    },
    {
        "style": "九厘米风格",
        "title": "留白是按秒计费的",
        "intro": "日本设计师留白比例高达六七成，报价比堆满的高三倍。网格系统决定设计报价，从来不是创意。野路子和科班的差距——版式之道。#版式设计 #排版设计 #日本设计 #审美提升 #干货分享",
        "product_title": "版式之道",
        "script": """平面设计最大的谎言：越满越用心。

日本设计师的留白比例，往往高达六七成。你以为没设计完，他们说——这是报价最高的部分。

留白是按秒计费的。网格系统决定设计报价，从来不是创意。

《版式之道》，18位日本设计大师亲自指导，6大创意风格，77种版式策略，70余个经典案例，212页精印内容。

留白空间感、高级反差感、几何交错感、手绘活泼感、复古意向感、秩序明镜感——六种风格，每一种都是一套完整的设计语言。

古平正义、平野甲贺、服部一成……18位大师，把网格系统、视觉层级、版心率、CRAP原则，拆成带坐标的解剖报告，放进这212页里。

野路子和科班平面设计师的差距，从来不在技术、设备，在于有没有掌握版式之道。

善本图书出品，豆瓣高分收录。

你的下一张作品，值得一套真正的方法论。""",
        "visual_script": """| 时间轴 | 画面描述 | 字幕 | BGM/音效 |
|--------|----------|------|----------|
| 0-3s | 黑底白字缓缓浮现，雾气粒子飘动 | 平面设计最大的谎言 | 纸张摩擦声 |
| 4-8s | 极简版式：大面积空白，一行文字居中 | 越满越用心 | 低沉纸页翻动 |
| 9-14s | 数字"60%-70%"淡入，雾感叠加 | 留白比例高达六七成 | 环境白噪音 |
| 15-22s | 书籍封面从雾中显现，镜头环绕 | 18位大师 / 6大风格 / 77种策略 | 钢琴极简 |
| 23-32s | 六大风格关键词依次呈现，快切 | 留白空间感 / 几何交错感 / 复古意向感 | 轻微'嗒'声 |
| 33-42s | 内页翻阅特写，网格线标注 | 带坐标的解剖报告 | 纸张声 |
| 43-50s | 黑底白字缓入 | 野路子与科班的差距——版式之道 | 音乐降低 |
| 51-55s | 善本logo + 豆瓣评分，雾气散开 | 善本图书 / 豆瓣高分 | 淡出至静默 |""",
        "bgm": "坂本龙一极简钢琴系列（BPM 60-75，低频留空间感）"
    },
    {
        "style": "Ad Scout风格",
        "title": "为什么你的海报总像路边摊牛皮癣？",
        "intro": "字塞满、颜色堆满、元素全上——客户还是说不够专业。日本顶级设计师留白比例高达六七成，报价比堆满的高三倍。你缺的不是软件技巧，是版式之道。#版式设计 #平面设计 #设计师必备 #留白美学 #干货分享",
        "product_title": "版式之道",
        "script": """为什么你做的海报总像路边摊上的牛皮癣？

字塞满了、颜色堆满了、元素全上了——客户还是说"不够专业"。

平面设计最大的谎言，就是越满越用心。

日本顶级设计师留白比例高达六七成，报价比堆满的高三倍。

版式，从来不是为了好看——是为了定价。

《版式之道》，18位日本设计大师亲自指导，6大创意风格，77种版式策略，70余个经典案例，212页精印。

留白空间感、高级反差感、几何交错感——每一种风格背后都有可复用的底层逻辑。

网格系统、视觉层级、CRAP原则，这些才是科班设计师和野路子之间真正的墙。

留白是按秒计费的。

网格系统决定设计报价，不是创意。

善本图书出品，豆瓣高分收录。

你缺的不是软件技巧，是版式之道。""",
        "visual_script": """| 时间轴 | 画面描述 | 字幕 | BGM/音效 |
|--------|----------|------|----------|
| 0-3s | 极简海报特写，中央一行细小文字 | 为什么你做的海报总像牛皮癣？ | 静音2秒 |
| 3-8s | 快切对比：满版花哨 vs 日式极简 | 字塞满/颜色堆满/元素全上 | 震动切换音效 |
| 8-15s | 书籍封面推进，手指翻页慢动作 | 平面设计最大的谎言 | 翻页质感音 |
| 15-22s | 数字逐帧跳出，单独占屏 | 18位/6大/77种/70余/212页 | 短促'咔'声 |
| 22-30s | 六大风格关键词 + 版面截图快闪 | 留白空间感 / 高级反差感 / 几何交错感 | 胶片过帧声 |
| 30-40s | 网格线动效覆盖，箭头标注 | 网格系统 / 视觉层级 / CRAP原则 | 低频节拍 |
| 40-50s | 书籍封面全景 + logo | 善本图书 / 豆瓣高分 | 音乐持续 |
| 50-60s | 黑底白字大字幕定格 | 留白是按秒计费的 | 静音0.5秒后淡出 |""",
        "bgm": "Nujabes轻量级器乐或Lo-fi Japan风（低频稳定节拍，克制有力）"
    }
]

def main():
    print("=" * 60)
    print("版式之道 - 三套文案分别上传到飞书")
    print("=" * 60)

    # 获取 token
    print("\n[1/4] 获取飞书 access token...")
    token = get_tenant_access_token()
    print("✓ Token 获取成功")

    # 逐条上传
    for idx, data in enumerate(copywriting_data, 1):
        print(f"\n[{idx+1}/4] 上传文案 {idx}: {data['style']}")
        print(f"  标题: {data['title']} ({len(data['title'])}字符)")
        print(f"  商品短标题: {data['product_title']} ({len(data['product_title'])}字符)")

        fields = {
            "选题标题": f"版式之道-{data['style']}",
            "标题": data["title"],
            "简介": data["intro"],
            "商品短标题": data["product_title"],
            "口播文案": data["script"],
            "画面脚本": data["visual_script"],
            "BGM建议": data["bgm"],
            "音效建议": "详见画面脚本表格",
            "状态": "待拍摄"
        }

        try:
            result = add_record(token, fields)
            print(f"  ✓ 上传成功，记录ID: {result.get('record_id')}")
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f"  ✗ 上传失败: {str(e)}")

    print("\n" + "=" * 60)
    print("上传完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
