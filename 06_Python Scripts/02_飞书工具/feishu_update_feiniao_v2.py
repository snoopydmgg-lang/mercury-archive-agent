# -*- coding: utf-8 -*-
"""
飞鸟集标题/简介迭代脚本
基于 DBS 内容诊断结论：
  - 版本1、4都走翻译历史 → 版本4改走「护封工艺设计哲学」新路线
  - 版本2、3、5保持高水准，改进CTA
  - 结尾CTA统一改为「翻到最后一页，你想到的是谁？」等身份认同型
"""
import sys, io, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    data = resp.json()
    if data.get("code") == 0:
        return data.get("tenant_access_token")
    print("获取token失败:", data)
    return None

def update_record(token, record_id, fields):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    resp = requests.put(url, headers=headers, json={"fields": fields})
    data = resp.json()
    if data.get("code") == 0:
        return True
    print(f"更新 {record_id} 失败:", data)
    return False

# 飞书 record_id
RECORDS = {
    # 余上沅-已发布
    "recvf3IcP0oSJr": {
        "title": "！郑振铎1922年翻译，至今无人超越？",
        "intro": "泰戈尔《飞鸟集》，郑振铎用白话散文诗翻译——开创白话译诗先河，奠定近百年经典地位。商务印书馆布面精装，天空蓝三面刷边，羽毛编码限量，一书一码。翻到最后一页，你想到的是谁？",
        "product": "飞鸟集羽毛编码布面精装版"
    },
    # 九厘米的雾-已发布
    "recvf3IdqAQGRJ": {
        "title": "？地铁刷短视频的人，永远不懂"生如夏花"！",
        "intro": "泰戈尔《飞鸟集》刷边版，440克巴掌本，三面天空蓝刷边，每本轨迹不同——不是印刷品，是握在手里的精神雕塑。28克薄纸专色印刷，翻页能感受纸张呼吸。羽毛编码限量，错过即绝版。翻到最后一页，你想到的是谁？",
        "product": "飞鸟集刷边绝版"
    },
    # Ad Scout-已发布
    "recvf3IdXsp0I6": {
        "title": "！亚洲首位诺奖得主，竟被误读100年？",
        "intro": "你以为《飞鸟集》只是鸡汤？1913年诺奖、1922年白话翻译开创先河。叶芝说它能忘却世间痛苦，但更狠的是——诗训练的是感受力，而不是背诵能力。布面精装、每本羽毛编码独一无二。下次有人说读诗没用，把这条转给他。",
        "product": "飞鸟集羽毛编码绝版"
    },
    # 风格1-待发布（改走「护封工艺设计哲学」全新路线）
    "recvghqKBe8tSY": {
        "title": "？这本书的护封设计，99%的人都没注意到？",
        "intro": "《飞鸟集》护封上随机分布的金银丝线，每本都不一样——这不是瑕疵，是设计：它们轨迹不同，寓意鸟儿飞行的轨迹，终以一只飞鸟栖于书末，泰戈尔在护封里藏了一个关于自由的故事。商务印书馆为这本书量身定制纸张，28克薄纸专色印刷。一书一码，随机即限量。",
        "product": "飞鸟集羽毛编码护封精装版"
    },
    # 风格2-待发布
    "recvghqL985vNe": {
        "title": "？碎片化时代，为什么还有人每天抄一句泰戈尔的诗？",
        "intro": "叶芝说每天读一句泰戈尔可以忘却世间痛苦——他教的不是诗，是让你在焦虑、失眠、emo里重建秩序的能力。325首，每首两行，刷牙时、地铁上、失眠夜，随手翻开都能用。布面精装刷边版，28g薄纸翻页如呼吸。不鸡汤，是武器。",
        "product": "飞鸟集天空蓝刷边便携版"
    },
}

def main():
    print("=" * 60)
    print("  飞鸟集迭代方案（基于DBS内容诊断）")
    print("=" * 60)

    print("\n[迭代策略]")
    print("  版本4改走「护封工艺设计哲学」全新路线（与版本1差异化）")
    print("  结尾CTA统一改为身份认同型（翻到最后一页/下次有人说转给他）")
    print()

    print("[详细方案]")
    name_map = {
        "recvf3IcP0oSJr": "版本1-余上沅",
        "recvf3IdqAQGRJ": "版本2-九厘米",
        "recvf3IdXsp0I6": "版本3-Ad Scout",
        "recvghqKBe8tSY": "版本4-护封工艺（新）",
        "recvghqL985vNe": "版本5-碎片化"
    }
    for rid, c in RECORDS.items():
        print(f"\n  【{name_map.get(rid, rid)}】")
        print(f"    标题: {c['title']}")
        print(f"    简介: {c['intro']}")
        print(f"    商品: {c['product']}")

    print("\n" + "=" * 60)
    print("上传到飞书...")

    token = get_access_token()
    if not token:
        return

    results = {}
    for rid, c in RECORDS.items():
        ok = update_record(token, rid, {
            "标题": c["title"],
            "简介": c["intro"],
            "商品短标题": c["product"]
        })
        results[rid] = ok
        name = name_map.get(rid, rid)
        print(f"  {name}: {'成功' if ok else '失败'}")

    print("\n" + "=" * 60)
    ok_count = sum(1 for v in results.values() if v)
    print(f"完成: {ok_count}/{len(results)} 条记录更新成功")

    if ok_count == len(results):
        print("\n全部更新成功！可在飞书中查看。")
    else:
        failed = [name_map.get(k, k) for k, v in results.items() if not v]
        print(f"\n失败: {', '.join(failed)}")

if __name__ == "__main__":
    main()
