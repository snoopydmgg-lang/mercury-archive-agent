#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆包 API 底图生成脚本
读取 covers.csv -> 调用豆包文生图 -> 下载到底图目录
"""

import os
import sys
import csv
import uuid
import base64
import traceback

print("[DEBUG] 1. 脚本开始解析...")

# 检查 requests
try:
    import requests
    print("[DEBUG] 2. requests 模块导入成功")
except ImportError as e:
    print(f"[FATAL] requests 模块导入失败: {e}")
    print("[FATAL] 请运行: pip install requests")
    sys.exit(1)

# ============================================================
# 豆包 API 配置
# ============================================================
API_KEY = "3140fe69-b4ea-42fa-9d6b-e8257c3f2ff7"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID = "doubao-seedream-5-0-260128"

print(f"[DEBUG] 3. API Key 已配置: {API_KEY[:8]}...")

# ============================================================
# Prompt 模板 (3:4 竖版封面 - 日式极简美学)
# ============================================================
# 3:4 竖版构图。上半部分：极简几何图形+大量留白。下半部分：纯白背景。
POSITIVE_PROMPT = (
    "Pure warm white background, flat minimal design, zero visual noise. "
    "Only one small crimson red circle in the upper right corner, nothing else. "
    "Massive negative white space, Japanese ma aesthetic. "
    "Subtle washi paper texture, 2-5% micro grain. "
    "No frames, no lines, no geometric structures, no grids, no borders, no intersecting lines. "
    "Completely flat, zero depth, zero 3D rendering. "
    "8K resolution, ultra-clean, masterpiece."
)

NEGATIVE_PROMPT = (
    "watermark, text, letters, characters, 3D rendering, complex structure, "
    "frame, frames, line, lines, geometric, grid, border, border lines, intersecting lines, "
    "messy, chaotic, human face, body, fingers, hand, "
    "low quality, blurry, distortion, neon lights, cyberpunk"
)

# ============================================================
# 风格预设 Prompt 矩阵（基于用户 VIS 规范）
# ============================================================
STYLE_PROMPTS = {
    "classic-print": {
        "positive": (
            "Minimalist, classical printmaking aesthetic, pure cream white warm paper background #F5F4F0, "
            "subtle organic paper texture, only one extremely restrained amorphous terracotta brick-red "
            "color block at the edge, massive white space, high signal-to-noise ratio. "
            "Ultra-clean, fine grain, masterpiece. "
            "Strictly non-geometric, fluid edges, organic irregular shape only."
        ),
        "negative": (
            "circles, concentric circles, target shapes, dots, radial patterns, "
            "geometric shapes, frames, grids, 3D rendering, cyberpunk, mechanical structures, "
            "excess lines, unnecessary objects, watermark, text, letters, characters, "
            "human face, body, fingers, high saturation, neon lights, messy, chaotic"
        ),
    },
    "organic-botanical": {
        "positive": (
            "Minimalist, neo-classical humanism, pure cream white warm paper background #F5F4F0, "
            "upper right corner: only ONE single ginkgo leaf silhouette, semi-transparent, "
            "muted gray-peach tone, delicate fan-shape with central vein, "
            "absolutely NO circles, NO concentric rings, NO dots, NO radial lines, "
            "massive white space, ultra-clean, fine grain, masterpiece. "
            "右上角仅有一片极简的、半透明的银杏叶剪影，无任何其他元素。"
        ),
        "negative": (
            "ABSOLUTELY NO circles, ABSOLUTELY NO concentric circles, ABSOLUTELY NO target shapes, "
            "ABSOLUTELY NO dots, ABSOLUTELY NO dot patterns, ABSOLUTELY NO radial patterns, "
            "ABSOLUTELY NO geometric shapes, ABSOLUTELY NO regular curves, ABSOLUTELY NO symmetrical forms, "
            "mechanical feel, high-dimensional matrix, complex colors, excess objects, "
            "frame, frames, grid, grids, intersecting lines, watermark, text, letters, characters, "
            "human face, body, fingers, neon lights, cyberpunk, messy, chaotic"
        ),
    },
    "academic-grid": {
        "positive": (
            "Minimalist, academic publication style, pure cream white warm paper background #F5F4F0, "
            "with extremely faint subtle classical typographic grid lines, "
            "massive white space, extremely restrained, scholarly. "
            "Ultra-clean, fine grain, high signal-to-noise ratio, masterpiece. "
            "Strictly non-decorative, minimal grid reference only."
        ),
        "negative": (
            "excess decorative graphics, 3D elements, vivid colors, complex structures, "
            "circles, concentric circles, target shapes, dots, radial patterns, "
            "mechanical feel, frame, frames, intersecting lines, watermark, "
            "text, letters, characters, human face, body, fingers, "
            "neon lights, cyberpunk, messy, chaotic"
        ),
    },
}
DEFAULT_STYLE = "classic-print"


def get_style_prompt(style: str) -> str:
    style = style.lower()
    if style in STYLE_PROMPTS:
        return STYLE_PROMPTS[style]["positive"]
    return STYLE_PROMPTS[DEFAULT_STYLE]["positive"]


def get_style_negative(style: str) -> str:
    style = style.lower()
    if style in STYLE_PROMPTS and "negative" in STYLE_PROMPTS[style]:
        return STYLE_PROMPTS[style]["negative"]
    return NEGATIVE_PROMPT


def image_to_base64(image_path):
    """将本地图片转换为 base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_format(image_path):
    """根据文件扩展名判断图片格式"""
    ext = os.path.splitext(image_path)[1].lower()
    format_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                  '.gif': 'image/gif', '.webp': 'image/webp'}
    return format_map.get(ext, 'image/png')


