"""
飞鸟集封面（轻盈羽毛版）
羽毛出现在画面中间三分之二区域，轻盈通透
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BG = (245, 244, 240)
TEXT = (45, 43, 42)
ACCENT = (211, 107, 77)
MUTED = (138, 133, 128)
SOFT = (230, 200, 185)

output_dir = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集"
os.makedirs(output_dir, exist_ok=True)

def add_noise(img, intensity=0.03):
    noise_img = Image.new('L', img.size)
    pixels = noise_img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = int(random.gauss(128, 128 * intensity))
    noise_img = noise_img.convert('RGB')
    return Image.blend(img, noise_img, alpha=intensity)

def draw_light_feather(draw, cx, cy, size, angle, color, alpha):
    """轻盈羽毛：细线、透明、流畅"""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    # 细羽轴（1px）
    shaft_pts = []
    for t in range(0, 181, 2):
        r = size * t / 180
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        shaft_pts.append((x, y))

    for i in range(len(shaft_pts) - 1):
        a = int(alpha * (0.6 + 0.4 * i / len(shaft_pts)))
        draw.line([shaft_pts[i], shaft_pts[i+1]], fill=color + (max(30, a),), width=1)

    # 轻盈羽枝（细线，透明度渐变）
    for i in range(0, 180, 4):
        r = size * i / 180
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)

        # 羽枝长度随位置变化（中间最密，两端稀疏）
        br_ratio = 0.35 * math.sin(math.pi * i / 180)

        for side in [-1, 1]:
            br = r * br_ratio
            bx = px + br * math.cos(math.radians(angle + side * 78))
            by = py + br * math.sin(math.radians(angle + side * 78))
            # 透明度从根部的alpha渐变到羽尖的20
            a = int(alpha * (0.3 + 0.7 * i / 180))
            draw.line([(px, py), (bx, by)], fill=color + (max(15, a),), width=1)

def generate_cover(index, output_file):
    width, height = 1080, 1440
    margin = 60

    # 中间三分之二区域
    zone_left = width // 6      # 180
    zone_right = width * 5 // 6  # 900
    zone_top = height // 6     # 240
    zone_bottom = height * 5 // 6  # 1200

    img = Image.new("RGB", (width, height), BG)
    img = add_noise(img, 0.03)
    draw = ImageDraw.Draw(img)

    # 内框 1px
    draw.rectangle([margin, margin, width - margin, height - margin], outline=TEXT, width=1)

    # 字体
    font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 130)
    font_subtitle = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    font_quote = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 36)
    font_tiny = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 12)

    # 文字
    draw.text((margin + 40, margin + 60), "飞鸟集", font=font_title, fill=TEXT)
    draw.line([(margin + 40, margin + 210), (margin + 180, margin + 210)], fill=ACCENT, width=3)
    draw.text((margin + 40, margin + 235), "S T R A Y   B I R D S", font=font_subtitle, fill=TEXT)
    draw.multiline_text(
        (width - margin - 40, height - margin - 200),
        "生如夏花之绚烂，\n死如秋叶之静美。",
        font=font_quote, fill=TEXT, align="right", anchor="rd", spacing=20
    )
    draw.text((margin + 40, height - margin - 50), "水星艺术馆", font=font_tiny, fill=MUTED, anchor="ld")
    draw.text((margin + 40, height - margin - 30), "MERCURY ART ARCHIVE // CURATED VISUALS",
              font=font_tiny, fill=MUTED, anchor="ld")
    draw.text((width - margin - 40, height - margin - 30), "ARCHIVE", font=font_tiny, fill=MUTED, anchor="rd")
    draw.text((width - margin - 40, margin + 30), "VOL.01", font=font_tiny, fill=ACCENT, anchor="rt")

    # 两根轻盈羽毛（画面中间三分之二区域）
    center_x = (zone_left + zone_right) // 2   # 540
    center_y = (zone_top + zone_bottom) // 2   # 720

    feather_configs = [
        # 羽毛1：赤陶色，从中心向左上延伸
        {"cx": center_x - 50, "cy": center_y + 30, "size": 500, "angle": 155, "color": ACCENT, "alpha": 140},
        # 羽毛2：灰桃色，从中心向右下延伸
        {"cx": center_x + 50, "cy": center_y - 30, "size": 500, "angle": 335, "color": SOFT, "alpha": 120},
    ]

    # 变体：不同角度和位置
    variants = [
        # 交叉形态
        {"cx1": center_x - 50, "cy1": center_y + 30, "a1": 155,
         "cx2": center_x + 50, "cy2": center_y - 30, "a2": 335},
        # 并排形态
        {"cx1": center_x - 80, "cy1": center_y, "a1": 150,
         "cx2": center_x + 80, "cy2": center_y, "a2": 30},
        # 上下形态
        {"cx1": center_x, "cy1": center_y - 80, "a1": 170,
         "cx2": center_x, "cy2": center_y + 80, "a2": 350},
        # 斜向形态
        {"cx1": center_x - 60, "cy1": center_y - 60, "a1": 160,
         "cx2": center_x + 60, "cy2": center_y + 60, "a2": 340},
    ]

    v = variants[index % len(variants)]
    size = 480

    # 羽毛1
    draw_light_feather(draw, v["cx1"], v["cy1"], size, v["a1"], ACCENT, 140)
    # 羽毛2
    draw_light_feather(draw, v["cx2"], v["cy2"], size, v["a2"], SOFT, 120)

    img.save(output_file, quality=95)
    print(f"生成：{os.path.basename(output_file)}")


if __name__ == "__main__":
    for i in range(4):
        output_path = f"{output_dir}/0414-飞鸟集-封面-{i+1:02d}.png"
        generate_cover(i, output_path)
