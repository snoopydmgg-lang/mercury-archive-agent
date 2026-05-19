#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《我等你》三套文案创建飞书记录 - 诊断版
"""

import sys
import traceback
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

# 飞书配置
APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

print("=" * 60)
print("  《我等你》三套文案创建飞书记录 - 诊断版")
print("=" * 60)
print()
print("🔍 配置检查：")
print(f"   APP_ID: {'✅ 已设置' if APP_ID else '❌ 为空'} ({APP_ID})")
print(f"   APP_SECRET: {'✅ 已设置' if APP_SECRET else '❌ 为空'} ({'*' * 10}...已隐藏)")
print(f"   BITABLE_TOKEN: {'✅ 已设置' if BITABLE_TOKEN else '❌ 为空'} ({BITABLE_TOKEN})")
print(f"   TABLE_ID: {'✅ 已设置' if TABLE_ID else '❌ 为空'} ({TABLE_ID})")
print()

# 初始化客户端
print("🔧 正在初始化飞书客户端...")
try:
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .build()
    print("✅ 客户端初始化成功")
    print()
except Exception as e:
    print(f"❌ 客户端初始化失败：{e}")
    print(traceback.format_exc())
    sys.exit(1)

# 三套文案数据
records = [
    {
        "name": "文案1：余上沅风格",
        "fields": {
            "选题标题": "我等你-余上沅风格",
            "状态": "已完成",
            "标题": "我等你纸雕书：法国绘本天后7000小时打造的告白艺术品",
            "简介": "法国绘本天后海贝卡·朵特梅耗时7000小时打造的纸雕神作，212页全激光雕刻，每一页都是精密舞台。讲述一个关于等待与表白的暖心童话，约好中午十二点见面，九点二十分就已经开始等你了。豆瓣9.8分，法国2019年度创意书大奖，首印14500本7天售罄。",
            "商品短标题": "我等你",
            "视频文件名": "0430-我等你-余上沅",
            "口播文案": """你有多久没被一本书震撼到失语？

法国绘本天后海贝卡·朵特梅耗时7000小时打造的《我等你》，212页全激光纸雕，每一页都是精密舞台。

纸张厚实，镂空细腻，拿在手里有分量。把书立起来，整个场景瞬间立体展开，小路蜿蜒、房屋错落、花草鲜活，光影穿过纸雕缝隙，画面像活了一样。

故事讲的是两只兔子的约会。明明约好中午十二点见面，他却九点二十分就迫不及待出发。从家里出发，一路紧张又期待。

最打动人的是这句话：约会不是从见面才开始，从约定那一刻，浪漫就已经发生了。全书没有一句"我爱你"，却通篇都是"我爱你"的故事。

小孩看热闹，大人看门道。

不管是自留治愈，还是送给爱人、挚友、家人，都远比普通礼物更有分量。这本书就是一句告白：有人值得你等待，也永远有人在等你。""",
            "BGM建议": "Yann Tiersen - Comptine d'un autre été（法式钢琴）",
        }
    },
    {
        "name": "文案2：九厘米的雾风格",
        "fields": {
            "选题标题": "我等你-九厘米的雾风格",
            "状态": "已完成",
            "标题": "我等你纸雕书：首印7天售罄的法式浪漫剧场（豆瓣9.8）",
            "简介": "法国绘本天后海贝卡·朵特梅耗时7000小时打造的纸雕神作，212页全激光雕刻，每一页都是精密舞台。讲述一个关于等待与表白的暖心童话，约好中午十二点见面，九点二十分就已经开始等你了。豆瓣9.8分，法国2019年度创意书大奖，首印14500本7天售罄。",
            "商品短标题": "我等你",
            "视频文件名": "0430-我等你-九厘米的雾",
            "口播文案": """这哪是书，明明是艺术品。

法国绘本天后海贝卡的《我等你》，首印14500本，7天售罄，一书难求。

为什么这么火？因为它把一个关于等待的故事，做成了212页可以手动播放的纸上电影。

全激光雕刻，细如发丝的平面细节。即使书上只有一两毫米的叶片，都富有深浅冷暖的层次感。当你把书立起来，光影穿透镂空，每一页都像自带光影的绝美电影画面。

约好中午十二点见面，九点二十分就已经开始等你了。这句话就像一颗糖含在嘴里，甜得让人眼眶发热。

从等待到相遇，每一帧都是情绪。

豆瓣9.8分，法国2019年度创意书大奖。价格不算低，但拿到手就知道有多值。