def generate_image(prompt, size="1920x1080", negative_prompt=None):
    """
    调用豆包文生图 API
    """
    print(f"[DEBUG] 调用豆包 API，尺寸: {size}")

    # 构建请求数据
    data = {
        "model": MODEL_ID,
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT if negative_prompt is None else negative_prompt,
        "size": size,
        "quality": "hd"
    }

    # 调用 API
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"[DEBUG] 发送请求到: {url}")
    print(f"[DEBUG] 请求数据: model={MODEL_ID}, prompt长度={len(prompt)}")

    response = requests.post(url, headers=headers, json=data, timeout=180)
    print(f"[DEBUG] 响应状态码: {response.status_code}")

    if response.status_code != 200:
        error_msg = f"API error: {response.status_code} - {response.text}"
        print(f"[ERROR] {error_msg}")
        raise Exception(error_msg)

    result = response.json()
    print(f"[DEBUG] 响应内容: {result}")

    if "data" not in result or len(result["data"]) == 0:
        raise Exception(f"API返回数据格式异常: {result}")

    image_url = result["data"][0]["url"]
    print(f"[DEBUG] 获得图片URL: {image_url[:50]}...")
    return image_url


def download_image(image_url, output_path):
    """下载图片并保存"""
    print(f"[DEBUG] 开始下载图片到: {output_path}")
    response = requests.get(image_url, timeout=60)
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"[DEBUG] 下载完成，文件大小: {os.path.getsize(output_path)} bytes")


def ensure_assets_dir():
    """确保 assets 目录存在"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"[DEBUG] 创建目录: {assets_dir}")
    return assets_dir


def find_missing_assets():
    """找出 covers.csv 中缺失底图的行"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "covers.csv")

    missing = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                img_path = os.path.join(script_dir, row["image_path"])
                if not os.path.exists(img_path):
                    missing.append(row)
                    print(f"[DEBUG] 发现缺失底图: {row['id']} -> {row['image_path']}")
    else:
        print(f"[WARN] CSV文件不存在: {csv_path}")

    return missing


