# -*- coding: utf-8 -*-
"""版式之道 0517 余上沅风格 — Kitta TTS 配音"""
import requests, os, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
API_URL = "https://kittaai.com/api/open/tts"
REFERENCE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"

MD_FILE = "01_Projects_制作中/版式之道/0517-版式之道-三套文案.md"
OUTPUT_DIR = "01_Projects_制作中/版式之道/03_配音_音频"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "0517-版式之道-余上沅.wav")

# Read oral script from MD
with open(MD_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Extract oral text between "### 口播文案" and next "###" or "---"
m = re.search(r'###\s+口播文案\s*\n+(.*?)(?=\n###|\n---\n|\Z)', content, re.DOTALL)
if not m:
    print("ERROR: 未找到口播文案")
    sys.exit(1)

oral_text = m.group(1).strip()

# Clean: remove markdown artifacts, normalize newlines
oral_text = oral_text.replace("\r\n", "\n").replace("\r", "\n")
# Collapse multiple blank lines
oral_text = re.sub(r'\n{3,}', '\n\n', oral_text)

print(f"口播文案: {len(oral_text)} chars")
print(f"文本预览:\n{oral_text[:200]}...\n")

# Call Kitta TTS API
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "text": oral_text,
    "version": "s1",
    "format": "wav",
    "reference_id": REFERENCE_ID
}

print("正在调用 Kitta TTS API...")
try:
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
    print(f"状态码: {resp.status_code}")

    if resp.status_code == 200:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(resp.content)
        size_kb = os.path.getsize(OUTPUT_FILE) / 1024
        print(f"配音成功: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    else:
        print(f"API 错误: {resp.text[:500]}")
        sys.exit(1)
except Exception as e:
    print(f"请求失败: {e}")
    sys.exit(1)
