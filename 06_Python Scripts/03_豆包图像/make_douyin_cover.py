#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音封面自动生成器
基于现有图片生成适配抖音竖屏的封面图
"""

import os
import sys
import io
# 修复 Windows GBK 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import platform


def find_chinese_font():
    """自动检测系统可用的中文字体"""
    system = platform.system()

    font_candidates = []

    if system == "Windows":
        font_dirs = [
            r"C:\Windows\Fonts",
            os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts")
        ]
        font_candidates = [
            ("msyh.ttc", "Microsoft YaHei"),  # 微软雅黑
            ("msyhbd.ttc", "Microsoft YaHei Bold"),
            ("simhei.ttf", "SimHei"),  # 黑体
            ("simsun.ttc", "SimSun"),  # 宋体
            ("simkai.ttf", "KaiTi"),  # 楷体
        ]
    elif system == "Darwin":  # macOS
        font_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
        font_candidates = [
            ("PingFang.ttc", "PingFang SC"),
            ("Songti.ttc", "Songti SC"),
            ("STHeiti Medium.ttc", "Heiti SC"),
        ]
    else:  # Linux
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts")
        ]
        font_candidates = [
            ("NotoSansCJK-Regular.ttc", "Noto Sans CJK"),
            ("NotoSerifCJK-Regular.ttc", "Noto Serif CJK"),
        ]

    # 搜索字体文件
    for font_dir in font_dirs:
        if not os.path.exists(font_dir):
            continue
        for font_file, font_name in font_candidates:
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if font_file.lower() in file.lower():
                        font_path = os.path.join(root, file)
                        print(f"[OK] 找到中文字体: {font_name} ({font_path})")
                        return font_path

    raise FileNotFoundError(
        f"错误：未找到可用的中文字体。\n"
        f"系统: {system}\n"
        f"搜索路径: {font_dirs}\n"
        f"候选字体: {[f[1] for f in font_candidates]}"
    )


def crop_and_resize(img, target_width, target_height):
    """等比缩放并裁切图片到目标尺寸"""
    original_width, original_height = img.size
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height

    if original_ratio > target_ratio:
        # 原图更宽，按高度缩放
        new_height = target_height
        new_width = int(original_width * (target_height / original_height))
    else:
        # 原图更高，按宽度缩放
        new_width = target_width
        new_height = int(original_height * (target_width / original_width))

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 居中裁切
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    return img_resized.crop((left, top, right, bottom))


def add_gradient_overlay(img, color=(245, 244, 240), alpha_top=0, alpha_bottom=120):
    """添加从上到下的渐变遮罩"""
    width, height = img.size
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for y in range(height):
        alpha = int(alpha_top + (alpha_bottom - alpha_top) * (y / height))
        draw.line([(0, y), (width, y)], fill=(*color, alpha))

    return Image.alpha_composite(img.convert('RGBA'), overlay)


def draw_rounded_rectangle(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)


def draw_text_centered(draw, text, y, font, color, canvas_width):
    """绘制居中文本"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (canvas_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]  # 返回文本高度


