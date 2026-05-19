"""
生成 Claude 风格分形资产
功能：基于个人视觉规范，生成抽象几何分形图案
风格：Claude 品牌美学 + 视觉规范配色
依赖：Pillow
"""
from PIL import Image, ImageDraw
import math
import random
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def draw_claude_fractal(draw, center_x, center_y, radius, depth, color, alpha):
    """
    递归绘制 Claude 风格的圆形分形图案

    Args:
        draw: ImageDraw 对象
        center_x, center_y: 圆心坐标
        radius: 半径
        depth: 递归深度
        color: 颜色
        alpha: 透明度
    """
    if depth == 0 or radius < 5:
        return

    # 绘制当前圆（空心）
    bbox = [
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    ]
    draw.ellipse(bbox, outline=color + (alpha,), width=2)

    # 递归绘制子圆（3个方向）
    angles = [0, 120, 240]
    new_radius = radius * 0.5

    for angle in angles:
        rad = math.radians(angle)
        new_x = center_x + radius * 0.6 * math.cos(rad)
        new_y = center_y + radius * 0.6 * math.sin(rad)

        draw_claude_fractal(
            draw, new_x, new_y, new_radius,
            depth - 1, color, max(20, alpha - 30)
        )

def generate_claude_asset(output_path):
    """
    生成 Claude 风格分形资产

    Args:
        output_path: 输出路径
    """
    # 画布尺寸（方形，便于缩放）
    size = 800

    # 创建透明画布
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 配色方案（遵循视觉规范）
    accent_color = (211, 107, 77)  # #D36B4D 赤陶土
    text_color = (45, 43, 42)      # #2D2B2A 暖炭灰

    print(f"画布尺寸：{size}x{size}")
    print(f"配色：赤陶土 RGB{accent_color} + 暖炭灰 RGB{text_color}")

    # 绘制主分形（中心）
    center = size // 2
    main_radius = 280

    # 主图案（赤陶色）
    draw_claude_fractal(
        draw, center, center, main_radius,
        depth=3, color=accent_color, alpha=120
    )

    # 辅助图案（暖炭灰，偏移位置）
    draw_claude_fractal(
        draw, center - 80, center + 60, main_radius * 0.6,
        depth=2, color=text_color, alpha=60
    )

    # 添加微妙的几何线条（Claude 风格）
    for i in range(5):
        angle = random.uniform(0, 360)
        rad = math.radians(angle)
        length = random.randint(100, 200)

        x1 = center + length * math.cos(rad)
        y1 = center + length * math.sin(rad)
        x2 = center + (length + 80) * math.cos(rad)
        y2 = center + (length + 80) * math.sin(rad)

        draw.line(
            [(x1, y1), (x2, y2)],
            fill=accent_color + (40,),
            width=1
        )

    # 保存
    img.save(output_path, "PNG")
    print(f"Claude 风格分形资产已生成：{output_path}")
    return True


if __name__ == "__main__":
    output_path = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_asset.png"
    generate_claude_asset(output_path)
