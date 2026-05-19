#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地沙盒测试 — 零 API 调用, 仅验证硬裁剪 + 左对齐"""
import os, sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from cover_layout_engine import *
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUT, exist_ok=True)

# ── 字体 ──────────────────────────────────────────────
def load_font(size, serif=True):
    paths = [
        "C:/Windows/Fonts/NotoSerifSC-VF.ttf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSerifSC-VF.ttf",
        "C:/Windows/Fonts/NotoSansSC-VF.ttf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ── 生成 1080×1080 占位底图 (顶部有红色条纹, 底部有蓝色条纹, 方便肉眼验证裁剪线) ──
dummy = Image.new("RGB", (1080, 1080), (200, 180, 160))
dd = ImageDraw.Draw(dummy)
# 红色块: y=0~730 (裁剪后应保留)
for y in range(0, 730, 10):
    dd.line([(0, y), (1080, y)], fill=(210, 80, 60), width=4)
# 蓝色块: y=750~1080 (裁剪后必须消失)
for y in range(750, 1080, 10):
    dd.line([(0, y), (1080, y)], fill=(40, 80, 200), width=4)
# 裁剪标记线
dd.line([(0, 750), (1080, 750)], fill=(255, 255, 0), width=3)
dd.text((400, 760), "CROP LINE @ 750", fill=(255,255,0), font=load_font(24))
dd.text((400, 800), "THIS MUST DISAPPEAR", fill=(255,255,255), font=load_font(24))
dd.text((400, 840), "IF YOU SEE THIS, CROP FAILED", fill=(255, 0, 0), font=load_font(24))

dummy_path = os.path.join(OUT, "_dummy_bg.png")
dummy.save(dummy_path)

print("1. 占位底图: 1080×1080, 红色(保留区) + 蓝色(应被裁掉) + 黄色裁剪线@750")

# ── 排版引擎 ──────────────────────────────────────────
bg = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
engine = CoverLayoutEngine(bg)

# place_image → 内部执行: 宽度铺满1080, 裁剪至MAX_IMG_H=750
engine.place_image(dummy)

# 分割线
engine.draw_divider(color=(211, 107, 77), width=2)

# H1 主标题 — x = MARGIN_X = 108 (硬编码在 cover_layout_engine)
engine.render_h1("中国传统色", load_font(120), color=(45, 43, 42), line_spacing=150)

# H2 副标题 — x = MARGIN_X = 108
engine.render_h2("我见青山多妩媚，料青山见我应如是", load_font(50), color=(105, 100, 95), line_spacing=70)

# Tag 底部 — x = MARGIN_X = 108
engine.render_description("碧山 · 故宫美学", load_font(28), color=(102, 102, 102))

out_path = os.path.join(OUT, "_test_hardcrop.png")
engine.save(out_path, noise_intensity=0.03)

# ── 验证 ──────────────────────────────────────────────
print(f"2. 输出: {out_path}")
print(f"3. 关键坐标:")
print(f"   MARGIN_X      = {MARGIN_X} px (左对齐锚点)")
print(f"   MAX_IMG_H     = {CoverLayoutEngine.MAX_IMG_H} px (硬裁剪线)")
print(f"   H1_BASE_Y     = {H1_BASE_Y} px (主标题)")
print(f"   DIVIDER_LINE_Y= {DIVIDER_LINE_Y} px (分割线)")
print(f"   文字区间隙    = {H1_BASE_Y - CoverLayoutEngine.MAX_IMG_H} px (纯底色)")
print(f"\n4. 肉眼验证:")
print(f"   - 蓝色条纹必须完全消失 (在 750px 处被切除)")
print(f"   - 黄色裁剪线必须消失 (恰在边界)")
print(f"   - 所有文字靠左对齐 (x={MARGIN_X})")
print(f"   - y>750 区域全是纯 #F5F4F0 底色")
