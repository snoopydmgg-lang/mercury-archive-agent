"""
飞鸟集封面批量生成脚本
功能：生成多个带飞鸟分形资产的封面供选择
严格遵循视觉规范：#F5F4F0 / #2D2B2A / #D36B4D / #E6C8B5
依赖：Pillow
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 视觉规范配色
BG = "#F5F4F0"       # 暖米色
TEXT = "#2D2B2A"     # 暖炭灰
ACCENT = "#D36B4D"  # 赤陶土
SOFT = "#E6C8B5"    # 灰桃色

assets_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"
output_dir = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集"
os.makedirs(output_dir, exist_ok=True)

def add_noise(img, intensity=0.03):
    """注入 3% 单色噪点"""
    import random
    noise_img = Image.new('L', img.size)
    pixels = noise_img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = int(random.gauss(128, 128 * intensity))
    noise_img = noise_img.convert('RGB')
    return Image.blend(img, noise_img, alpha=intensity)

def generate_base_cover():
    """生成基础封面（文字+网格）"""
    width, height = 1080, 1440
    img = Image.new("RGB", (width, height), BG)
    img = add_noise(img, 0.03)
    draw = ImageDraw.Draw(img)

    # 内边框
    margin = 60
    draw.rectangle([margin, margin, width - margin, height - margin], outline=TEXT, width=1)

    # 字体
    font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 160)
    font_subtitle = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
    font_quote = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 48)
    font_tiny = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)

    # 标题
    draw.text((margin + 40, margin + 80), "飞鸟集", font=font_title, fill=TEXT)

    # 分割线
    draw.line([(margin + 40, margin + 280), (margin + 180, margin + 280)], fill=ACCENT, width=4)

    # 副标题
    draw.text((margin + 40, margin + 320), "S T R A Y   B I R D S", font=font_subtitle, fill=TEXT)

    # 引言
    quote = "生如夏花之绚烂，\n死如秋叶之静美。"
    draw.multiline_text(
        (width - margin - 40, height - margin - 200),
        quote, font=font_quote, fill=TEXT, align="right", anchor="rd", spacing=24
    )

    # 底部标识
    draw.text((margin + 40, height - margin - 40), "MERCURY ART ARCHIVE // CURATED VISUALS",
              font=font_tiny, fill="#8A8580", anchor="ld")
    draw.text((width - margin - 40, margin + 40), "VOL.01",
              font=font_tiny, fill=ACCENT, anchor="rt")

    return img

def inject_asset(base_img, asset_path, position="right", alpha=0.85, size=400):
    """注入分形资产"""
    asset = Image.open(asset_path).convert("RGBA")
    width, height = base_img.size

    # 缩放
    ratio = size / asset.width
    new_h = int(asset.height * ratio)
    asset = asset.resize((size, new_h), Image.Resampling.LANCZOS)

    # 位置计算
    if position == "right":
        x = width - 60 - size - 40
        y = int(height * 0.25)
    elif position == "left":
        x = 60 + 40
        y = int(height * 0.3)
    elif position == "center":
        x = (width - size) // 2
        y = (height - new_h) // 2
    elif position == "bottom":
        x = width - 60 - size - 30
        y = height - 60 - new_h - 100
    elif position == "top_right":
        x = width - 60 - size - 20
        y = 80

    # 透明度
    a = asset.split()[3]
    a = ImageEnhance.Brightness(a).enhance(alpha)
    asset.putalpha(a)

    # 合成
    result = base_img.convert("RGBA")
    result.paste(asset, (x, y), asset)
    return result.convert("RGB")

def generate_covers():
    """批量生成封面"""
    # 获取所有飞鸟主题资产
    assets = sorted([f for f in os.listdir(assets_dir) if f.endswith('.png')])
    bird_assets = [f for f in assets if 'bird' in f or 'combined' in f]

    print(f"发现 {len(bird_assets)} 个飞鸟主题资产\n")

    positions = ["right", "bottom", "top_right", "center"]
    sizes = [350, 400, 450]

    count = 0
    for asset_file in bird_assets[:12]:  # 前12个
        asset_path = os.path.join(assets_dir, asset_file)
        base = generate_base_cover()

        for pos in positions[:2]:
            for sz in sizes[:1]:
                count += 1
                # 注入资产
                final = inject_asset(base, asset_path, position=pos, alpha=0.8, size=sz)

                # 保存
                name = asset_file.replace('.png', '').replace('_', '-')
                output_path = f"{output_dir}/0414-飞鸟集-封面-{count:02d}-{name}-{pos}.png"
                final.save(output_path, quality=95)
                print(f"  [{count:02d}] {os.path.basename(output_path)}")

    print(f"\n共生成 {count} 个封面版本")
    print(f"存放目录：{output_dir}")

if __name__ == "__main__":
    generate_covers()
