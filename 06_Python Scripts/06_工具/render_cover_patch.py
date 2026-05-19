"""
飞鸟集封面修复脚本（遮盖+重绘模式）
功能：用色块遮盖 AI 生成的错误文字，重新渲染正确文本
依赖：Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def generate_cover_with_patch(base_image_path, output_path):
    """
    在原图上遮盖错误文字并重新渲染

    Args:
        base_image_path: 豆包生成的原始图片（含错误文字）
        output_path: 修复后的封面输出路径
    """
    if not os.path.exists(base_image_path):
        print(f"错误：底图文件不存在 {base_image_path}")
        return False

    img = Image.open(base_image_path)
    width, height = img.size
    print(f"底图尺寸：{width}x{height}")

    draw = ImageDraw.Draw(img)

    # 1. 遮盖原文本区域（用背景色填充）
    # 根据视觉规范，背景色应为 #F5F4F0（米白色）
    bg_color = "#F5F4F0"

    # 定义遮盖区域（覆盖图片下半部分的文字区域）
    # 基于 1920x2560 尺寸，遮盖从 y=1200 到 y=2100 的区域
    patch_box = [(0, 1200), (width, 2100)]
    draw.rectangle(patch_box, fill=bg_color)
    print(f"已遮盖区域：{patch_box}")

    # 2. 加载字体
    try:
        # 中文标题：宋体（衬线体）
        font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 220)
        # 英文副标题：宋体
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 80)
        # Slogan：宋体
        font_slogan = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 65)
    except Exception as e:
        print(f"字体加载失败：{e}")
        print("提示：请确保系统已安装 simsun.ttc")
        return False

    # 3. 重新渲染文本
    text_color = "#2D2B2A"  # 主文本色（深棕）
    accent_color = "#D36B4D"  # 点缀色（赤陶）
    center_x = width // 2

    # 主标题「飞鸟集」
    title_y = 1450
    draw.text(
        (center_x, title_y),
        "飞鸟集",
        font=font_title,
        fill=text_color,
        anchor="mm"
    )

    # 英文副标题「STRAY BIRDS」（字母间距加大）
    subtitle_y = 1680
    draw.text(
        (center_x, subtitle_y),
        "S T R A Y   B I R D S",
        font=font_subtitle,
        fill=text_color,
        anchor="mm"
    )

    # 装饰线（赤陶色）
    line_y = 1780
    line_width = 400
    draw.line(
        [(center_x - line_width//2, line_y), (center_x + line_width//2, line_y)],
        fill=accent_color,
        width=3
    )

    # Slogan「生如夏花之绚烂，死如秋叶之静美」
    slogan_y = 1900
    draw.text(
        (center_x, slogan_y),
        "生如夏花之绚烂，死如秋叶之静美",
        font=font_slogan,
        fill=text_color,
        anchor="mm"
    )

    # 保存修复后的封面
    img.save(output_path, quality=95)
    print(f"修复版封面已生成：{output_path}")
    return True


if __name__ == "__main__":
    # 输入：豆包生成的原始图片（含错误文字）
    base_image = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-text2img_output.png"

    # 输出：修复后的封面
    output_image = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-patched.png"

    generate_cover_with_patch(base_image, output_image)
