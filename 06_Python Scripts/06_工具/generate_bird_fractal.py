"""
飞鸟主题分形资产
- 鸟群V字形飞行轨迹
- 展翅轮廓
- 羽毛纹理
"""
from PIL import Image, ImageDraw
import math
import os
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ACCENT = (211, 107, 77)  # 赤陶土
TEXT = (45, 43, 42)      # 暖炭灰
SOFT = (230, 200, 185)   # 灰桃色
SOFT_LIGHT = (240, 235, 225)

output_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"
os.makedirs(output_dir, exist_ok=True)

def draw_bird_shape(draw, cx, cy, size, color, alpha, angle=0):
    """绘制一只展翅飞鸟"""
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    # 鸟身（椭圆）
    bx, by = cx, cy
    # 翅膀（左）
    wl = []
    for t in range(-60, 1, 5):
        r = size * (0.3 + 0.7 * math.cos(math.radians(t * 0.8)))
        wx = bx + r * math.cos(math.radians(t - 90))
        wy = by + r * math.sin(math.radians(t - 90))
        # 旋转
        rx = cx + (wx - cx) * cos_a - (wy - cy) * sin_a
        ry = cy + (wx - cx) * sin_a + (wy - cy) * cos_a
        wl.append((rx, ry))
    # 翅膀（右）
    wr = []
    for t in range(0, 61, 5):
        r = size * (0.3 + 0.7 * math.cos(math.radians(t * 0.8)))
        wx = bx + r * math.cos(math.radians(t - 90))
        wy = by + r * math.sin(math.radians(t - 90))
        rx = cx + (wx - cx) * cos_a - (wy - cy) * sin_a
        ry = cy + (wx - cx) * sin_a + (wy - cy) * cos_a
        wr.append((rx, ry))

    if len(wl) > 1:
        draw.line(wl, fill=color + (alpha,), width=2)
    if len(wr) > 1:
        draw.line(wr, fill=color + (alpha,), width=2)
    # 身体
    draw.ellipse([cx-size*0.15, cy-size*0.08, cx+size*0.15, cy+size*0.08],
                 outline=color + (alpha,), width=2)

def draw_bird_trail(draw, cx, cy, size, color, alpha):
    """鸟群V字形飞行轨迹"""
    # V字形主线
    points_l = []
    points_r = []
    for i in range(20):
        t = i / 19
        # 左边
        x1 = cx - size * 0.5 * t
        y1 = cy - size * 0.3 * t
        points_l.append((x1, y1))
        # 右边
        x2 = cx + size * 0.5 * t
        y2 = cy - size * 0.3 * t
        points_r.append((x2, y2))

    for i in range(len(points_l) - 1):
        a = int(alpha * (1 - i / len(points_l) * 0.5))
        draw.line([points_l[i], points_l[i+1]], fill=color + (max(40, a),), width=3)
        draw.line([points_r[i], points_r[i+1]], fill=color + (max(40, a),), width=3)

    # 连接线（V底）
    draw.line([points_l[-1], points_r[-1]], fill=color + (alpha,), width=2)

def draw_feather(draw, cx, cy, size, angle, color, alpha):
    """单根羽毛"""
    rad = math.radians(angle)
    # 羽轴
    for t in range(0, 61, 3):
        r = size * t / 60
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        # 羽枝
        for side in [-1, 1]:
            sr = r * 0.3
            sx = x + sr * math.cos(math.radians(angle + side * 80))
            sy = y + sr * math.sin(math.radians(angle + side * 80))
            draw.line([(x, y), (sx, sy)], fill=color + (alpha,), width=1)

def draw_feather_group(draw, cx, cy, size, color, alpha):
    """羽毛群"""
    for i in range(8):
        angle = i * 45 + 15
        draw_feather(draw, cx, cy, size, angle, color, alpha)

def draw_wing_arc(draw, cx, cy, size, color, alpha):
    """翅膀展开的弧线（多羽毛感）"""
    for i in range(5):
        offset = i * 20
        pts = []
        for t in range(-50, 51, 3):
            r = size * (0.2 + 0.8 * math.cos(math.radians(t * 0.9)))
            x = cx + r * math.cos(math.radians(t + offset))
            y = cy + r * math.sin(math.radians(t + offset))
            pts.append((x, y))
        if len(pts) > 1:
            draw.line(pts, fill=color + (alpha - i*15,), width=2)

def add_grain_rgba(img, intensity=0.03):
    w, h = img.size
    noise = Image.new('RGBA', (w, h))
    npixels = noise.load()
    for i in range(w):
        for j in range(h):
            v = int(random.gauss(0, 128 * intensity))
            npixels[i, j] = (0, 0, 0, max(0, v))
    return Image.alpha_composite(img, noise)

