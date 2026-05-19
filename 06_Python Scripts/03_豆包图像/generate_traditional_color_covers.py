#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成三张中国传统色封面 — 使用绝对锚点排版引擎"""
import os, sys, random

# ── 路径设置 ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from cover_layout_engine import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT_DIR = r"E:\1.work\douyin\1.shuixing\00_InBox_收件箱"
os.makedirs(OUT_DIR, exist_ok=True)

# ── 字体加载 (保持原有规范) ──────────────────────────
def get_serif_font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/NotoSerifSC-VF.ttf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSerifSC-VF.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simkai.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def get_sans_font(size):
    paths = [
        "C:/Windows/Fonts/NotoSansSC-VF.ttf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ── 噪点纹理 (品牌规范: 2-5%) ──────────────────────
def add_noise(img, intensity=0.025):
    noise = Image.new("L", img.size, 0)
    px = noise.load()
    for y in range(img.height):
        for x in range(img.width):
            if random.random() < intensity:
                px[x, y] = random.randint(0, 255)
    noise = noise.filter(ImageFilter.GaussianBlur(radius=0.5))
    noise_rgb = Image.merge("RGB", [noise, noise, noise])
    return Image.blend(img.convert("RGB"), noise_rgb, intensity * 0.5)

# ── 三套配色方案 ─────────────────────────────────────
THEMES = [
    {
        "name": "碧山",
        "subtitle": "我见青山多妩媚，料青山见我应如是",
        "bg":      (225, 232, 228),   # 青绿底
        "accent":  (80, 130, 110),     # 青山色
        "divider": (110, 155, 130),
        "title_c": (45, 55, 48),
        "sub_c":   (90, 110, 100),
    },
    {
        "name": "暮山紫",
        "subtitle": "潦水尽而寒潭清，烟光凝而暮山紫",
        "bg":      (236, 230, 238),   # 紫雾底
        "accent":  (135, 105, 155),    # 暮紫色
        "divider": (150, 125, 165),
        "title_c": (55, 42, 58),
        "sub_c":   (110, 95, 120),
    },
    {
        "name": "黄白游",
        "subtitle": "黄山白岳是神仙梦，黄金白银是富贵梦",
        "bg":      (244, 236, 220),   # 暖金底
        "accent":  (185, 145, 85),     # 黄白游色
        "divider": (195, 160, 105),
        "title_c": (58, 48, 32),
        "sub_c":   (130, 110, 80),
    },
]

# ── 生成 ──────────────────────────────────────────────
for t in THEMES:
    print(f"生成: {t['name']} ...")

    # 1. 纯色底图 + 轻微渐变
    bg = Image.new("RGB", (CANVAS_W, CANVAS_H), t["bg"])
    draw_bg = ImageDraw.Draw(bg)

    # 2. 图像区域放一个色块 (模拟 AI 插图区域)
    box_x1, box_y1 = MARGIN_X, IMAGE_BOX_TOP
    box_x2, box_y2 = CANVAS_W - MARGIN_X, IMAGE_BOX_BOTTOM

    # 圆角色块作为"插图"
    accent_rgba = t["accent"] + (40,)
    overlay = Image.new("RGBA", (IMAGE_BOX_W, IMAGE_BOX_H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    # 大椭圆 + 小圆点装饰
    overlay_draw.ellipse(
        [IMAGE_BOX_W * 0.15, IMAGE_BOX_H * 0.1,
         IMAGE_BOX_W * 0.85, IMAGE_BOX_H * 0.9],
        fill=t["accent"] + (25,)
    )
    overlay_draw.ellipse(
        [IMAGE_BOX_W * 0.35, IMAGE_BOX_H * 0.3,
         IMAGE_BOX_W * 0.65, IMAGE_BOX_H * 0.7],
        fill=t["accent"] + (15,)
    )
    # 中心颜色名 (作为 AI 图的占位)
    center_font = get_serif_font(72)
    c_bbox = center_font.getbbox(t["name"])
    c_w = c_bbox[2] - c_bbox[0]
    overlay_draw.text(
        ((IMAGE_BOX_W - c_w) // 2, (IMAGE_BOX_H - 72) // 2),
        t["name"], font=center_font, fill=t["accent"] + (60,)
    )
    bg.paste(overlay, (box_x1, box_y1), overlay)

    # 3. 噪点纹理
    bg = add_noise(bg, 0.025)

    # 4. 绝对锚点排版引擎
    engine = CoverLayoutEngine(bg)
    engine.draw_divider(color=t["divider"], width=2)

    # H1 主标题 — 具体元素名 (120pt 衬线体, 绝对锚点)
    title_font = get_serif_font(120, bold=False)
    engine.render_h1(
        t["name"], title_font,
        color=t["title_c"],
        line_spacing=150
    )

    # H2 副标题 — 诗句/解释 (50pt 无衬线体, 保持不变)
    sub_font = get_sans_font(50)
    engine.render_h2(
        t["subtitle"], sub_font,
        color=t["sub_c"],
        line_spacing=70
    )

    # 底部标签 — 系列/产品名常量 (沉底锚定)
    meta_font = get_sans_font(28)
    engine.render_description(
        "中国传统色 · 故宫美学", meta_font,
        color=t["accent"] + (180,),
        line_spacing=42
    )

    out_path = os.path.join(OUT_DIR, f"传统色_{t['name']}.png")
    engine.save(out_path)
    print(f"  → {out_path}")

print("\n三张封面生成完毕。")
