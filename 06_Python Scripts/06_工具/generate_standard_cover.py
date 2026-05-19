"""
飞鸟集封面生成脚本（完全遵循视觉规范）
功能：纯代码生成封面，无需 AI，严格遵循个人视觉系统设计规范
依赖：Pillow
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def add_monochromatic_noise(img, intensity=0.03):
    """注入 3% 单色噪点，模拟物理印刷品微观粗糙感"""
    noise_img = Image.new('L', img.size)
    pixels = noise_img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            # 使用高斯分布生成噪点
            pixels[i, j] = int(random.gauss(128, 128 * intensity))

    noise_img = noise_img.convert('RGB')
    return Image.blend(img, noise_img, alpha=intensity)

def generate_cover(output_path):
    """
    生成飞鸟集封面（完全遵循视觉规范）

    Args:
        output_path: 封面输出路径
    """
    # 1. 核心参数锁定（严格遵循规范）
    width, height = 1080, 1440  # 3:4 死命令
    bg_color = "#F5F4F0"        # 暖米色
    text_color = "#2D2B2A"      # 暖炭灰
    accent_color = "#D36B4D"    # 赤陶土
    margin = 60                 # 画布边距

    print(f"画布尺寸：{width}x{height}")
    print(f"配色方案：背景 {bg_color} / 文本 {text_color} / 点缀 {accent_color}")

    # 2. 初始化画布与质感
    img = Image.new("RGB", (width, height), bg_color)
    img = add_monochromatic_noise(img, intensity=0.03)
    draw = ImageDraw.Draw(img)
    print("已注入 3% 单色噪点")

    # 3. 绘制网格系统（1px 内边框）
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=text_color,
        width=1
    )

    # 4. 字体映射（Windows 系统字体）
    try:
        # 标题：古典衬线体（宋体）
        font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 160)
        # 正文/副标：无衬线体（微软雅黑）
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
        font_quote = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 48)
        font_tiny = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
        print("字体加载成功")
    except Exception as e:
        print(f"字体加载失败：{e}")
        return False

    # 5. 瑞士网格排版渲染（极端字号对比）

    # 左上角：主标题与副标题
    draw.text((margin + 40, margin + 80), "飞鸟集", font=font_title, fill=text_color)

    # 核心点缀色分割线
    draw.line(
        [(margin + 40, margin + 280), (margin + 180, margin + 280)],
        fill=accent_color,
        width=4
    )

    draw.text(
        (margin + 40, margin + 320),
        "S T R A Y   B I R D S",
        font=font_subtitle,
        fill=text_color
    )

    # 右下角：核心引言（右对齐）
    quote = "生如夏花之绚烂，\n死如秋叶之静美。"
    draw.multiline_text(
        (width - margin - 40, height - margin - 200),
        quote,
        font=font_quote,
        fill=text_color,
        align="right",
        anchor="rd",
        spacing=24
    )

    # 底部/顶部：资产规格标识
    draw.text(
        (margin + 40, height - margin - 40),
        "MERCURY ART ARCHIVE // CURATED VISUALS",
        font=font_tiny,
        fill="#8A8580",
        anchor="ld"
    )

    draw.text(
        (width - margin - 40, margin + 40),
        "VOL.01",
        font=font_tiny,
        fill=accent_color,
        anchor="rt"
    )

    # 6. 导出
    img.save(output_path, quality=95)
    print(f"规范化封面已生成：{output_path}")
    return True


if __name__ == "__main__":
    output_path = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-规范版.png"
    generate_cover(output_path)
