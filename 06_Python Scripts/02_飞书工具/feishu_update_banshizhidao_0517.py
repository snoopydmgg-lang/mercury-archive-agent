# -*- coding: utf-8 -*-
"""
版式之道 0517 文案上传飞书 (从 MD 文件提取)
"""
import requests, sys, io, os, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
TABLE_ID = "tblSBx7rHX0siCnD"

MD_FILE = "01_Projects_制作中/版式之道/0517-版式之道-三套文案.md"

with open(MD_FILE, "r", encoding="utf-8") as f:
    content = f.read()

def extract_section(text, section_name):
    """Extract content between ### {section_name} and next ### or ---"""
    pattern = rf'###\s+{re.escape(section_name)}\s*\n+(.*?)(?=\n###|\n---\n|\Z)'
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""

def extract_meta(text, key):
    """Extract metadata like - **标题**：value"""
    pattern = rf'-\s*\*\*{re.escape(key)}\*\*[：:]\s*(.+)'
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""

# Extract oral script
oral_text = extract_section(content, "口播文案")
print(f"口播文案: {len(oral_text)} chars")

# Extract visual script table
visual_script = extract_section(content, "画面脚本")
print(f"画面脚本: {len(visual_script)} chars")

# Extract BGM
bgm_section = extract_section(content, "BGM建议")
print(f"BGM建议: {len(bgm_section)} chars")

# Extract metadata
title = extract_meta(content, "视频标题")
short_title = extract_meta(content, "商品短标题")
intro = extract_meta(content, "产品简介")
print(f"标题: {title}")
print(f"商品短标题: {short_title}")
print(f"简介: {intro}")

# Also extract sound effects from visual script rows
sound_effects = []
for line in visual_script.split("\n"):
    if "|" in line and not line.strip().startswith("|--"):
        parts = line.split("|")
        if len(parts) >= 9:
            sfx = parts[-1].strip()
            if sfx and sfx != "音效":
                sound_effects.append(sfx)

# Note: record for style 1 only (余上沅的奇妙屋)
# Mark the copy with style tag
oral_with_tag = "【余上沅的奇妙屋】\n\n" + oral_text

fields = {
    "选题标题": "版式之道",
    "标题": title,
    "简介": intro,
    "商品短标题": short_title,
    "口播文案": oral_with_tag,
    "画面脚本": visual_script,
    "BGM建议": bgm_section,
    "音效建议": "；".join(sound_effects) if sound_effects else "详见画面脚本表格",
    "配音链接": "",
    "状态": "待筛选",
}

def get_token():
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET}
    )
    token = resp.json().get("tenant_access_token")
    if not token:
        print(f"Token 获取失败: {resp.json()}")
    return token

def create_record(token, fields):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, headers=headers, json={"fields": fields})
    result = resp.json()
    if result.get("code") == 0:
        return result["data"]["record"]["record_id"]
    else:
        print(f"创建失败: {result}")
        return None

def main():
    token = get_token()
    if not token:
        print("获取 token 失败")
        return

    print("\n=== 上传版式之道 0517 文案到飞书 ===\n")
    for k, v in fields.items():
        preview = v[:60] + "..." if len(v) > 60 else v
        print(f"  {k}: {preview}")

    record_id = create_record(token, fields)

    if record_id:
        print(f"\n上传成功 (record_id: {record_id})")
    else:
        print("\n上传失败")

if __name__ == "__main__":
    main()
