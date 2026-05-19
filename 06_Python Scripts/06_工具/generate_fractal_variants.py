"""
生成 20 个 Claude 风格分形资产变体
功能：批量生成多种分形图案供选择
依赖：Pillow
"""
from PIL import Image, ImageDraw
import math
import random
import os
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 输出目录
output_dir = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_variants"

def draw_circular_fractal(draw, cx, cy, radius, depth, color, alpha):
    """递归圆形分形"""
    if depth == 0 or radius < 5:
        return
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(bbox, outline=color + (alpha,), width=max(1, 3 - depth))
    for angle in [0, 72, 144, 216, 288]:
        rad = math.radians(angle)
        nx = cx + radius * 0.618 * math.cos(rad)
        ny = cy + radius * 0.618 * math.sin(rad)
        draw_circular_fractal(draw, nx, ny, radius * 0.45, depth - 1, color, max(20, alpha - 25))

def draw_triangular_fractal(draw, x, y, size, depth, color, alpha):
    """递归三角形分形（谢尔宾斯基风格）"""
    if depth == 0 or size < 5:
        return
    h = size * math.sqrt(3) / 2
    points = [
        (x, y - h * 2/3),
        (x - size/2, y + h/3),
        (x + size/2, y + h/3)
    ]
    draw.polygon(points, outline=color + (alpha,), width=1)
    for px, py in points:
        draw_triangular_fractal(draw, px, py, size * 0.5, depth - 1, color, max(20, alpha - 30))

def draw_hexagonal_fractal(draw, cx, cy, radius, depth, color, alpha):
    """递归六边形分形"""
    if depth == 0 or radius < 5:
        return
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(points, outline=color + (alpha,), width=max(1, 2 - depth))
    for px, py in points:
        draw_hexagonal_fractal(draw, px, py, radius * 0.35, depth - 1, color, max(20, alpha - 30))

def draw_organic_fractal(draw, cx, cy, radius, depth, color, alpha):
    """有机曲线分形（Claude 风格）"""
    if depth == 0 or radius < 8:
        return
    # 绘制不规则弧线
    for i in range(3):
        offset = random.uniform(-20, 20)
        arc_start = random.uniform(0, 360)
        arc_end = arc_start + random.uniform(60, 180)
        points = []
        for a in range(int(arc_start), int(arc_end), 10):
            rad = math.radians(a)
            r_var = radius * (0.8 + 0.2 * math.sin(5 * rad))
            points.append((cx + r_var * math.cos(rad), cy + r_var * math.sin(rad)))
        if len(points) > 2:
            draw.line(points, fill=color + (alpha,), width=max(1, 2 - depth))
    # 递归
    for _ in range(2):
        angle = random.uniform(0, 360)
        rad = math.radians(angle)
        nx = cx + radius * 0.5 * math.cos(rad)
        ny = cy + radius * 0.5 * math.sin(rad)
        draw_organic_fractal(draw, nx, ny, radius * 0.5, depth - 1, color, max(20, alpha - 25))

def draw_concentric_fractal(draw, cx, cy, radius, depth, color, alpha):
    """同心圆 + 螺旋分形"""
    if depth == 0 or radius < 5:
        return
    # 同心圆
    for r in range(3):
        bbox = [cx - radius + r*5, cy - radius + r*5, cx + radius - r*5, cy + radius - r*5]
        draw.ellipse(bbox, outline=color + (max(20, alpha - r*15),), width=1)
    # 螺旋线
    points = []
    for t in range(0, 360, 5):
        rad = math.radians(t)
        r = radius * (1 - t / 720)
        points.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    if len(points) > 2:
        draw.line(points, fill=color + (alpha,), width=1)
    draw_concentric_fractal(draw, cx, cy, radius * 0.6, depth - 1, color, max(20, alpha - 25))

def draw_grid_fractal(draw, cx, cy, size, depth, color, alpha):
    """网格分形"""
    if depth == 0 or size < 5:
        return
    half = size / 2
    # 绘制田字格
    draw.rectangle([cx - half, cy - half, cx + half, cy + half], outline=color + (alpha,), width=1)
    draw.line([cx, cy - half, cx, cy + half], fill=color + (alpha,), width=1)
    draw.line([cx - half, cy, cx + half, cy], fill=color + (alpha,), width=1)
    # 递归四个子格
    offsets = [(-half/2, -half/2), (half/2, -half/2), (-half/2, half/2), (half/2, half/2)]
    for ox, oy in offsets:
        draw_grid_fractal(draw, cx + ox, cy + oy, size * 0.5, depth - 1, color, max(20, alpha - 20))

def draw_branch_fractal(draw, cx, cy, length, angle, depth, color, alpha):
    """分形树枝"""
    if depth == 0 or length < 5:
        return
    rad = math.radians(angle)
    ex = cx + length * math.cos(rad)
    ey = cy + length * math.sin(rad)
    draw.line([(cx, cy), (ex, ey)], fill=color + (alpha,), width=max(1, 3 - depth))
    # 两分支
    draw_branch_fractal(draw, ex, ey, length * 0.7, angle - 30, depth - 1, color, max(20, alpha - 25))
    draw_branch_fractal(draw, ex, ey, length * 0.7, angle + 30, depth - 1, color, max(20, alpha - 25))

def draw_voronoi_fractal(draw, points, color, alpha, depth=3):
    """伪 Voronoi 分形"""
    if depth == 0:
        return
    # 绘制随机点连线
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            x1, y1 = points[i]
            x2, y2 = points[j]
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if dist < 150:
                draw.line([(x1, y1), (x2, y2)], fill=color + (int(alpha * (1 - dist/150)),), width=1)
    # 生成子点
    new_points = []
    for _ in range(len(points)):
        px, py = random.choice(points)
        new_points.append((px + random.uniform(-30, 30), py + random.uniform(-30, 30)))
    draw_voronoi_fractal(draw, new_points, color, alpha * 0.7, depth - 1)

