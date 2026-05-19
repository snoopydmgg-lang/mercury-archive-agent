# -*- coding: utf-8 -*-
"""
版式之道 - 三套风格文案上传到飞书内容追踪表格
同时生成标题、简介、商品总标题
"""
import requests, sys, io, json, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

# ================= 读取三套风格文案 =================
copy_file = "01_Projects_制作中/版式之道/02_脚本_逻辑链/0407-版式之道-三套风格文案.md"

with open(copy_file, "r", encoding="utf-8") as f:
    content = f.read()

# 解析三个风格块
styles = {}
current_style = None

sections = re.split(r"(?=## 风格\d+:)", content)
for section in sections:
    if not section.strip():
        continue
    # 提取风格名
    style_match = re.search(r"## 风格(\d+):\s*【?(.+?)】?\s*-?\s*(.+)", section)
    if style_match:
        num = style_match.group(1)
        style_name = style_match.group(2).strip() + " - " + style_match.group(3).strip()
        styles[num] = {"name": style_name, "raw": section}

def extract_section(text, start_marker, end_markers):
    for m in end_markers:
        if m in text:
            text = text.split(m)[0]
    if start_marker in text:
        text = text.split(start_marker)[1]
    return text.strip()

def extract_copy_parts(section_text):
    """从风格section提取各部分"""
    # 画面脚本 - 表格
    script_match = re.search(r"### 画面脚本\s*\n\|(.+)", section_text)
    script_table = ""
    if script_match:
        # 提取整个表格
        table_match = re.search(r"((?:\|.+\n)+)", section_text[script_match.start():])
        if table_match:
            script_table = "画面脚本\n" + table_match.group(0)

    # 口播文案
    oral_match = re.search(r"### 口播文案\s*\n(.+?)(?=\n---\n|\n### BGM|$)", section_text, re.DOTALL)
    oral = ""
    if oral_match:
        oral = oral_match.group(1).strip()

    # BGM建议
    bgm_match = re.search(r"### BGM建议\s*\n(.+?)(?=\n---\n|\n### 音效|$)", section_text, re.DOTALL)
    bgm = ""
    if bgm_match:
        bgm = bgm_match.group(1).strip()

    # 音效建议
    sfx_match = re.search(r"### 音效建议\s*\n(.+?)(?=\n---\n|$)", section_text, re.DOTALL)
    sfx = ""
    if sfx_match:
        sfx = sfx_match.group(1).strip()

    return script_table, oral, bgm, sfx

copies = {}
for num, data in styles.items():
    script_table, oral, bgm, sfx = extract_copy_parts(data["raw"])
    copies[num] = {
        "name": data["name"],
        "script": script_table,
        "oral": oral,
        "bgm": bgm,
        "sfx": sfx
    }

print(f"解析到 {len(copies)} 套风格文案")

# ================= 飞书操作 =================
def get_token():
    resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                         json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")

def create_record(token, fields):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, headers=headers, json={"fields": fields})
    data = resp.json()
    if data.get("code") == 0:
        record_id = data["data"]["record"]["record_id"]
        print(f"  记录创建成功: {record_id}")
        return record_id
    else:
        print(f"  创建失败: {data}")
        return None

def batch_update_text(texts):
    """合并多套文案为一个文本块"""
    result = ""
    for i, (k, v) in enumerate(texts.items(), 1):
        result += f"\n{'='*40}\n"
        result += f"风格{i}：{v['name']}\n"
        result += f"{'='*40}\n"
        result += f"【画面脚本】\n{v['script']}\n\n"
        result += f"【口播文案】\n{v['oral']}\n\n"
        result += f"【BGM建议】\n{v['bgm']}\n\n"
        result += f"【音效建议】\n{v['sfx']}\n"
    return result.strip()

def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    print("=== 上传版式之道三套风格文案到飞书 ===\n")

    # 合并三套文案
    script_all = batch_update_text(copies)

    # 构建记录字段
    fields = {
        "选题标题": "《版式之道》三套风格文案",
        "画面脚本": copies["1"]["script"] + "\n\n[风格2和风格3详见口播文案]",
        "口播文案": script_all,
        "BGM建议": copies["1"]["bgm"] + "\n\n" + copies["2"]["bgm"] + "\n\n" + copies["3"]["bgm"],
        "音效建议": copies["1"]["sfx"] + "\n\n" + copies["2"]["sfx"] + "\n\n" + copies["3"]["sfx"],
        "状态": "待筛选",
    }

    record_id = create_record(token, fields)

    if record_id:
        print(f"\n✅ 三套风格文案已上传到飞书 (record_id: {record_id})")
    else:
        print("\n❌ 上传失败")

if __name__ == "__main__":
    main()
