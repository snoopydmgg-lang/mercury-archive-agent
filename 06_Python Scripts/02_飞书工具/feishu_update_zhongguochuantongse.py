# -*- coding: utf-8 -*-
"""
中国传统色 - 完整文案上传飞书（包含口播和画面脚本）
"""
import requests, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# 读取完整文案文件
import os
script_file = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\中国传统色\0504-中国传统色-三套文案.md"

with open(script_file, "r", encoding="utf-8") as f:
    content = f.read()

# 提取三套文案的口播和画面脚本
# 余上沅的奇妙屋
oral_1_start = content.find("### 口播文案", content.find("## 文案1：余上沅的奇妙屋风格"))
oral_1_end = content.find("### 优化说明", oral_1_start)
oral_1 = content[oral_1_start+len("### 口播文案"):oral_1_end].strip()

visual_1_start = content.find("### 画面脚本", content.find("## 文案1：余上沅的奇妙屋风格"))
visual_1_end = content.find("### BGM建议", visual_1_start)
visual_1 = content[visual_1_start+len("### 画面脚本"):visual_1_end].strip()

# 九厘米的雾
oral_2_start = content.find("### 口播文案", content.find("## 文案2：九厘米的雾风格"))
oral_2_end = content.find("### 优化说明", oral_2_start)
oral_2 = content[oral_2_start+len("### 口播文案"):oral_2_end].strip()

visual_2_start = content.find("### 画面脚本", content.find("## 文案2：九厘米的雾风格"))
visual_2_end = content.find("### BGM建议", visual_2_start)
visual_2 = content[visual_2_start+len("### 画面脚本"):visual_2_end].strip()

# Ad Scout
oral_3_start = content.find("### 口播文案", content.find("## 文案3：Ad Scout风格"))
oral_3_end = content.find("### 优化说明", oral_3_start)
oral_3 = content[oral_3_start+len("### 口播文案"):oral_3_end].strip()

visual_3_start = content.find("### 画面脚本", content.find("## 文案3：Ad Scout风格"))
visual_3_end = content.find("### BGM建议", visual_3_start)
visual_3 = content[visual_3_start+len("### 画面脚本"):visual_3_end].strip()

RECORDS = [
    {
        "选题标题": "中国传统色 - 余上沅的奇妙屋",
        "标题": "中国传统色：从400部古籍里考据出的384种颜色美学",
        "商品短标题": "传统色·配色",
        "简介": "郭浩耗时两年从近400部典籍中考据384种中国传统色，按24节气编排，192件故宫文物对应，每种标注CMYK+RGB色值，附赠全套色卡。",
        "BGM建议": "The Theory of Everything - Album Track",
        "音效建议": "翻页声、水滴声、钟声",
        "状态": "已完成文案",
        "口播文案": oral_1,
        "画面脚本": visual_1,
    },
    {
        "选题标题": "中国传统色 - 九厘米的雾",
        "标题": "中国传统色：设计师配色库缺少的384种千年方案",
        "商品短标题": "传统色·配色",
        "简介": "384种中国传统色，每种有文献出处和文化意境。24节气时间轴编排，192件故宫文物佐证，CMYK+RGB色值设计师直接可用，附赠全套色卡。",
        "BGM建议": "Westworld - Ramin Djawadi",
        "音效建议": "切换闪白、茶水声、钟声",
        "状态": "已完成文案",
        "口播文案": oral_2,
        "画面脚本": visual_2,
    },
    {
        "选题标题": "中国传统色 - Ad Scout",
        "标题": "中国传统色：你的配色库里少了384种经过千年验证的方案",
        "商品短标题": "传统色·配色",
        "简介": "潘通一年出一套流行色，这本书一次性给你384套中国传统配色方案。400部古籍考据，24节气编排，192件故宫文物对应，附赠全套色卡。",
        "BGM建议": "The Maw Of Normalcy",
        "音效建议": "快门声、花开声、钟声",
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

if __name__ == "__main__":
    token = get_token()
    print(f"✅ 获取 Token 成功")

    for i, record in enumerate(RECORDS, 1):
        success, result = create_record(token, record)
        if success:
            print(f"✅ 文案{i}（{record['选题标题']}）上传成功，Record ID: {result}")
        else:
            print(f"❌ 文案{i}（{record['选题标题']}）上传失败: {result}")

    print("\n📊 上传完成")
    print(f"   - 视频标题1：{RECORDS[0]['标题']}")
    print(f"   - 视频标题2：{RECORDS[1]['标题']}")
    print(f"   - 视频标题3：{RECORDS[2]['标题']}")
    print(f"   - 商品短标题：{RECORDS[0]['商品短标题']}")
