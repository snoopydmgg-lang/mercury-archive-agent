#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摄影构图艺术 - 封面生成脚本（一次生成3个风格）
==============================================
基于新古典人文主义视觉系统

生成3个不同风格的封面：
1. 黄金分割 - 几何分形风格
2. 三分法则 - 自然叶脉风格
3. 对角线构图 - 折叠纸张风格

用法:
    python generate_photography_covers.py
"""

import os
import sys
import uuid
import requests
import json
import random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ============================================================
# 豆包 API 配置
# ============================================================
API_KEY = "3140fe69-b4ea-42fa-9d6b-e8257c3f2ff7"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID = "doubao-seedream-5-0-260128"

# ============================================================
# 画布与布局参数
# ============================================================
CANVAS_W = 1080
CANVAS_H = 1440
IMAGE_END = 700
TEXT_BG_START = 700
MARGIN_LEFT = 60
MARGIN_RIGHT = 60
TITLE_Y = 800
SUBTITLE_Y = 920

# ============================================================
# 新古典人文主义色彩系统
# ============================================================
BG_COLOR = (245, 244, 240)      # #F5F4F0 羊皮纸白
INK_COLOR = (45, 43, 42)        # #2D2B2A 暖炭灰
ACCENT_COLOR = (211, 107, 77)   # #D36B4D 赤陶土
PEACH_COLOR = (230, 200, 181)   # #E6C8B5 灰桃色
META_COLOR = (120, 115, 110)    # 元数据灰

# ============================================================
# 三种风格的Prompt配置
# ============================================================
STYLES = [
    {
        "name": "黄金分割",
        "subtitle": "几何秩序的视觉平衡",
        "concept": "黄金分割比例的取景框",
        "prompt": """画面主体：根据'黄金分割比例的取景框'转化的抽象形态——
相机取景框的几何分割、黄金螺旋的构图引导线、画幅比例的视觉秩序。
可参考：取景框网格、构图辅助线、画幅分割、景深标尺。

