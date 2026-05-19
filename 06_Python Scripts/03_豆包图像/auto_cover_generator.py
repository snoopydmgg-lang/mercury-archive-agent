#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动封面生成器 - 集成到文案生成流程
====================================
基于 auto_cover_engine.py,为文案生成流程提供自动封面生成

核心功能:
1. 从文案 MD 文件中提取元数据(标题、副标题)
2. 根据产品类型自动选择风格
3. 调用 auto_cover_engine.py 生成封面
4. 输出到产品项目文件夹和收件箱

使用方法:
python auto_cover_generator.py --product "宫崎骏作品集"
python auto_cover_generator.py --product "版式之道" --style "academic-grid"
"""

import sys
import os
import io
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════════════════════
# 配置区
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
PROJECTS_DIR = BASE_DIR / "01_Projects_制作中"
COVER_ENGINE_PATH = Path(__file__).parent / "auto_cover_engine.py"

# 产品风格映射（更新为 Wiki 规范风格）
PRODUCT_STYLE_MAPPING = {
    "宫崎骏作品集": "organic-botanical",   # 测试银杏叶背景
    "版式之道": "grid-system",             # Wiki 方案2：网格系统
    "飞鸟集": "whitespace-aesthetic",      # Wiki 方案1：留白美学
    "默认": "contrast-impact"              # 默认使用 Wiki 推荐方案
}

# ═══════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════

def find_latest_script(product_name):
    """查找产品最新的文案 MD 文件"""
    script_dir = PROJECTS_DIR / product_name / "02_脚本_逻辑链"

    if not script_dir.exists():
        print(f"错误：未找到脚本目录 {script_dir}")
        return None

    # 查找所有 MD 文件
    md_files = list(script_dir.glob("*-三套文案.md"))

    if not md_files:
        print(f"错误：未找到文案文件 {script_dir}/*-三套文案.md")
        return None

    # 按修改时间排序,返回最新的
    latest_file = max(md_files, key=lambda f: f.stat().st_mtime)
    print(f"✓ 找到最新文案: {latest_file.name}")
    return latest_file

def extract_metadata(md_file):
    """从文案 MD 文件中提取元数据"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取视频标题
    title_match = re.search(r'\*\*视频标题\*\*[：:]\s*(.+)', content)
    video_title = title_match.group(1).strip() if title_match else None

    # 提取商品短标题
    short_title_match = re.search(r'\*\*商品短标题\*\*[：:]\s*(.+)', content)
    short_title = short_title_match.group(1).strip() if short_title_match else None

    # 提取产品简介
    intro_match = re.search(r'\*\*产品简介\*\*[：:]\s*(.+)', content)
    intro = intro_match.group(1).strip() if intro_match else None

    return {
        "video_title": video_title,
        "short_title": short_title,
        "intro": intro
    }

def generate_cover_title(product_name, metadata):
    """生成封面标题(支持换行)"""
    # 优先使用商品短标题,如果太长则拆分
    title = metadata.get("short_title") or product_name

    # 如果标题超过10个字符,尝试智能拆分
    if len(title) > 10:
        # 查找合适的拆分点(·、-、空格等)
        for sep in ["·", "-", " ", "、"]:
            if sep in title:
                parts = title.split(sep, 1)
                return f"{parts[0]}\n{parts[1]}"

        # 如果没有分隔符,按长度拆分
        mid = len(title) // 2
        return f"{title[:mid]}\n{title[mid:]}"

    return title

def generate_cover_concept(metadata):
    """生成封面副标题(核心概念)"""
    # 优先使用产品简介的前半部分
    intro = metadata.get("intro", "")
    if intro:
        # 提取第一句话或前20个字符
        first_sentence = intro.split('。')[0].split('，')[0]
        if len(first_sentence) <= 20:
            return first_sentence
        return first_sentence[:20]

    # 备选:从视频标题中提取核心概念
    video_title = metadata.get("video_title", "")
    if video_title:
        # 移除数字、标点,提取核心词
        concept = re.sub(r'[0-9]+岁|[0-9]+次|[0-9]+年|[0-9]+部', '', video_title)
        concept = re.sub(r'[，。！？、：；""''《》【】（）]', ' ', concept)
        # 取前15个字符作为副标题
        concept = concept.strip()[:15]
        if concept:
            return concept

    return "经典收藏"

def get_product_style(product_name):
    """根据产品名称获取推荐风格"""
    return PRODUCT_STYLE_MAPPING.get(product_name, PRODUCT_STYLE_MAPPING["默认"])

