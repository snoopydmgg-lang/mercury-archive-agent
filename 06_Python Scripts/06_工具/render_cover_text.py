"""
飞鸟集封面文字渲染脚本
功能：在纯净底图上精确叠加中英文标题和 slogan
依赖：Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def generate_cover(base_image_path, output_path):
    """
    在底图上渲染飞鸟集封面文字

    Args:
        base_image_path: 豆包生成的纯净底图路径
        output_path: 最终封面输出路径
    """
    if not os.path.exists(base_image_path):
        print(f"❌ 错误：底图文件不存在 {base_image_path}")
        return False

    # 加载底图
    img = Image.open(base_image_path)
    width, height = img.size
    print(f"✓ 底图尺寸：{width}x{height}")

    draw = ImageDraw.Draw(img)

    # 颜色定义（遵循视觉规范）
    text_color = "#2D2B2A"  # 主文本色
    accent_color = "#D36B4D"  # 点缀色（用于装饰线）

    # 字体路径（Windows 系统字体）
    try:
        # 中文标题：宋体/明体（衬线体）
        font_title = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 140)
        # 英文副标题：Georgia（衬线体）
        font_subtitle = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 50)
        # Slogan：宋体
        font_slogan = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 45)
    except Exception as e:
        print(f"❌ 字体加载失败：{e}")
        print("提示：请确保系统已安装 simsun.ttc 和 georgia.ttf")
        return False

    # 文字布局（基于 1920x2560 尺寸）
    center_x = width // 2

    # 主标题「飞鸟集」
    title_y = int(height * 0.55)  # 约 1408px
    draw.text(
        (center_x, title_y),
        "飞鸟集",
        font=font_title,
        fill=text_color,
        anchor="mm"
    )

    # 英文副标题「STRAY BIRDS」
    subtitle_y = title_y + 120
    draw.text(
        (center_x, subtitle_y),
        "STRAY BIRDS",
        font=font_subtitle,
        fill=text_color,
        anchor="mm"
    )

    # 装饰线（赤陶色）
    line_y = subtitle_y + 70
    line_width = 400
    draw.line(
        [(center_x - line_width//2, line_y), (center_x + line_width//2, line_y)],
        fill=accent_color,
        width=3
    )

    # Slogan「生如夏花之绚烂，死如秋叶之静美」
    slogan_y = line_y + 100
    draw.text(
        (center_x, slogan_y),
        "生如夏花之绚烂，死如秋叶之静美",
        font=font_slogan,
        fill=text_color,
        anchor="mm"
    )

    # 保存最终封面
    img.save(output_path, quality=95)
    print(f"✓ 封面已生成：{output_path}")
    return True


if __name__ == "__main__":
    # 输入：豆包生成的纯净底图
    base_image = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-text2img_output.png"

    # 输出：最终封面
    output_image = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-final.png"

    generate_cover(base_image, output_image)
