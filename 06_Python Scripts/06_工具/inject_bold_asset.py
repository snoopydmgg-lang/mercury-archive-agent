"""
注入醒目版分形资产到封面
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BG = "#F5F4F0"
TEXT = "#2D2B2A"
ACCENT = "#D36B4D"
SOFT = "#E6C8B5"

assets_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"
output_dir = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集"

def add_noise(img, intensity=0.03):
    import random
    noise_img = Image.new('L', img.size)
    pixels = noise_img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = int(random.gauss(128, 128 * intensity))
    noise_img = noise_img.convert('RGB')
    return Image.blend(img, noise_img, alpha=intensity)

def generate_base():
    width, height = 1080, 1440
    img = Image.new("RGB", (width, height), BG)
    img = add_noise(img, 0.03)
    draw = ImageDraw.Draw(img)

    margin = 60
    draw.rectangle([margin, margin, width - margin, height - margin], outline=TEXT, width=1)

    font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 160)
    font_subtitle = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
    font_quote = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 48)
    font_tiny = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)

    draw.text((margin + 40, margin + 80), "飞鸟集", font=font_title, fill=TEXT)
    draw.line([(margin + 40, margin + 280), (margin + 180, margin + 280)], fill=ACCENT, width=4)
    draw.text((margin + 40, margin + 320), "S T R A Y   B I R D S", font=font_subtitle, fill=TEXT)

    quote = "生如夏花之绚烂，\n死如秋叶之静美。"
    draw.multiline_text(
        (width - margin - 40, height - margin - 200),
        quote, font=font_quote, fill=TEXT, align="right", anchor="rd", spacing=24
    )

    draw.text((margin + 40, height - margin - 40), "MERCURY ART ARCHIVE // CURATED VISUALS",
              font=font_tiny, fill="#8A8580", anchor="ld")
    draw.text((width - margin - 40, margin + 40), "VOL.01",
              font=font_tiny, fill=ACCENT, anchor="rt")

    return img

def inject(asset_path, output_path, size=500, pos_x=430, pos_y=200, alpha=0.9):
    asset = Image.open(asset_path).convert("RGBA")
    ratio = size / asset.width
    new_h = int(asset.height * ratio)
    asset = asset.resize((size, new_h), Image.Resampling.LANCZOS)

    a = asset.split()[3]
    a = ImageEnhance.Brightness(a).enhance(alpha)
    asset.putalpha(a)

    result = generate_base().convert("RGBA")
    result.paste(asset, (pos_x, pos_y), asset)
    result = result.convert("RGB")
    result.save(output_path, quality=95)
    print(f"生成：{output_path}")

# 注入前4个醒目变体
assets = sorted([f for f in os.listdir(assets_dir) if 'bold_' in f])

for i, asset in enumerate(assets[:4]):
    inject(
        os.path.join(assets_dir, asset),
        f"{output_dir}/0414-飞鸟集-封面-{i+1:02d}-{asset}.png",
        size=550, pos_x=400, pos_y=180, alpha=0.9
    )