def generate_variant(index, draw_func, size=800):
    """生成单个变体"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 配色方案变体
    color_schemes = [
        ((211, 107, 77), (45, 43, 42)),     # 赤陶 + 暖炭
        ((180, 90, 60), (60, 58, 56)),       # 深赤陶
        ((230, 200, 185), (211, 107, 77)),   # 灰桃 + 赤陶
        ((45, 43, 42), (211, 107, 77)),      # 反转配色
        ((160, 120, 100), (80, 60, 50)),     # 暖棕系
    ]
    scheme = color_schemes[index % len(color_schemes)]

    center = size // 2

    # 调用对应的绘制函数
    if draw_func == "circular":
        draw_circular_fractal(draw, center, center, 280, 4, scheme[0], 140)
        draw_circular_fractal(draw, center - 50, center + 40, 150, 3, scheme[1], 70)
    elif draw_func == "triangular":
        draw_triangular_fractal(draw, center, center, 300, 4, scheme[0], 120)
    elif draw_func == "hexagonal":
        draw_hexagonal_fractal(draw, center, center, 250, 4, scheme[0], 120)
    elif draw_func == "organic":
        draw_organic_fractal(draw, center, center, 250, 4, scheme[0], 100)
    elif draw_func == "concentric":
        draw_concentric_fractal(draw, center, center, 300, 4, scheme[0], 100)
    elif draw_func == "grid":
        draw_grid_fractal(draw, center, center, 400, 4, scheme[0], 120)
    elif draw_func == "branch":
        draw_branch_fractal(draw, center, center + 100, 150, -90, 5, scheme[0], 120)
        draw_branch_fractal(draw, center, center + 100, 150, -90, 5, scheme[1], 60)
    elif draw_func == "voronoi":
        points = [(random.uniform(200, 600), random.uniform(200, 600)) for _ in range(8)]
        draw_voronoi_fractal(draw, points, scheme[0], 100, 3)

    # 批量生成变体
    variants = [
        ("circular", "圆形递归"),
        ("triangular", "三角分形"),
        ("hexagonal", "六边形"),
        ("organic", "有机曲线"),
        ("concentric", "同心螺旋"),
        ("grid", "网格分形"),
        ("branch", "分形树枝"),
        ("voronoi", "Voronoi图案"),
    ]

    # 每种类型生成多个变体
    count = 0
    for vf, vname in variants:
        for i in range(3):  # 每种类型3个变体
            output_path = f"{output_dir}/fractal_{count+1:02d}_{vf}.png"
            generate_variant(count, vf, size)
            img.save(output_path, "PNG")
            print(f"生成中: {count+1}/24 - {vname} 变体{i+1}")
            count += 1
            if count >= 24:
                break
        if count >= 24:
            break

if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)

    variants = [
        ("circular", "圆形递归"),
        ("triangular", "三角分形"),
        ("hexagonal", "六边形"),
        ("organic", "有机曲线"),
        ("concentric", "同心螺旋"),
        ("grid", "网格分形"),
        ("branch", "分形树枝"),
        ("voronoi", "Voronoi图案"),
    ]

    # 每种类型3个变体 = 24个
    count = 0
    color_schemes = [
        ((211, 107, 77), (45, 43, 42)),
        ((180, 90, 60), (60, 58, 56)),
        ((230, 200, 185), (211, 107, 77)),
        ((45, 43, 42), (211, 107, 77)),
        ((160, 120, 100), (80, 60, 50)),
        ((200, 160, 140), (100, 80, 60)),
        ((140, 90, 70), (200, 180, 160)),
        ((80, 70, 65), (220, 180, 160)),
    ]

    for vf, vname in variants:
        for i in range(3):
            if count >= 24:
                break

            size = 800
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            scheme = color_schemes[count % len(color_schemes)]
            center = size // 2

            if vf == "circular":
                draw_circular_fractal(draw, center, center, 280, 4, scheme[0], 140)
                draw_circular_fractal(draw, center - 50, center + 40, 150, 3, scheme[1], 70)
            elif vf == "triangular":
                draw_triangular_fractal(draw, center, center, 300, 4, scheme[0], 120)
            elif vf == "hexagonal":
                draw_hexagonal_fractal(draw, center, center, 250, 4, scheme[0], 120)
            elif vf == "organic":
                draw_organic_fractal(draw, center, center, 250, 4, scheme[0], 100)
            elif vf == "concentric":
                draw_concentric_fractal(draw, center, center, 300, 4, scheme[0], 100)
            elif vf == "grid":
                draw_grid_fractal(draw, center, center, 400, 4, scheme[0], 120)
            elif vf == "branch":
                draw_branch_fractal(draw, center, center + 100, 150, -90, 5, scheme[0], 120)
                draw_branch_fractal(draw, center, center + 100, 150, -90, 5, scheme[1], 60)
            elif vf == "voronoi":
                points = [(random.uniform(200, 600), random.uniform(200, 600)) for _ in range(8)]
                draw_voronoi_fractal(draw, points, scheme[0], 100, 3)

            output_path = f"{output_dir}/fractal_{count+1:02d}_{vf}.png"
            img.save(output_path, "PNG")
            print(f"生成中: {count+1}/24 - {vname} 变体{i+1}")
            count += 1

    print(f"\n全部生成完成！共 {count} 个变体")
    print(f"存放目录：{output_dir}")
