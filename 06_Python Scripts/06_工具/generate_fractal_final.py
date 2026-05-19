"""
飞鸟集分形资产（修复版）
- 内圈：赤陶土 #D36B4D 分形
- 中层：灰桃色螺旋
- 外圈：淡灰桃色呼吸
- 骨架：1px 暖炭灰
- 质感：3% 单色杂色
"""
from PIL import Image, ImageDraw
import math
import os
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 规范四色
ACCENT = (211, 107, 77)  # #D36B4D 赤陶土
TEXT = (45, 43, 42)      # #2D2B2A 暖炭灰
SOFT = (230, 200, 185)   # #E6C8B5 灰桃色
SOFT_LIGHT = (240, 235, 225)  # 淡灰桃色

output_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"
os.makedirs(output_dir, exist_ok=True)

def draw_spiral(draw, cx, cy, size, color, alpha, turns=2.5, width=2):
    """绘制螺旋线"""
    points = []
    for i in range(0, int(turns * 360) + 1, 3):
        rad = math.radians(i)
        t = i / (turns * 360)
        r = size * (0.15 + 0.85 * t)
        x = cx + r * math.cos(rad) * 1.2
        y = cy + r * math.sin(rad) * 0.85
        points.append((x, y))
    for i in range(len(points) - 1):
        a = int(alpha * (1 - i / len(points) * 0.5))
        draw.line([points[i], points[i+1]], fill=color + (max(40, a),), width=width)

def draw_inner_flower(draw, cx, cy, size, depth, color, alpha):
    """内圈花瓣分形"""
    if depth == 0 or size < 10:
        return
    # 6瓣
    for i in range(6):
        angle = i * 60
        pts = []
        for t in range(-25, 26, 3):
            rad = math.radians(angle + t)
            r = size * (0.2 + 0.8 * math.cos(math.radians(t * 1.8)))
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        if len(pts) > 2:
            draw.line(pts, fill=color + (alpha,), width=2)
    # 递归
    for i in range(6):
        rad = math.radians(i * 60)
        nx = cx + size * 0.5 * math.cos(rad)
        ny = cy + size * 0.5 * math.sin(rad)
        draw_inner_flower(draw, nx, ny, size * 0.38, depth-1, color, max(30, alpha-25))

def draw_rays(draw, cx, cy, size, color, alpha):
    """12点放射线"""
    for i in range(12):
        rad = math.radians(i * 30)
        x2 = cx + size * math.cos(rad)
        y2 = cy + size * math.sin(rad)
        draw.line([(cx, cy), (x2, y2)], fill=color + (alpha,), width=1)

def draw_dots(draw, cx, cy, size, color, alpha):
    """端点圆点"""
    for i in range(12):
        rad = math.radians(i * 30)
        x2 = cx + size * math.cos(rad)
        y2 = cy + size * math.sin(rad)
        draw.ellipse([x2-5, y2-5, x2+5, y2+5], fill=color + (alpha,))

def add_grain_to_rgba(img, intensity=0.03):
    """给RGBA图片叠加3%单色杂色"""
    w, h = img.size
    noise = Image.new('RGBA', (w, h))
    npixels = noise.load()
    for i in range(w):
        for j in range(h):
            v = int(random.gauss(0, 128 * intensity))
            npixels[i, j] = (0, 0, 0, max(0, v))
    return Image.alpha_composite(img, noise)

def generate_fractal(index):
    """生成单个分形"""
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # 色彩方案
    schemes = [
        # 方案1：赤陶核心
        {"inner": ACCENT, "spiral": SOFT, "outer": SOFT_LIGHT, "skeleton": TEXT, "dots": ACCENT},
        # 方案2：灰桃核心
        {"inner": SOFT, "spiral": ACCENT, "outer": SOFT_LIGHT, "skeleton": TEXT, "dots": SOFT},
        # 方案3：双色调
        {"inner": ACCENT, "spiral": (200, 170, 150), "outer": SOFT, "skeleton": TEXT, "dots": ACCENT},
        # 方案4：暖炭灰主
        {"inner": TEXT, "spiral": ACCENT, "outer": SOFT, "skeleton": TEXT, "dots": TEXT},
        # 方案5：赤陶+淡灰桃
        {"inner": ACCENT, "spiral": SOFT, "outer": (220, 210, 200), "skeleton": (80, 75, 70), "dots": ACCENT},
        # 方案6：灰桃渐变
        {"inner": SOFT, "spiral": SOFT_LIGHT, "outer": (235, 230, 220), "skeleton": TEXT, "dots": SOFT},
    ]
    s = schemes[index % len(schemes)]

    # 外圈螺旋（最淡，最外层）
    draw_spiral(draw, cx, cy, 300, s["outer"], 60, turns=1.5, width=1)

    # 中层螺旋（灰桃色）
    draw_spiral(draw, cx, cy, 250, s["spiral"], 100, turns=2.5, width=2)

    # 内圈花瓣（赤陶土，视觉焦点）
    draw_inner_flower(draw, cx, cy, 100, 3, s["inner"], 180)

    # 放射骨架（1px暖炭灰，弱化）
    draw_rays(draw, cx, cy, 280, s["skeleton"], 50)

    # 端点圆点
    draw_dots(draw, cx, cy, 280, s["dots"], 120)

    # 叠加3%杂色
    img = add_grain_to_rgba(img, 0.03)

    return img

if __name__ == "__main__":
    print("生成修复版分形资产...\n")

    for i in range(6):
        img = generate_fractal(i)
        output_path = f"{output_dir}/opt_fractal_{i+1:02d}.png"
        img.save(output_path, "PNG")
        print(f"  生成：opt_fractal_{i+1:02d}.png")

    print(f"\n共 6 个，存放：{output_dir}")
