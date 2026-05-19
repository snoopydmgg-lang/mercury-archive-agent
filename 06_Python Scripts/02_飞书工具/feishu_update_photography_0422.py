# -*- coding: utf-8 -*-
"""
摄影构图艺术 - 0422文案上传飞书（风格2和风格3）
"""
import requests, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# 读取完整文案文件
script_file = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\摄影构图艺术\0422-摄影构图艺术-三套文案.md"

with open(script_file, "r", encoding="utf-8") as f:
    content = f.read()

# 提取风格2和风格3的口播文案
# 风格2：九厘米的雾
oral_2_start = content.find("### 口播文案", content.find("## 文案2：九厘米的雾风格"))
oral_2_end = content.find("### 优化说明", oral_2_start)
oral_2 = content[oral_2_start+len("### 口播文案"):oral_2_end].strip()

# 风格3：Ad Scout
oral_3_start = content.find("### 口播文案", content.find("## 文案3：Ad Scout风格"))
oral_3_end = content.find("### 优化说明", oral_3_start)
oral_3 = content[oral_3_start+len("### 口播文案"):oral_3_end].strip()

# 提取画面脚本（从表格到BGM建议之前）
visual_2_start = content.find("| 时间 |", content.find("## 文案2：九厘米的雾风格"))
visual_2_end = content.find("### BGM建议", visual_2_start)
visual_2 = content[visual_2_start:visual_2_end].strip()

visual_3_start = content.find("| 时间 |", content.find("## 文案3：Ad Scout风格"))
visual_3_end = content.find("### BGM建议", visual_3_start)
visual_3 = content[visual_3_start:visual_3_end].strip()

RECORDS = [
    {
        "\u9009\u9898\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f - \u4e5d\u5398\u7c73\u7684\u96fe",
        "\u6807\u9898": "\u540c\u4e00\u666f\u70b9\uff0c\u4e3a\u4ec0\u4e48\u522b\u4eba\u62cd\u5927\u7247\u4f60\u62cd\u6e38\u5ba2\u7167",
        "\u5546\u54c1\u77ed\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f\uff1a\u89c6\u89c9\u5fc3\u7406\u5b66\u62c6\u89e3",
        "\u7b80\u4ecb": "\u8c46\u74e38.0\u5206\u6444\u5f71\u4e66\uff0c\u804c\u4e1a\u6444\u5f71\u5e08\u628a\u89c6\u89c9\u5fc3\u7406\u5b66\u8bb2\u6210\u4eba\u8bdd\u3002\u6d4b\u8bd5\u4e00\u5468\uff0c\u670b\u53cb\u5708\u70b9\u8d5e\u4ece10\u4e2a\u6da8\u523050\u4e2a\u3002\u4ece\u201c\u77e5\u9053\u600e\u4e48\u62cd\u201d\u5230\u201c\u77e5\u9053\u4e3a\u4ec0\u4e48\u8fd9\u4e48\u62cd\u201d\u3002#\u6444\u5f71\u6784\u56fe #\u6444\u5f71\u6280\u5de7 #\u62cd\u7167\u6280\u5de7 #\u6444\u5f71\u4e66\u5355 #\u89c6\u89c9\u5fc3\u7406\u5b66",
        "BGM\u5efa\u8bae": "The xx - Intro",
        "\u97f3\u6548\u5efa\u8bae": "Boom\u97f3\u6548\u3001\u5feb\u95e8\u58f0\u3001\u51e0\u4f55\u97f3\u6548\u3001\u6570\u636e\u5f39\u51fa\u97f3\u3001\u5feb\u95e8\u58f0\uff08\u6162\uff09\u3001\u7b14\u89e6\u7ed8\u753b\u97f3",
        "\u72b6\u6001": "\u5df2\u5b8c\u6210\u6587\u6848",
        "\u53e3\u64ad\u6587\u6848": oral_2,
        "\u753b\u9762\u811a\u672c": visual_2,
    },
    {
        "\u9009\u9898\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f - Ad Scout",
        "\u6807\u9898": "\u62cd\u4e861000\u5f20\u7167\u7247\uff0c\u670b\u53cb\u5708\u8fd8\u662f\u6ca1\u4eba\u70b9\u8d5e",
        "\u5546\u54c1\u77ed\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f\uff1a\u4ece\u6a21\u4eff\u5230\u521b\u9020",
        "\u7b80\u4ecb": "\u6362\u4e86\u66f4\u8d35\u7684\u76f8\u673a\u3001\u5b66\u4e86\u4e09\u5206\u6cd5\uff0c\u7167\u7247\u8fd8\u662f\u5e73\u5e73\u65e0\u5947\uff1f\u5dee\u7684\u4e0d\u662f\u6280\u5de7\uff0c\u662f\u5ba1\u7f8e\u3002\u804c\u4e1a\u6444\u5f71\u5e08\u63ed\u793a\u597d\u7167\u7247\u6838\u5fc3\uff1a\u60c5\u611f\u5171\u9e23\u3002\u8c46\u74e38.0\u5206\u3002#\u6444\u5f71\u8fdb\u9636 #\u5ba1\u7f8e\u63d0\u5347 #\u6444\u5f71\u601d\u7ef4 #\u6784\u56fe\u7f8e\u5b66 #\u62cd\u7167\u8fdb\u9636",
        "BGM\u5efa\u8bae": "Experience - Ludovico Einaudi",
        "\u97f3\u6548\u5efa\u8bae": "Boom\u97f3\u6548\u3001\u7ffb\u9875\u97f3\u3001\u5c0f\u949f\u58f0\u3001\u653e\u5927/\u7f29\u5c0f\u97f3\u6548\u3001\u6570\u636e\u4e0a\u5347\u97f3\u3001\u56fe\u8868\u5f39\u51fa\u97f3\u3001\u786e\u8ba4\u63d0\u793a\u97f3",
        "\u72b6\u6001": "\u5df2\u5b8c\u6210\u6587\u6848",
        "\u53e3\u64ad\u6587\u6848": oral_3,
        "\u753b\u9762\u811a\u672c": visual_3,
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
    print("  Photography 0422 - Upload")
    print("=" * 60)
    print()

    success_count = 0
    for i, record in enumerate(RECORDS, 1):
        title = record["\u9009\u9898\u6807\u9898"]
        print(f"[{i}/2] Uploading: {title}")
        ok, result = create_record(token, record)
        if ok:
            print(f"  OK - Record ID: {result}")
            success_count += 1
        else:
            print(f"  FAIL - {result}")
        print()

    print("=" * 60)
    print(f"Done: {success_count}/2")
    print("=" * 60)

if __name__ == "__main__":
    main()