def generate_assets_for_csv(size="1920x2560", style=None):
    """为 covers.csv 中缺失底图的行生成底图"""
    size = validate_size(size)
    print(f"[INFO] 进入 CSV 模式，尺寸: {size}, 风格: {style}...")
    assets_dir = ensure_assets_dir()
    missing = find_missing_assets()

    if not missing:
        print("[INFO] 所有底图都已存在，无需生成")
        return

    print(f"[INFO] 发现 {len(missing)} 个缺失底图，开始生成...")

    prompt = get_style_prompt(style) if style else POSITIVE_PROMPT
    negative = get_style_negative(style) if style else NEGATIVE_PROMPT

    for row in missing:
        try:
            print(f"[INFO] 正在为 {row['id']} 生成底图 [style={style}]...")
            image_url = generate_image(prompt, size=size, negative_prompt=negative)

            # 生成文件名
            filename = f"{uuid.uuid4().hex[:8]}_art.png"
            output_path = os.path.join(assets_dir, filename)

            # 下载
            download_image(image_url, output_path)
            print(f"[SUCCESS] 已保存: {output_path}")
            print(f"[INFO] 请将以下路径填入 covers.csv:")
            print(f"       image_path: assets/{filename}")

        except Exception as e:
            print(f"[ERROR] 为 {row['id']} 生成底图失败: {e}")
            traceback.print_exc()


def validate_size(size):
    """验证尺寸是否满足最小像素要求 (3686400)"""
    parts = size.split("x")
    if len(parts) != 2:
        raise ValueError(f"尺寸格式错误: {size}，应为 WxH 格式")
    w, h = int(parts[0]), int(parts[1])
    pixels = w * h
    if pixels < 3686400:
        print(f"[WARN] 尺寸 {size}={pixels} 像素不足3686400，自动调整为 1920x2560(3:4)")
        return "1920x2560"  # 3:4比例，满足最小像素
    return size


def batch_generate(count=2, size="1920x2560", style=None):
    """批量生成底图（不依赖 CSV）"""
    size = validate_size(size)
    print(f"[INFO] 进入批量生成模式，生成 {count} 张，尺寸: {size}, 风格: {style}...")
    assets_dir = ensure_assets_dir()

    prompt = get_style_prompt(style) if style else POSITIVE_PROMPT
    negative = get_style_negative(style) if style else NEGATIVE_PROMPT

    for i in range(count):
        try:
            print(f"[INFO] === 生成第 {i+1}/{count} 张 [style={style}] ===")
            image_url = generate_image(prompt, size=size, negative_prompt=negative)

            filename = f"{uuid.uuid4().hex[:8]}_art.png"
            output_path = os.path.join(assets_dir, filename)

            download_image(image_url, output_path)
            print(f"[SUCCESS] 第 {i+1} 张已保存: assets/{filename}")

        except Exception as e:
            print(f"[ERROR] 第 {i+1} 张生成失败: {e}")
            traceback.print_exc()


def main():
    print("[DEBUG] 4. 进入 main() 函数...")

    import argparse

    print("[DEBUG] 5. argparse 初始化...")
    parser = argparse.ArgumentParser(description="豆包底图生成工具")
    parser.add_argument("--count", type=int, default=0,
                        help="批量生成数量（不指定则读取covers.csv缺失项）")
    parser.add_argument("--size", type=str, default="1920x2560",
                        help="输出尺寸，如 1920x2560(3:4) 或 2560x1440(16:9)，最小像素3686400")
    parser.add_argument("--style", default=DEFAULT_STYLE,
                        choices=["classic-print", "organic-botanical", "academic-grid"],
                        help=f"底图风格 (默认: {DEFAULT_STYLE})")

    args = parser.parse_args()
    print(f"[DEBUG] 6. 命令行参数解析完成: count={args.count}, size={args.size}, style={args.style}")

    if args.count > 0:
        batch_generate(args.count, args.size, style=args.style)
    else:
        generate_assets_for_csv(args.size, style=args.style)

    print("[DEBUG] 7. 执行完成...")


if __name__ == "__main__":
    try:
        print("[DEBUG] 0. __name__ == '__main__' 入口...")
        main()
    except Exception as e:
        print(f"[FATAL] 脚本执行致命错误: {e}")
        traceback.print_exc()
        sys.exit(1)