def draw_tag(draw, text, x, y, font, bg_color, text_color, padding=20, radius=15):
    """绘制圆角标签"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    tag_width = text_width + padding * 2
    tag_height = text_height + padding

    tag_x1 = x - tag_width // 2
    tag_y1 = y
    tag_x2 = x + tag_width // 2
    tag_y2 = y + tag_height

    draw_rounded_rectangle(draw, (tag_x1, tag_y1, tag_x2, tag_y2), radius, bg_color)

    text_x = x - text_width // 2
    text_y = y + (tag_height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=text_color)


def main():
    # 配置
    INPUT_IMAGE = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\我等你\01_素材_试用装\00_封面设计\0430-我等你-封面-有机形态.png"
    OUTPUT_DIR = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\我等你\01_素材_试用装\00_封面设计"
    OUTPUT_PNG = os.path.join(OUTPUT_DIR, "douyin_cover_reworked.png")
    OUTPUT_PREVIEW = os.path.join(OUTPUT_DIR, "douyin_cover_preview.jpg")

    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920

    # 颜色配置（符合视觉规范）
    COLOR_BG = (245, 244, 240)  # 暖米色
    COLOR_ACCENT = (211, 107, 77)  # 赤陶土
    COLOR_TEXT_DARK = (45, 43, 42)  # 暖炭灰
    COLOR_TEXT_WARM = (120, 90, 70)  # 暖棕色
    COLOR_TEXT_LIGHT = (150, 130, 110)  # 暖灰棕

    print("=" * 60)
    print("抖音封面生成器")
    print("=" * 60)

    # 检查输入文件
    if not os.path.exists(INPUT_IMAGE):
        print(f"错误：找不到输入图片 {INPUT_IMAGE}")
        sys.exit(1)

    # 加载图片
    print(f"\n[1/6] 加载图片: {INPUT_IMAGE}")
    img = Image.open(INPUT_IMAGE)
    print(f"      原始尺寸: {img.size[0]}x{img.size[1]}")

    # 裁切和缩放
    print(f"\n[2/6] 裁切并缩放到 {TARGET_WIDTH}x{TARGET_HEIGHT}")
    img_cropped = crop_and_resize(img, TARGET_WIDTH, TARGET_HEIGHT)

    # 添加渐变遮罩
    print(f"\n[3/6] 添加渐变遮罩")
    img_with_overlay = add_gradient_overlay(img_cropped)

    # 查找字体
    print(f"\n[4/6] 查找中文字体")
    font_path = find_chinese_font()

    # 加载字体
    font_tag = ImageFont.truetype(font_path, 32)
    font_hook = ImageFont.truetype(font_path, 52)
    font_title = ImageFont.truetype(font_path, 180)
    font_subtitle = ImageFont.truetype(font_path, 54)
    font_bottom = ImageFont.truetype(font_path, 36)

    # 绘制文字
    print(f"\n[5/6] 绘制文字图层")
    draw = ImageDraw.Draw(img_with_overlay)

    # 顶部标签
    draw_tag(
        draw,
        "豆瓣高分治愈绘本",
        TARGET_WIDTH // 2,
        140,
        font_tag,
        COLOR_ACCENT,
        (255, 255, 255)
    )

    # 情绪钩子
    draw_text_centered(
        draw,
        "如果你也在等一个答案",
        780,
        font_hook,
        COLOR_TEXT_WARM,
        TARGET_WIDTH
    )

    # 主标题
    draw_text_centered(
        draw,
        "我等你",
        920,
        font_title,
        COLOR_TEXT_DARK,
        TARGET_WIDTH
    )

    # 副标题
    draw_text_centered(
        draw,
        "一本写给等待者的治愈绘本",
        1150,
        font_subtitle,
        COLOR_TEXT_WARM,
        TARGET_WIDTH
    )

    # 底部信息
    draw_text_centered(
        draw,
        "绘本推荐 | 情绪疗愈 | 睡前阅读",
        1680,
        font_bottom,
        COLOR_TEXT_LIGHT,
        TARGET_WIDTH
    )

    # 保存文件
    print(f"\n[6/6] 保存文件")
    img_with_overlay.convert('RGB').save(OUTPUT_PNG, 'PNG', optimize=True)
    print(f"      PNG: {OUTPUT_PNG}")
    print(f"      大小: {os.path.getsize(OUTPUT_PNG) / 1024:.1f} KB")

    img_with_overlay.convert('RGB').save(OUTPUT_PREVIEW, 'JPEG', quality=92)
    print(f"      预览: {OUTPUT_PREVIEW}")
    print(f"      大小: {os.path.getsize(OUTPUT_PREVIEW) / 1024:.1f} KB")

    print("\n" + "=" * 60)
    print("生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