视觉约束：
- 新古典人文主义风格
- 古典印刷术质感 + 摄影美学
- 色彩系统：羊皮纸白(#F5F4F0) + 暖炭灰(#2D2B2A) + 赤陶土(#D36B4D) + 灰桃色(#E6C8B5)
- 低饱和暖色调，大地色系
- 摄影器材意象（取景框、构图线、画幅比例）

构图约束：
- 画布比例：3:4竖版
- 画面上半部分50%展示主体
- 画面下半部分50%保持纯色负空间留白（羊皮纸白#F5F4F0）
- 强调黄金分割线的秩序感
- 可使用1px细线分割

质感要求：
- 细微纸张纹理
- 2%-5%单色噪点颗粒感（模拟物理印刷品）
- 哑光质感，无光泽
- 古典出版物的微观粗糙感

反向约束（严格禁止）：
- 禁止纯黑(#000000)、纯白(#FFFFFF)
- 禁止文字、水印、Logo、数字
- 禁止3D效果、重阴影、发光效果
- 禁止霓虹光效、高饱和渐变
- 禁止具象图形（人物/建筑/产品/品牌元素/相机实物）
- 禁止赛博朋克、科技感、未来感风格"""
    },
    {
        "name": "三分法则",
        "subtitle": "平衡构图的经典法则",
        "concept": "三分法则的构图网格",
        "prompt": """画面主体：根据'三分法则的构图网格'转化的抽象形态——
九宫格构图辅助线、三分线交点的视觉焦点、画面平衡的几何秩序。
可参考：构图网格、井字线、焦点标记、画面分割。

视觉约束：
- 新古典人文主义风格
- 古典印刷术质感 + 摄影美学
- 色彩系统：羊皮纸白(#F5F4F0) + 暖炭灰(#2D2B2A) + 赤陶土(#D36B4D) + 灰桃色(#E6C8B5)
- 低饱和暖色调，大地色系
- 摄影器材意象（构图网格、辅助线、焦点标记）

构图约束：
- 画布比例：3:4竖版
- 画面上半部分50%展示主体
- 画面下半部分50%保持纯色负空间留白（羊皮纸白#F5F4F0）
- 强调三分线的平衡感
- 可使用1px细线分割

质感要求：
- 细微纸张纹理
- 2%-5%单色噪点颗粒感（模拟物理印刷品）
- 哑光质感，无光泽
- 古典出版物的微观粗糙感

反向约束（严格禁止）：
- 禁止纯黑(#000000)、纯白(#FFFFFF)
- 禁止文字、水印、Logo、数字
- 禁止3D效果、重阴影、发光效果
- 禁止霓虹光效、高饱和渐变
- 禁止具象图形（人物/建筑/产品/品牌元素/相机实物）
- 禁止赛博朋克、科技感、未来感风格"""
    },
    {
        "name": "对角线构图",
        "subtitle": "动态张力的视觉引导",
        "concept": "对角线构图的视觉引导",
        "prompt": """画面主体：根据'对角线构图的视觉引导'转化的抽象形态——
对角线的动态引导、视觉流动的几何轨迹、画面张力的抽象表达。
可参考：对角线分割、视觉引导线、动态平衡、画面张力。

视觉约束：
- 新古典人文主义风格
- 古典印刷术质感 + 摄影美学
- 色彩系统：羊皮纸白(#F5F4F0) + 暖炭灰(#2D2B2A) + 赤陶土(#D36B4D) + 灰桃色(#E6C8B5)
- 低饱和暖色调，大地色系
- 摄影器材意象（对角线、引导线、画面张力）

构图约束：
- 画布比例：3:4竖版
- 画面上半部分50%展示主体
- 画面下半部分50%保持纯色负空间留白（羊皮纸白#F5F4F0）
- 强调对角线的动态张力
- 可使用1px细线分割

质感要求：
- 细微纸张纹理
- 2%-5%单色噪点颗粒感（模拟物理印刷品）
- 哑光质感，无光泽
- 古典出版物的微观粗糙感

反向约束（严格禁止）：
- 禁止纯黑(#000000)、纯白(#FFFFFF)
- 禁止文字、水印、Logo、数字
- 禁止3D效果、重阴影、发光效果
- 禁止霓虹光效、高饱和渐变
- 禁止具象图形（人物/建筑/产品/品牌元素/相机实物）
- 禁止赛博朋克、科技感、未来感风格"""
    }
]

# ============================================================
# 豆包 API 调用
# ============================================================
def generate_image_doubao(prompt: str, negative_prompt: str = None) -> str:
    """调用豆包API生成图片，返回本地路径"""

    if negative_prompt is None:
        negative_prompt = (
            "纯黑, 纯白, 文字, 水印, Logo, 数字, 品牌元素, "
            "3D效果, 重阴影, 发光效果, 霓虹光效, 高饱和渐变, "
            "具象图形, 人物, 建筑, 产品, 赛博朋克, 科技感, 未来感"
        )

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_ID,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": 1080,
        "height": 1440,
        "seed": random.randint(1, 999999999),
        "scale": 7.5,
        "steps": 30
    }

    print(f"\n[豆包API] 正在生成底图...")
    print(f"[Prompt] {prompt[:100]}...")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"豆包API调用失败: {response.status_code} - {response.text}")

    result = response.json()

    if "data" not in result or not result["data"]:
        raise Exception(f"豆包API返回数据为空: {result}")

    image_url = result["data"][0]["url"]
    print(f"[豆包API] 底图生成成功: {image_url}")

    # 下载图片
    img_response = requests.get(image_url)
    if img_response.status_code != 200:
        raise Exception(f"下载图片失败: {img_response.status_code}")

    # 保存到临时文件
    temp_path = Path(__file__).parent / "assets" / f"temp_{uuid.uuid4().hex[:8]}.png"
    temp_path.parent.mkdir(exist_ok=True)

    with open(temp_path, 'wb') as f:
        f.write(img_response.content)

    print(f"[豆包API] 底图已保存: {temp_path}")
    return str(temp_path)

# ============================================================
# 文字渲染
# ============================================================
def render_text_on_image(base_image_path: str, title: str, subtitle: str, volume: str = "VOL.01") -> Image.Image:
    """在底图上渲染文字"""

    img = Image.open(base_image_path).convert("RGBA")

    # 确保底图尺寸正确
    if img.size != (CANVAS_W, CANVAS_H):
        img = img.resize((CANVAS_W, CANVAS_H), Image.Resampling.LANCZOS)

    # 裁剪底图，只保留上半部分（0-720px）
    img = img.crop((0, 0, CANVAS_W, 720))

    # 创建完整画布
    canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)

    # 将裁剪后的底图粘贴到画布上半部分
    canvas.paste(img, (0, 0))

    # 创建文字层
    txt_layer = Image.new("RGBA", canvas.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # 加载字体
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 72)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
        meta_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        meta_font = ImageFont.load_default()

    # 绘制主标题
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (CANVAS_W - title_w) // 2
    draw.text((title_x, TITLE_Y), title, fill=INK_COLOR, font=title_font)

    # 绘制副标题
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_w = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (CANVAS_W - subtitle_w) // 2
    draw.text((subtitle_x, SUBTITLE_Y), subtitle, fill=META_COLOR, font=subtitle_font)

    # 绘制分隔线
    line_y = TITLE_Y - 40
    line_x1 = (CANVAS_W - 200) // 2
    line_x2 = line_x1 + 200
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=ACCENT_COLOR, width=1)

    # 绘制底部元数据
    meta_text = f"{volume} · MERCURY ARCHIVE"
    meta_bbox = draw.textbbox((0, 0), meta_text, font=meta_font)
    meta_w = meta_bbox[2] - meta_bbox[0]
    meta_x = (CANVAS_W - meta_w) // 2
    meta_y = CANVAS_H - 80
    draw.text((meta_x, meta_y), meta_text, fill=META_COLOR, font=meta_font)

    # 合并图层
    canvas = canvas.convert("RGBA")
    canvas = Image.alpha_composite(canvas, txt_layer)

    return canvas.convert("RGB")

# ============================================================
# 添加噪点纹理
# ============================================================
def add_noise_texture(img: Image.Image, intensity: float = 0.03) -> Image.Image:
    """添加2-5%单色噪点纹理"""

    img_array = list(img.getdata())
    noisy_array = []

    for pixel in img_array:
        r, g, b = pixel
        noise = random.randint(-int(255 * intensity), int(255 * intensity))
        r = max(0, min(255, r + noise))
        g = max(0, min(255, g + noise))
        b = max(0, min(255, b + noise))
        noisy_array.append((r, g, b))

    noisy_img = Image.new("RGB", img.size)
    noisy_img.putdata(noisy_array)

    return noisy_img

# ============================================================
# 主流程
# ============================================================
def generate_all_covers():
    """生成3个风格的封面"""

    print("\n" + "="*60)
    print("摄影构图艺术 - 封面生成流水线")
    print("="*60)

    # 创建输出目录
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    inbox_dir = Path(__file__).parent.parent.parent / "00_InBox_收件箱"
    inbox_dir.mkdir(exist_ok=True)

    date_str = datetime.now().strftime("%m%d")

    results = []

    for i, style in enumerate(STYLES, 1):
        print(f"\n{'='*60}")
        print(f"正在生成第 {i}/3 个封面：{style['name']}")
        print(f"{'='*60}")

        try:
            # Step 1: 调用豆包API生成底图
            base_image_path = generate_image_doubao(style['prompt'])

            # Step 2: 渲染文字
            print(f"\n[文字渲染] 正在渲染文字...")
            final_img = render_text_on_image(
                base_image_path,
                title="摄影构图艺术",
                subtitle=style['subtitle'],
                volume=f"VOL.0{i}"
            )

            # Step 3: 添加噪点纹理
            print(f"[质感处理] 正在添加噪点纹理...")
            final_img = add_noise_texture(final_img, intensity=0.03)

            # Step 4: 保存到输出目录
            output_filename = f"{date_str}-摄影构图艺术-封面{i:02d}-{style['name']}.png"
            output_path = output_dir / output_filename
            final_img.save(output_path, quality=95)
            print(f"[保存] 已保存到: {output_path}")

            # Step 5: 复制到收件箱
            inbox_path = inbox_dir / output_filename
            final_img.save(inbox_path, quality=95)
            print(f"[复制] 已复制到收件箱: {inbox_path}")

            results.append({
                "style": style['name'],
                "output_path": str(output_path),
                "inbox_path": str(inbox_path)
            })

            # 清理临时文件
            if os.path.exists(base_image_path):
                os.remove(base_image_path)
                print(f"[清理] 已删除临时文件: {base_image_path}")

        except Exception as e:
            print(f"\n[错误] 生成封面失败: {e}")
            continue

    # 输出总结
    print("\n" + "="*60)
    print("生成完成！")
    print("="*60)

    for i, result in enumerate(results, 1):
        print(f"\n封面 {i}: {result['style']}")
        print(f"  输出路径: {result['output_path']}")
        print(f"  收件箱路径: {result['inbox_path']}")

    print("\n" + "="*60)

# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    generate_all_covers()