def call_cover_engine(title, concept, style, output_path, description=None, platform="poster"):
    """调用 auto_cover_engine.py 生成封面"""
    cmd = [
        "py",
        str(COVER_ENGINE_PATH),
        "--title", title,
        "--concept", concept,
        "--style", style,
        "--output", str(output_path),
        "--platform", platform
    ]

    # 添加底部说明文案参数
    if description:
        cmd.extend(["--description", description])

    print(f"\n调用封面生成引擎...")
    print(f"  平台: {platform}")
    print(f"  标题: {title}")
    print(f"  概念: {concept}")
    print(f"  风格: {style}")
    if description:
        print(f"  说明: {description}")
    print(f"  输出: {output_path}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"封面生成失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

# ═══════════════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════════════

def main(product_name, style=None, custom_title=None, custom_concept=None):
    """主流程"""
    print("=" * 70)
    print(f"自动封面生成器 - {product_name}")
    print("=" * 70)

    # 1. 查找最新文案文件
    print("\n[1/4] 查找最新文案文件...")
    md_file = find_latest_script(product_name)
    if not md_file:
        return

    # 2. 提取元数据
    print("\n[2/4] 提取元数据...")
    metadata = extract_metadata(md_file)
    print(f"  ✓ 视频标题: {metadata.get('video_title', '未找到')}")
    print(f"  ✓ 商品短标题: {metadata.get('short_title', '未找到')}")

    # 3. 生成封面参数
    print("\n[3/4] 生成封面参数...")

    # 标题和概念(支持自定义)
    title = custom_title or generate_cover_title(product_name, metadata)
    concept = custom_concept or generate_cover_concept(metadata)

    # 底部说明文案（使用产品简介）
    description = metadata.get('intro', None)

    # 风格(支持自定义)
    if not style:
        style = get_product_style(product_name)

    print(f"  ✓ 封面标题: {title.replace(chr(10), ' / ')}")
    print(f"  ✓ 封面概念: {concept}")
    if description:
        print(f"  ✓ 底部说明: {description}")
    print(f"  ✓ 视觉风格: {style}")

    # 4. 生成封面（批量输出 poster 和 douyin 两个版本）
    print("\n[4/4] 生成封面...")

    # 输出路径
    today = datetime.now().strftime('%m%d')
    output_dir = PROJECTS_DIR / product_name / "01_素材_试用装" / "00_封面设计"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成两个版本
    platforms = [
        ("poster", f"{today}-{product_name}-封面-海报版.png"),
        ("douyin", f"{today}-{product_name}-封面-抖音版.png")
    ]

    all_success = True
    for platform, filename in platforms:
        output_path = output_dir / filename
        print(f"\n  生成 {platform} 版本...")

        # 抖音模式：极限信息降噪
        if platform == "douyin":
            # 强制删除 H3 概念文案
            douyin_concept = ""
            # 强制截断副标题：提取换行符后的内容并截断
            if '\n' in title:
                main_title, subtitle = title.split('\n', 1)
                # 截断副标题："吉卜力官方授权简体中文版" -> "吉卜力官方授权"
                if '简体中文版' in subtitle:
                    subtitle = subtitle.replace('简体中文版', '').replace('·', '').strip()
                douyin_title = f"{main_title}\n{subtitle}"
            else:
                douyin_title = title

            success = call_cover_engine(douyin_title, douyin_concept, style, output_path, description=None, platform=platform)
        else:
            # 海报模式：保持完整信息
            success = call_cover_engine(title, concept, style, output_path, description=description, platform=platform)

        if not success:
            all_success = False

    if all_success:
        print("\n" + "=" * 70)
        print("✓ 所有版本生成完成！")
        print("=" * 70)
        for platform, filename in platforms:
            path = output_dir / filename
            if path.exists():
                print(f"\n  ✓ {platform:6s} 版本: {path}")
                print(f"    文件大小: {path.stat().st_size / 1024:.1f} KB")
        print(f"\n下一步：")
        print("1. 检查封面质量")
        print("2. 如需调整,可使用以下参数重新生成:")
        print(f"   --style {style}")
        title_escaped = title.replace('\n', '\\n')
        print(f"   --title \"{title_escaped}\"")
        print(f"   --concept \"{concept}\"")
        print(f"   --platform poster  # 或 douyin")
        print("\n" + "=" * 70)
    else:
        print("\n❌ 封面生成失败")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="自动封面生成器")
    parser.add_argument("--product", type=str, required=True, help="产品名称(如: 宫崎骏作品集)")
    parser.add_argument("--style", type=str, choices=["classic-print", "organic-botanical", "academic-grid"],
                       help="视觉风格(可选,默认根据产品自动选择)")
    parser.add_argument("--title", type=str, help="自定义封面标题(可选)")
    parser.add_argument("--concept", type=str, help="自定义封面概念(可选)")

    args = parser.parse_args()

    main(args.product, style=args.style, custom_title=args.title, custom_concept=args.concept)
