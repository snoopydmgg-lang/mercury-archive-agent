# -*- coding: utf-8 -*-
"""
摄影构图艺术 - 0427文案上传飞书（三套文案）
"""
import requests, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# 读取完整文案文件
script_file = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\摄影构图艺术\02_脚本_逻辑链\0427-摄影构图艺术-三套文案.md"

with open(script_file, "r", encoding="utf-8") as f:
    content = f.read()

# 提取三套文案的口播文案
# 风格1：余上沅的奇妙屋
oral_1_start = content.find("### 口播文案", content.find("## 文案1：余上沅的奇妙屋风格"))
oral_1_end = content.find("### 优化说明", oral_1_start)
oral_1 = content[oral_1_start+len("### 口播文案"):oral_1_end].strip()

# 风格2：九厘米的雾
oral_2_start = content.find("### 口播文案", content.find("## 文案2：九厘米的雾风格"))
oral_2_end = content.find("### 优化说明", oral_2_start)
oral_2 = content[oral_2_start+len("### 口播文案"):oral_2_end].strip()

# 风格3：Ad Scout
oral_3_start = content.find("### 口播文案", content.find("## 文案3：Ad Scout风格"))
oral_3_end = content.find("### 优化说明", oral_3_start)
oral_3 = content[oral_3_start+len("### 口播文案"):oral_3_end].strip()

# 提取画面脚本（从表格到BGM建议之前）
visual_1_start = content.find("| 时间 |", content.find("## 文案1：余上沅的奇妙屋风格"))
visual_1_end = content.find("### BGM建议", visual_1_start)
visual_1 = content[visual_1_start:visual_1_end].strip()

visual_2_start = content.find("| 时间 |", content.find("## 文案2：九厘米的雾风格"))
visual_2_end = content.find("### BGM建议", visual_2_start)
visual_2 = content[visual_2_start:visual_2_end].strip()

visual_3_start = content.find("| 时间 |", content.find("## 文案3：Ad Scout风格"))
visual_3_end = content.find("### BGM建议", visual_3_start)
visual_3 = content[visual_3_start:visual_3_end].strip()

RECORDS = [
    {
        "选题标题": "摄影构图艺术 - 余上沅",
        "标题": "同一个景点，为什么别人拍大片你拍游客照",
        "商品短标题": "摄影构图艺术",
        "简介": "职业摄影师和新手的差别，就在按快门前那3秒钟。豆瓣8.0分，376人评价。3个核心技巧：三分法、视线留白、前景框架。#摄影构图 #摄影技巧 #拍照技巧 #摄影书单",
        "BGM建议": "The Man Who Fell To Earth Main Theme",
        "音效建议": "低频Boom、翻页声、轻击音效、咔嚓声",
        "状态": "已完成文案",
        "口播文案": oral_1,
        "画面脚本": visual_1,
    },
    {
        "选题标题": "摄影构图艺术 - 九厘米的雾",
        "标题": "拍了一千张，朋友圈还是没人点赞",
        "商品短标题": "摄影构图艺术",
        "简介": "新手研究怎么拍，大师研究怎么看。不是在主动看东西，是被画面引导的。豆瓣8.0分。3个引导视线的方法。#摄影进阶 #构图美学 #视觉引导",
        "BGM建议": "Westworld - Ramin Djawadi",
        "音效建议": "低频Boom、翻页声、咔嚓声",
        "状态": "已完成文案",
        "口播文案": oral_2,
        "画面脚本": visual_2,
    },
    {
        "选题标题": "摄影构图艺术 - Ad Scout",
        "标题": "别瞎学构图！越学越废的人都踩了同一个坑",
        "商品短标题": "摄影构图艺术",
        "简介": "把构图当公式背，越学越废。构图不是技巧，是思维方式。豆瓣8.0分。3个核心技巧看完就懂。#摄影避坑 #构图思维 #摄影进阶",
        "BGM建议": "The Chain (Instrumental)",
        "音效建议": "冲击音效、翻页声、脉冲音效、咔嚓声",
        "状态": "已完成文案",
        "口播文案": oral_3,
        "画面脚本": visual_3,
    },
]

def get_token():
    resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                         json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def create_record(token, fields):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, headers=headers, json={"fields": fields})
    result = resp.json()
    if result.get("code") == 0:
        record_id = result["data"]["record"]["record_id"]
        return True, record_id
    else:
        return False, result

def main():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    print("=" * 60)
    print("  摄影构图艺术 0427 - 三套文案上传飞书")
    print("=" * 60)
    print()

    success_count = 0
    for i, record in enumerate(RECORDS, 1):
        title = record["选题标题"]
        print(f"[{i}/3] 上传中: {title}")
        ok, result = create_record(token, record)
        if ok:
            print(f"  ✓ 成功 - Record ID: {result}")
            success_count += 1
        else:
            print(f"  ✗ 失败 - {result}")
        print()

    print("=" * 60)
    print(f"上传完成: {success_count}/3 成功")
    print("=" * 60)

if __name__ == "__main__":
    main()