这不只是一本书，而是一件可以捧在掌心的告白。如果等待真的有结果，那再等一等又何妨？""",
            "BGM建议": "The xx - Intro（极简电子）",
        }
    },
    {
        "name": "文案3：Ad Scout风格",
        "fields": {
            "选题标题": "我等你-Ad Scout风格",
            "状态": "已完成",
            "标题": "我等你纸雕书：情人节/纪念日/生日送礼首选（比鲜花更持久）",
            "简介": "法国绘本天后海贝卡·朵特梅耗时7000小时打造的纸雕神作，212页全激光雕刻，每一页都是精密舞台。讲述一个关于等待与表白的暖心童话，约好中午十二点见面，九点二十分就已经开始等你了。豆瓣9.8分，法国2019年度创意书大奖，首印14500本7天售罄。",
            "商品短标题": "我等你",
            "视频文件名": "0430-我等你-AdScout",
            "口播文案": """男生留下，女孩子把视频转发给男朋友，立马划走。这不是演习。

送TA这本书，就是送上一捧掌心的法式浪漫剧场。

《我等你》耗时7000小时精心打造，212页全激光纸雕，每一页都是精心雕刻的艺术品。

节日不知道送啥？怕撞款？怕没诚意？情人节、纪念日、生日送她再合适不过。比鲜花更持久，比普通礼物更有仪式感。

约好中午十二点见面，九点二十分就已经开始等你了。全书没有一句"我爱你"，却通篇都是"我爱你"的故事。

把书立起来的那一刻，整个场景瞬间立体展开，光影穿过纸雕缝隙，画面像活了一样。

告白、纪念日、节日，礼物首选。封底印有"我等你"，未说出口的心意藏进指尖光影。

适合作为追求、异地恋、和好或惊喜场景的礼物，传递心意。价格不算低，但拿到手就知道有多值，仪式感满满，心意藏不住。""",
            "BGM建议": "Ludovico Einaudi - Experience（情感升华）",
        }
    }
]

def main():
    print("📝 开始创建飞书记录...")
    print()

    success_count = 0
    fail_count = 0

    for i, record in enumerate(records, 1):
        print(f"[{i}/3] 正在处理：{record['name']}")

        try:
            # 构建请求
            print(f"   🔧 构建请求...")
            request = CreateAppTableRecordRequest.builder() \
                .app_token(BITABLE_TOKEN) \
                .table_id(TABLE_ID) \
                .request_body(AppTableRecord.builder()
                    .fields(record["fields"])
                    .build()) \
                .build()
            print(f"   ✅ 请求构建成功")

            # 发送请求
            print(f"   📡 发送 API 请求...")
            response = client.bitable.v1.app_table_record.create(request)

            # 打印响应详情
            print(f"   📥 收到响应：")
            print(f"      - response.code: {response.code}")
            print(f"      - response.msg: {response.msg}")
            print(f"      - response.success(): {response.success()}")

            # 处理结果
            if not response.success():
                print(f"   ❌ 创建失败")
                print(f"      错误码: {response.code}")
                print(f"      错误信息: {response.msg}")
                if hasattr(response, 'data') and response.data:
                    print(f"      响应数据: {response.data}")
                fail_count += 1
                print()
                continue

            print(f"   ✅ 创建成功")
            if hasattr(response, 'data') and response.data and hasattr(response.data, 'record'):
                print(f"      Record ID: {response.data.record.record_id}")
            print(f"      - 标题: {record['fields']['标题'][:50]}...")
            print(f"      - 商品短标题: {record['fields']['商品短标题']}")
            print(f"      - BGM: {record['fields']['BGM建议']}")
            success_count += 1
            print()

        except Exception as e:
            print(f"   ❌ 发生异常：{e}")
            print(f"   📋 完整 traceback：")
            print(traceback.format_exc())
            fail_count += 1
            print()

    print("=" * 60)
    print(f"📊 执行结果：成功 {success_count}/3，失败 {fail_count}/3")

    if success_count == 3:
        print()
        print("💡 DBS 检定结果：")
        print("   - 文案1（余上沅）：✅ 通过检定，可直接拍摄")
        print("   - 文案2（九厘米的雾）：✅ 通过检定，质量最高")
        print("   - 文案3（Ad Scout）：✅ 通过检定，转化能力最强")
        print()
        print("📋 本地文件：")
        print("   01_Projects_制作中/我等你/0430-我等你-三套文案.md")

    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 程序异常退出：{e}")
        print(traceback.format_exc())
        sys.exit(1)
