# -*- coding: utf-8 -*-
"""
版式之道 0414-004428-1 文案上传飞书
"""
import requests, sys, io, json, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# 读取JSON文案
script_file = "01_Projects_制作中/版式之道/02_脚本_逻辑链/0414-004428-1.json"
audio_file = "01_Projects_制作中/版式之道/01_素材_试用装/0414-配音-1.wav"

with open(script_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 处理分镜脚本：从JSON提取并还原成表格文本
vs_raw = data.get("visual_script", "")
# 处理 \\n 分隔符
vs_lines = re.split(r'(?:\\\\n|\\n|\n)', vs_raw)
vs_table = "时间轴|素材类型|画面描述|花字/字幕|BGM处理|音效设计\n" + \
           "|".join(["" for _ in range(6)]) + "\n"
for line in vs_lines:
    line = line.strip()
    if line:
        parts = line.split("|")
        if len(parts) >= 6:
            vs_table += "|".join(parts[:6]) + "\n"

# 构建飞书记录字段
fields = {
    "选题标题": "版式之道",
    "标题": data.get("title", ""),
    "简介": data.get("publish_intro", ""),
    "商品短标题": data.get("product_short_title", ""),
    "口播文案": data.get("oral_text", "").replace("\\n", "\n"),
    "画面脚本": vs_table,
    "BGM建议": data.get("bgm_suggestion", ""),
    "音效建议": "详见画面脚本表格",
    "配音链接": audio_file if os.path.exists(audio_file) else "",
    "状态": "待筛选",
}

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
        print(f"  记录创建成功: {record_id}")
        return record_id
    else:
        print(f"  创建失败: {result}")
        return None

def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    print("=== 上传版式之道 0414-004428-1 到飞书 ===\n")
    print(f"选题标题: {fields['选题标题']}")
    print(f"标题: {fields['标题']}")
    print(f"商品短标题: {fields['商品短标题']}")
    print(f"BGM: {fields['BGM建议']}")
    print(f"配音文件: {fields['配音链接']}")
    print()

    record_id = create_record(token, fields)

    if record_id:
        print(f"\n✅ 上传成功 (record_id: {record_id})")
    else:
        print("\n❌ 上传失败")

if __name__ == "__main__":
    main()
