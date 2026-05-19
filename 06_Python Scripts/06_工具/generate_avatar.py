#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成个人头像 - 基于视觉规范
色彩：背景 #F5F4F0 / 文字 #2D2B2A / 点缀 #D36B4D / 辅助 #E6C8B5
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import random

def generate_avatar():
    size = 1080
    img = Image.new('RGB', (size, size), '#F5F4F0')
    draw = ImageDraw.Draw(img)

    # ===== 有机分形 M 形图案 =====
    center_x, center_y = size // 2, size // 2 - 50
    scale = 280

    # 颜色定义
    primary = '#D36B4D'    # 赤陶土
    secondary = '#E6C8B5' # 灰桃色
    ink = '#2D2B2A'       # 暖炭灰

    # 绘制有机花瓣 M 形（4个象限的弧线组成）
    def draw_petal(draw, cx, cy, angle, length, color, alpha=255):
        """绘制单个花瓣"""
        points = []
        steps = 30
        for i in range(steps + 1):
            t = i / steps
            # 贝塞尔曲线形成花瓣形状
            x = cx + length * math.sin(t * math.pi + angle) * (1 + 0.3 * math.sin(t * math.pi * 2))
            y = cy + length * math.cos(t * math.pi + angle) * (1 + 0.3 * math.sin(t * math.pi * 2))
            points.append((x, y))

        # 将颜色转换为RGBA以便透明度处理
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        draw.line(points, fill=(r, g, b), width=12)

    # 绘制M形的有机分形结构
    # 左半M
    draw_petal(draw, center_x - 80, center_y, 0, scale * 0.8, primary)
    draw_petal(draw, center_x - 80, center_y, math.pi * 0.3, scale * 0.7, secondary)
    draw_petal(draw, center_x - 80, center_y, math.pi * 0.6, scale * 0.6, primary, alpha=180)

    # 右半M
    draw_petal(draw, center_x + 80, center_y, 0, scale * 0.8, primary)
    draw_petal(draw, center_x + 80, center_y, math.pi * 0.4, scale * 0.7, secondary)
    draw_petal(draw, center_x + 80, center_y, math.pi * 0.7, scale * 0.6, primary, alpha=180)

    # 中间连接 - 柔和的弧线
    draw_petal(draw, center_x, center_y + 50, math.pi * 0.5, scale * 0.5, secondary, alpha=150)

    # 添加圆形节点点缀
    for offset_x, offset_y in [(-80, 0), (80, 0), (0, -100), (0, 50)]:
        node_x = center_x + offset_x
        node_y = center_y + offset_y
        draw.ellipse([node_x - 15, node_y - 15, node_x + 15, node_y + 15], fill=primary)

    # 中心节点
    draw.ellipse([center_x - 20, center_y - 20, center_x + 20, center_y + 20], fill=ink)

    # ===== 添加噪点质感 (3%) =====
    noise_img = Image.new('RGB', (size, size))
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            # 3%的像素添加噪点
            if random.random() < 0.03:
                noise = random.randint(-15, 15)
                # 获取原图该位置颜色
                orig_r, orig_g, orig_b = img.getpixel((x, y))
                r = max(0, min(255, orig_r + noise))
                g = max(0, min(255, orig_g + noise))
                b = max(0, min(255, orig_b + noise))
                row.append((r, g, b))
            else:
                row.append(img.getpixel((x, y)))
        pixels.append(row)

    # 转换为图像
    for y in range(size):
        for x in range(size):
            noise_img.putpixel((x, y), pixels[y][x])

    # 高斯模糊使噪点更自然
    noise_img = noise_img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # ===== 保存 =====
    output_path = 'E:/1.work/douyin/1.shuixing/00_InBox_收件箱/Claude头像_有机M形.png'
    noise_img.save(output_path, 'PNG', quality=95)
    print(f'[SUCCESS] 头像已生成: {output_path}')
    return output_path

if __name__ == '__main__':
    generate_avatar()
