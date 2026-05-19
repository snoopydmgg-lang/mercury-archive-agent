"""
飞鸟集主题分形资产 v2（醒目版）
功能：粗线条、高对比度、视觉冲击力强
严格遵循视觉规范：#D36B4D / #2D2B2A / #E6C8B5
"""
from PIL import Image, ImageDraw
import math
import random
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

output_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"

# 视觉规范配色
ACCENT = (211, 107, 77)    # #D36B4D 赤陶土
TEXT = (45, 43, 42)         # #2D2B2A 暖炭灰
SOFT = (230, 200, 185)      # #E6C8B5 灰桃色

def draw_bold_bird_trail(draw, cx, cy, size, color, alpha=255):
    """粗线条鸟群轨迹"""
    # 主螺旋轨迹（粗线）
    points = []
    for i in range(0, 361, 3):
        rad = math.radians(i)
        r = size * (0.15 + 0.85 * i / 360)
        x = cx + r * math.cos(rad) * 1.3
        y = cy + r * math.sin(rad) * 0.85
        points.append((x, y))

    # 粗线绘制（宽度6）
    for i in range(len(points) - 1):
        a = int(alpha * (1 - i / len(points) * 0.5))
        draw.line([points[i], points[i+1]], fill=color + (max(100, a),), width=6)

    # 外圈装饰（粗弧线）
    for i in range(4):
        angle_start = i * 90 + 15
        pts = []
        for t in range(0, 120, 3):
            rad = math.radians(angle_start + t)
            r = size * 0.7 + t * 1.8
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        draw.line(pts, fill=color + (max(120, alpha-50),), width=4)

def draw_bold_wings(draw, cx, cy, size, color, alpha=255):
    """粗线条翅膀"""
    for i in range(6):
        angle = i * 60
        pts = []
        for t in range(-40, 41, 2):
            rad = math.radians(angle + t)
            r = size * (0.2 + 0.8 * math.cos(math.radians(t * 1.2)))
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=color + (alpha,), width=5)

def draw_concentric_rings(draw, cx, cy, size, color, alpha=255):
    """粗同心圆"""
    for i in range(5):
        r = size * (0.3 + i * 0.18)
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.ellipse(bbox, outline=color + (alpha - i*30,), width=6)

def draw_radial_lines(draw, cx, cy, size, color, alpha=255):
    """放射状粗线条"""
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        x2 = cx + size * math.cos(rad)
        y2 = cy + size * math.sin(rad)
        # 粗线
        draw.line([(cx, cy), (x2, y2)], fill=color + (alpha,), width=4)
        # 端点圆
        draw.ellipse([x2-8, y2-8, x2+8, y2+8], fill=color + (alpha,))

def draw_geometric_bird(draw, cx, cy, size, color, alpha=255):
    """几何化飞鸟"""
    # 身体（椭圆）
    draw.ellipse([cx-size*0.3, cy-size*0.1, cx+size*0.3, cy+size*0.1],
                 outline=color + (alpha,), width=8)
    # 翅膀（三角形）
    for side in [-1, 1]:
        wing_pts = [
            (cx, cy),
            (cx + side * size * 0.5, cy - size * 0.3),
            (cx + side * size * 0.3, cy + size * 0.1)
        ]
        draw.polygon(wing_pts, outline=color + (alpha,), width=4)
    # 尾巴
    draw.line([(cx - size*0.3, cy), (cx - size*0.6, cy - size*0.15)],
              fill=color + (alpha,), width=4)
    draw.line([(cx - size*0.3, cy), (cx - size*0.6, cy + size*0.15)],
              fill=color + (alpha,), width=4)

def draw_wave_pattern(draw, cx, cy, width, height, color, alpha=255):
    """粗波浪（羽毛感）"""
    for i in range(8):
        offset = i * 25
        pts = []
        for t in range(0, 361, 5):
            x = cx - width/2 + t * width / 360
            y = cy + math.sin(math.radians(t + offset)) * (height * (0.5 + i * 0.1))
            pts.append((x, y))
        draw.line(pts, fill=color + (max(60, alpha - i*15),), width=5)

def generate_variant(index):
    """生成单个变体"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2

    schemes = [
        (ACCENT, TEXT, SOFT),
        (TEXT, ACCENT, SOFT),
        (SOFT, ACCENT, TEXT),
        (ACCENT, SOFT, TEXT),
    ]
    c1, c2, c3 = schemes[index % len(schemes)]

    # 主轨迹螺旋（醒目）
    draw_bold_bird_trail(draw, center, center, 300, c1, 200)

    # 翅膀（粗线）
    draw_bold_wings(draw, center, center, 180, c2, 180)

    # 同心圆
    draw_concentric_rings(draw, center, center, 200, c1, 150)

    # 放射线
    draw_radial_lines(draw, center, center, 250, c3, 120)

    return img

def generate_variant2(index):
    """变体2：波浪+几何飞鸟"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    center = size // 2

    schemes = [
        (ACCENT, SOFT),
        (SOFT, TEXT),
        (TEXT, ACCENT),
        (ACCENT, TEXT),
    ]
    c1, c2 = schemes[index % len(schemes)]

    # 粗波浪
    draw_wave_pattern(draw, center, center, 700, 80, c1, 180)

    # 几何飞鸟
    draw_geometric_bird(draw, center - 50, center, 80, c1, 200)
    draw_geometric_bird(draw, center + 100, center + 80, 60, c2, 150)
    draw_geometric_bird(draw, center - 80, center + 120, 50, c2, 120)

    # 同心圆
    draw_concentric_rings(draw, center, center, 180, c1, 100)

    return img

if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)
    print("生成醒目版飞鸟分形资产...")

    # 每个类型生成4个变体
    for i in range(4):
        img = generate_variant(i)
        img.save(f"{output_dir}/bold_trail_{i+1:02d}.png", "PNG")
        print(f"  轨迹变体 {i+1}/4")

    for i in range(4):
        img = generate_variant2(i)
        img.save(f"{output_dir}/bold_wave_{i+1:02d}.png", "PNG")
        print(f"  波浪变体 {i+1}/4")

    print(f"\n共生成 8 个醒目版变体")
    print(f"存放目录：{output_dir}")
