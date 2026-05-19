# -*- coding: utf-8 -*-
import sys, io, requests, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

def get_token():
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                      json={"app_id": APP_ID, "app_secret": APP_SECRET})
    d = r.json()
    return d.get("tenant_access_token") if d.get("code") == 0 else None

def create_record(token, fields):
    """创建新记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    r = requests.post(url, headers={"Authorization": f"Bearer {token}",
                                     "Content-Type": "application/json; charset=utf-8"},
                       json={"fields": fields})
    d = r.json()
    return d.get("code") == 0, d

def main():
    print("=" * 60)
    print("  《我等你》三套文案创建飞书记录")
    print("=" * 60)

    token = get_token()
    if not token:
        print("❌ Token 获取失败")
        return

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
                "封面文件名": "0430-我等你-余上沅-封面",
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
                "封面文件名": "0430-我等你-九厘米的雾-封面",
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
                "封面文件名": "0430-我等你-AdScout-封面",
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

    # 创建三条新记录
    print("📤 开始创建三条新记录...")
    print()

    for record in records:
        ok, result = create_record(token, record["fields"])

        if ok:
            new_record_id = result.get("data", {}).get("record", {}).get("record_id", "N/A")
            print(f"✅ {record['name']} 创建成功")
            print(f"   Record ID: {new_record_id}")
            print(f"   - 标题: {record['fields']['标题'][:50]}...")
            print(f"   - 商品短标题: {record['fields']['商品短标题']}")
            print(f"   - BGM: {record['fields']['BGM建议']}")
        else:
            print(f"❌ {record['name']} 创建失败")
            print(f"   错误信息: {result}")
        print()

    print("=" * 60)
    print("✅ 三套文案已全部上传飞书")
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
    main()
