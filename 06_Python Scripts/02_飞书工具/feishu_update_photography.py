# -*- coding: utf-8 -*-
"""
摄影构图艺术 - 三套文案上传飞书
"""
import requests, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# 三套文案数据
RECORDS = [
    {
        "\u9009\u9898\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f - \u4f59\u4e0a\u6c85\u7684\u5947\u5999\u5c4b",
        "\u6807\u9898": "\u80cc\u4e86100\u4e2a\u6784\u56fe\u6cd5\u5219\uff0c\u4e3a\u4ec0\u4e48\u62cd\u51fa\u6765\u7684\u7167\u7247\u8fd8\u662f\u88ab\u79d2\u6740\uff1f",
        "\u5546\u54c1\u77ed\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f\uff1a\u4ece\u6280\u672f\u5230\u60c5\u611f\u7684\u7f8e\u5b66\u539f\u7406",
        "\u7b80\u4ecb": "\u63ed\u793a\u6444\u5f71\u80cc\u540e\u7684\u89c6\u89c9\u5fc3\u7406\u5b66\uff0c\u4ece\u60c5\u611f\u51fa\u53d1\u5012\u63a8\u6280\u672f\u9009\u62e9\u3002\u4e0d\u662f\u5de5\u5177\u4e66\uff0c\u800c\u662f\u7f8e\u5b66\u539f\u7406\u63a2\u8ba8\u3002\u5e03\u5217\u677e\u3001\u4e9a\u5f53\u65af\u90fd\u5728\u7528\u7684\u201c\u6d3b\u601d\u7ef4\u201d\uff0c\u5e2e\u4f60\u4ece\u201c\u6b63\u786e\u7684\u5e73\u5eb8\u201d\u5347\u7ea7\u5230\u201c\u60c5\u611f\u5171\u9e23\u201d\u3002#\u6444\u5f71\u6784\u56fe #\u89c6\u89c9\u5fc3\u7406\u5b66 #\u6444\u5f71\u7f8e\u5b66 #\u5e03\u5217\u677e #\u6444\u5f71\u4e66\u5355",
        "\u72b6\u6001": "\u5df2\u5b8c\u6210\u6587\u6848",
    },
    {
        "\u9009\u9898\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f - \u4e5d\u5398\u7c73\u7684\u96fe",
        "\u6807\u9898": "\u61c2\u9ec4\u91d1\u5206\u5272\u7684\u6444\u5f71\u5e08\uff0c\u62a5\u4ef7\u80fd\u6bd4\u4e0d\u61c2\u7684\u9ad8\u4e94\u500d",
        "\u5546\u54c1\u77ed\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f\uff1a\u6784\u56fe\u51b3\u5b9a\u5b9a\u4ef7\u6743",
        "\u7b80\u4ecb": "\u884c\u4e1a\u5185\u7684\u6f5c\u89c4\u5219\uff1a\u540c\u4e00\u573a\u666f\uff0c\u5e03\u5217\u677e\u88c1\u526a\u540e\u80fd\u536550\u4e07\u7f8e\u5143\uff0c\u666e\u901a\u6444\u5f71\u5e08\u7248\u672c\u53ea\u80fd\u53685000\u5757\u3002\u5dee\u7684\u4e0d\u662f\u76f8\u673a\uff0c\u662f\u8fd910\u5398\u7c73\u7684\u88c1\u526a\u3002\u4ece\u201c\u77e5\u9053\u600e\u4e48\u62cd\u201d\u5230\u201c\u77e5\u9053\u4e3a\u4ec0\u4e48\u8fd9\u4e48\u62cd\u201d\uff0c\u62a5\u4ef7\u6743\u5c31\u5728\u8fd9\u91cc\u9762\u3002#\u6444\u5f71\u5e08\u6da8\u4ef7 #\u6784\u56fe\u6280\u5de7 #\u6444\u5f71\u5b9a\u4ef7 #\u5546\u4e1a\u6444\u5f71 #\u6444\u5f71\u5e08\u5fc5\u8bfb",
        "\u72b6\u6001": "\u5df2\u5b8c\u6210\u6587\u6848",
    },
    {
        "\u9009\u9898\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f - Ad Scout",
        "\u6807\u9898": "\u62cd\u4e86\u4e00\u5343\u5f20\u7167\u7247\uff0c\u670b\u53cb\u5708\u8fd8\u662f\u6ca1\u4eba\u70b9\u8d5e\uff1f\u95ee\u9898\u5728\u8fd9",
        "\u5546\u54c1\u77ed\u6807\u9898": "\u6444\u5f71\u6784\u56fe\u827a\u672f\uff1a\u4ece\u6a21\u4eff\u5230\u521b\u9020\u7684\u5ba1\u7f8e\u5347\u7ea7",
        "\u7b80\u4ecb": "\u4f60\u548c\u5927\u5e08\u7684\u5dee\u8ddd\uff1a\u4e00\u4e2a\u5728\u590d\u5236\u6784\u56fe\u516c\u5f0f\uff0c\u4e00\u4e2a\u5728\u7528\u89c6\u89c9\u8bb2\u6545\u4e8b\u3002\u597d\u7167\u7247\u76844\u4e2a\u8981\u7d20\u91cc\uff0c\u6700\u540e\u4e00\u4e2a\u6700\u5173\u952e\u2014\u2014\u60c5\u611f\u5171\u9e23\u3002\u8fd9\u672c\u4e66\u4e0d\u662f\u5de5\u5177\u4e66\uff0c\u800c\u662f\u5e2e\u4f60\u5efa\u7acb\u81ea\u5df1\u7684\u6444\u5f71\u5ba1\u7f8e\u4f53\u7cfb\uff0c\u4ece\u201c\u6a21\u4eff\u201d\u5347\u7ea7\u5230\u201c\u521b\u9020\u201d\u3002#\u6444\u5f71\u8fdb\u9636 #\u5ba1\u7f8e\u63d0\u5347 #\u6444\u5f71\u601d\u7ef4 #\u6784\u56fe\u7f8e\u5b66 #\u6444\u5f71\u4e66\u63a8\u8350",
        "\u72b6\u6001": "\u5df2\u5b8c\u6210\u6587\u6848",
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
    print("  Photography Composition - Upload to Feishu")
    print("=" * 60)
    print()

    success_count = 0
    for i, record in enumerate(RECORDS, 1):
        print(f"[{i}/3] Uploading record {i}...")
        ok, result = create_record(token, record)
        if ok:
            print(f"  OK - {result}")
            success_count += 1
        else:
            print(f"  FAIL - {result}")
        print()

    print("=" * 60)
    print(f"Done: {success_count}/3 success")
    print("=" * 60)

if __name__ == "__main__":
    main()