def generate_bird_variant(index):
    """鸟群飞行轨迹变体"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    schemes = [
        (ACCENT, SOFT, TEXT),
        (SOFT, ACCENT, TEXT),
        (TEXT, ACCENT, SOFT),
    ]
    c1, c2, c3 = schemes[index % 3]

    # V字形飞行轨迹
    draw_bird_trail(draw, cx, cy + 50, 250, c1, 180)

    # 多只飞鸟
    positions = [(cx - 80, cy - 60), (cx + 80, cy - 60), (cx, cy - 120)]
    for i, (px, py) in enumerate(positions):
        draw_bird_shape(draw, px, py, 50, c1, 160, angle=-20 + i*20)

    # 羽毛群
    draw_feather_group(draw, cx + 100, cy + 80, 60, c2, 100)
    draw_feather_group(draw, cx - 120, cy + 100, 50, c3, 80)

    return add_grain_rgba(img, 0.03)

def generate_wing_variant(index):
    """展翅形态变体"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    schemes = [
        (ACCENT, SOFT),
        (SOFT, TEXT),
        (TEXT, ACCENT),
    ]
    c1, c2 = schemes[index % 3]

    # 主翅膀弧线
    draw_wing_arc(draw, cx, cy, 280, c1, 160)

    # 多层翅膀
    draw_wing_arc(draw, cx, cy, 200, c2, 120)
    draw_wing_arc(draw, cx, cy, 120, c1, 80)

    # 中心飞鸟
    draw_bird_shape(draw, cx, cy, 40, c1, 180)

    return add_grain_rgba(img, 0.03)

def generate_feather_variant(index):
    """羽毛纹理变体"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    schemes = [
        (ACCENT, SOFT, TEXT),
        (SOFT, ACCENT, TEXT),
        (TEXT, SOFT, ACCENT),
    ]
    c1, c2, c3 = schemes[index % 3]

    # 羽毛群（中心发射）
    for i in range(12):
        angle = i * 30
        draw_feather(draw, cx, cy, 150, angle, c1, 140 - i*5)
        draw_feather(draw, cx, cy, 100, angle + 15, c2, 100 - i*5)

    # 飞鸟点缀
    draw_bird_shape(draw, cx - 50, cy - 80, 35, c1, 120, angle=-15)
    draw_bird_shape(draw, cx + 60, cy - 50, 30, c3, 100, angle=10)

    return add_grain_rgba(img, 0.03)

def generate_flight_variant(index):
    """飞行轨迹+羽毛综合变体"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    schemes = [
        (ACCENT, SOFT, TEXT),
        (SOFT, TEXT, ACCENT),
        (TEXT, ACCENT, SOFT),
        (ACCENT, TEXT, SOFT),
    ]
    c1, c2, c3 = schemes[index % 4]

    # 飞行轨迹
    draw_bird_trail(draw, cx, cy + 30, 280, c1, 160)

    # 飞鸟群
    for i in range(5):
        bx = cx + (i - 2) * 50
        by = cy - 50 + abs(i - 2) * 30
        draw_bird_shape(draw, bx, by, 35, c1, 140, angle=-10 + i*5)

    # 羽毛装饰
    draw_feather_group(draw, cx + 150, cy + 150, 80, c2, 100)
    draw_feather_group(draw, cx - 180, cy + 120, 70, c3, 80)

    return add_grain_rgba(img, 0.03)

if __name__ == "__main__":
    print("生成飞鸟主题分形资产...\n")

    # 鸟群飞行 x2
    for i in range(2):
        img = generate_bird_variant(i)
        img.save(f"{output_dir}/bird_flight_{i+1:02d}.png", "PNG")
        print(f"  鸟群飞行 {i+1}/2")

    # 展翅形态 x2
    for i in range(2):
        img = generate_wing_variant(i)
        img.save(f"{output_dir}/bird_wing_{i+1:02d}.png", "PNG")
        print(f"  展翅形态 {i+1}/2")

    # 羽毛纹理 x2
    for i in range(2):
        img = generate_feather_variant(i)
        img.save(f"{output_dir}/bird_feather_{i+1:02d}.png", "PNG")
        print(f"  羽毛纹理 {i+1}/2")

    # 综合变体 x2
    for i in range(2):
        img = generate_flight_variant(i)
        img.save(f"{output_dir}/bird_mixed_{i+1:02d}.png", "PNG")
        print(f"  综合变体 {i+1}/2")

    print(f"\n共 8 个飞鸟主题分形")
