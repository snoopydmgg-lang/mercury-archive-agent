#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在封面图片上添加文字 - 生成三个版本
"""

import sys
import io
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置
INPUT_IMAGE = "01_Projects_制作中/我等你/01_素材_试用装/00_封面设计/0430-我等你-封面-有机形态.png"
OUTPUT_DIR = "01_Projects_制作中/我等你/01_素材_试用装/00_封面设计"

# 色彩系统
BG_COLOR = (245, 244, 240)  # #F5F4F0 暖米色
INK_COLOR = (45, 43, 42)    # #2D2B2A 暖炭灰
ACCENT_COLOR = (211, 107, 77)  # #D36B4D 赤陶土

# 文字内容
TITLE = "我等你"

def create_version_1():
    """版本1：经典版 - 完整信息"""
    img = Image.open(INPUT_IMAGE)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 180)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
        bottom_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
    except:
        title_font = subtitle_font = bottom_font = ImageFont.load_default()

    # 主标题
    title_bbox = draw.textbbox((0, 0), TITLE, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (width - title_width) // 2
    title_y = int(height * 0.55)

    # 副标题
    subtitle = "法国绘本天后 海贝卡·朵特梅"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y - 60

    # 底部文字
    bottom_text = "212页激光纸雕 | 豆瓣9.8分"
    bottom_bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
    bottom_width = bottom_bbox[2] - bottom_bbox[0]
    bottom_x = (width - bottom_width) // 2
    bottom_y = height - 120

    # 绘制
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=INK_COLOR)
    draw.text((title_x, title_y), TITLE, font=title_font, fill=INK_COLOR)

    # 装饰线
    line_y = title_y + title_height + 30
    line_x1 = (width - 200) // 2
    line_x2 = line_x1 + 200
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=ACCENT_COLOR, width=2)

    draw.text((bottom_x, bottom_y), bottom_text, font=bottom_font, fill=INK_COLOR)

    output = f"{OUTPUT_DIR}/0430-我等你-封面-版本1-经典版.png"
    img.save(output, quality=95)
    print(f"✓ 版本1（经典版）: {Path(output).stat().st_size / 1024:.1f} KB")

def create_version_2():
    """版本2：极简版 - 只有书名"""
    img = Image.open(INPUT_IMAGE)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 220)
    except:
        title_font = ImageFont.load_default()

    # 主标题（更大）
    title_bbox = draw.textbbox((0, 0), TITLE, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = int(height * 0.50)

    draw.text((title_x, title_y), TITLE, font=title_font, fill=INK_COLOR)

    output = f"{OUTPUT_DIR}/0430-我等你-封面-版本2-极简版.png"
    img.save(output, quality=95)
    print(f"✓ 版本2（极简版）: {Path(output).stat().st_size / 1024:.1f} KB")

def create_version_3():
    """版本3：情感版 - 加金句"""
    img = Image.open(INPUT_IMAGE)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 180)
        quote_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
        bottom_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    except:
        title_font = quote_font = bottom_font = ImageFont.load_default()

    # 主标题
    title_bbox = draw.textbbox((0, 0), TITLE, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]
    title_x = (width - title_width) // 2
    title_y = int(height * 0.52)

    # 顶部金句
    quote = "从约定那一刻，浪漫就已经发生"
    quote_bbox = draw.textbbox((0, 0), quote, font=quote_font)
    quote_width = quote_bbox[2] - quote_bbox[0]
    quote_x = (width - quote_width) // 2
    quote_y = title_y - 80

    # 底部信息
    bottom_text = "212页激光纸雕 | 法国创意书大奖"
    bottom_bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
    bottom_width = bottom_bbox[2] - bottom_bbox[0]
    bottom_x = (width - bottom_width) // 2
    bottom_y = height - 120

    # 绘制
    draw.text((quote_x, quote_y), quote, font=quote_font, fill=ACCENT_COLOR)
    draw.text((title_x, title_y), TITLE, font=title_font, fill=INK_COLOR)

    # 装饰线
    line_y = title_y + title_height + 30
    line_x1 = (width - 200) // 2
    line_x2 = line_x1 + 200
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=ACCENT_COLOR, width=2)

    draw.text((bottom_x, bottom_y), bottom_text, font=bottom_font, fill=INK_COLOR)

    output = f"{OUTPUT_DIR}/0430-我等你-封面-版本3-情感版.png"
    img.save(output, quality=95)
    print(f"✓ 版本3（情感版）: {Path(output).stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    print("=" * 60)
    print("生成《我等你》封面 - 三个版本")
    print("=" * 60)
    create_version_1()
    create_version_2()
    create_version_3()
    print("=" * 60)
    print("✓ 所有版本生成完成！")
