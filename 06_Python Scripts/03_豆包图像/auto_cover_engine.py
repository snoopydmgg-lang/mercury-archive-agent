#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全自动封面生成流水线 - 新古典人文主义视觉系统
===============================================
基于"个人视觉系统设计"规范

设计原则:
- 新古典人文主义 (Neo-Classical Humanism)
- 高信噪比，降噪留白
- 色彩系统: 羊皮纸白 + 暖炭灰 + 赤陶土 + 灰桃色
- 质感: 2-5%单色噪点 + 纸张纹理
- 字体: 衬线体(标题) + 无衬线体(副标题)

用法:
    python auto_cover_engine.py --title "时间管理" --concept "战胜拖延症"
    python auto_cover_engine.py --title "版式之道" --concept "控制视觉熵的物理工程"
"""

import os
import sys
import uuid
import argparse
import random
import requests
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ============================================================
# 豆包 API 配置
# ============================================================
API_KEY = "3140fe69-b4ea-42fa-9d6b-e8257c3f2ff7"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID = "doubao-seedream-5-0-260128"

# ============================================================
# 配置文件加载
# ============================================================
def load_config():
    """从 cover_config.json 加载配置"""
    config_path = Path(__file__).parent / "cover_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载配置
CONFIG = load_config()

# ============================================================
# 画布与布局参数 (从配置文件读取)
# ============================================================
CANVAS_W = CONFIG["canvas"]["width"]
CANVAS_H = CONFIG["canvas"]["height"]

# 图片区域
IMAGE_END = CONFIG["layout"]["image_end"]

# 文字区域
TEXT_BG_START = CONFIG["layout"]["text_bg_start"]
TEXT_AREA_TOP = CONFIG["layout"]["text_area_top"]
MARGIN_LEFT = CONFIG["layout"]["margin_left"]
MARGIN_RIGHT = CONFIG["layout"]["margin_right"]
TITLE_Y = CONFIG["layout"]["title_y"]
SUBTITLE_Y = CONFIG["layout"]["subtitle_y"]

# 文本渲染边距
MARGIN = CONFIG["text_rendering"]["margin"]
MAX_WIDTH = CONFIG["text_rendering"]["max_width"]

# ============================================================
# 新古典人文主义色彩系统 (从配置文件读取)
# ============================================================
BG_COLOR = tuple(CONFIG["colors"]["background"])
INK_COLOR = tuple(CONFIG["colors"]["ink"])
ACCENT_COLOR = tuple(CONFIG["colors"]["accent"])
PEACH_COLOR = tuple(CONFIG["colors"]["peach"])
META_COLOR = tuple(CONFIG["colors"]["meta"])
LIGHT_GRAY = tuple(CONFIG["colors"]["light_gray"])
WHITE = tuple(CONFIG["colors"]["white"])

# 兼容旧版
GRAY_COLOR = (153, 153, 153)  # #999999 灰色（仅用于旧版风格）

# ============================================================
# Prompt 模板 - 新古典人文主义 (锁定模板，只替换概念)
# ============================================================
def build_prompt(concept: str, custom_prompt: str = None) -> str:
    """
    锁定Prompt模板 - 新古典人文主义风格
    只允许替换[核心概念]部分
    custom_prompt: 可选，覆盖默认正向提示词
    """
    if custom_prompt:
        return custom_prompt

    return (
        "画面主体：根据'{concept}'转化的一个有机抽象形态，"
        "例如折叠的纸张/贝壳纹理/花瓣分形/叶脉结构。"
        "视觉约束：新古典人文主义风格，古典印刷术质感，"
        "大地色系（米色/桃色/赤陶色），有机生命体隐喻。"
        "构图约束：画面上半部分70%展示主体，"
        "画面下半部分30%保持纯色负空间留白，绝对干净。"
        "质感要求：细微纸张纹理，2%-5%噪点颗粒感。"
        "反向约束：禁止任何文字、字母、水印、"
        "3D立体效果、重阴影、霓虹光效、赛博朋克元素。"
    ).format(concept=concept)


# 系统级正向 Prompt 后缀 — 纯英文，零中文渗透
SYSTEM_PROMPT_SUFFIX = (
    ". Pure visual art, absolutely NO text, NO typography, NO letters, "
    "NO calligraphy, NO characters, NO numbers, NO symbols. "
    "Macro photography close-up of an organic abstract structure "
    "inspired by natural fractals, leaf veins, cellular structures, "
    "and elegant folded paper art. "
    "Neo-classical humanism aesthetic, classical printing texture, "
    "highly detailed, intricate textures, matte finish. "
    "The subject is perfectly isolated in the center "
    "of a solid #F5F4F0 background. "
    "Color palette: muted warm earth tones, terracotta, "
    "dusty peach, warm charcoal. "
    "Masterpiece, high quality."
)

# 强化版负向提示词 — text/typography/chinese 置于最前排
STRONG_NEGATIVE_PROMPT = (
    "text, typography, letters, words, numbers, "
    "chinese characters, calligraphy, hanzi, "
    "watermark, logo, signature, "
    "borders, frames, geometric shapes, flat circles, "
    "messy background, clutter, human, realistic photography, "
    "3d render gloss, neon lights, high saturation, "
    "pure black, pure white"
)


def build_clean_minimal_prompt(concept: str = "") -> str:
    """
    纯净背景正向提示词 - 强调主体细节密度 + 干净背景融合
    """
    base = (
        "Macro close-up of an organic abstract sculpture "
        "with highly detailed natural fractals, delicate cell structures, "
        "and elegant paper art textures. "
        "The intricate subject is centered on a perfectly clean solid #F5F4F0 background, "
        "edge-to-edge seamless blend with the warm cream canvas. "
        "Soft volumetric studio lighting reveals the subject's rich textures. "
        "Neo-classical humanism, museum-quality fine art. "
        "No background clutter, no decorative elements behind the subject."
    )
    if concept:
        base += f" The organic form subtly evokes the concept of: {concept}"
    return base


# ============================================================
# 产品关键词 → 视觉主题映射（定制底图 prompt）
# ============================================================
PRODUCT_VISUAL_MAP = {
    # 色彩/配色类
    "色": {
        "visual": "color swatches arranged in a grid, traditional Chinese color palette, "
                  "muted earth tones, ink wash textures, antique paper background",
        "elements": "color chips, pigment samples, ink bottles, calligraphy brushes",
    },
    "配色": {
        "visual": "color harmony wheel, complementary color pairs, "
                  "traditional Chinese five-element color theory",
        "elements": "color cards, fabric swatches, ceramic glazes",
    },
    # 构图/摄影类
    "构图": {
        "visual": "golden ratio spiral overlay on landscape, rule of thirds grid, "
                  "diagonal composition lines, photographic framing guides",
        "elements": "camera viewfinder, lens aperture, composition grid lines",
    },
    "摄影": {
        "visual": "camera lens elements, aperture blades, depth of field gradient, "
                  "light and shadow interplay on textured surface",
        "elements": "camera body, film strips, light meters",
    },
    # 版式/排版类
    "版式": {
        "visual": "Swiss typographic grid, modular scale, baseline grid system, "
                  "column layout with generous margins, neo-classical book design",
        "elements": "grid lines, type specimens, spacing ratios",
    },
    "排版": {
        "visual": "typographic hierarchy demonstration, font pairing samples, "
                  "leading and kerning visualization",
        "elements": "letterforms, text blocks, paragraph spacing",
    },
    # 留白/极简类
    "留白": {
        "visual": "vast empty space with single minimal element, "
                  "Japanese ma (間) concept, breathing room, negative space",
        "elements": "single ink stroke, empty frame, void with texture",
    },
    "极简": {
        "visual": "absolute minimal composition, one element maximum, "
                  "monochrome with texture, quiet contemplation",
        "elements": "single geometric form, raw material texture",
    },
    # 文学/诗歌类
    "诗": {
        "visual": "delicate ink wash landscape, misty mountains, flowing water, "
                  "traditional Chinese painting aesthetics",
        "elements": "brush strokes, ink splatter, rice paper texture",
    },
    "集": {
        "visual": "curated collection layout, specimen-style arrangement, "
                  "archival presentation, numbered items in grid",
        "elements": "catalog numbers, specimen labels, archival paper",
    },
    # 历史/文化类
    "古": {
        "visual": "antique document fragments, aged paper with patina, "
                  "seal impressions, classical Chinese binding",
        "elements": "red seal stamps, bamboo slips, silk texture",
    },
    "传统": {
        "visual": "traditional Chinese craft materials, "
                  "lacquerware textures, bronze patina, jade surfaces",
        "elements": "ceramic patterns, textile weave, wood grain",
    },
    # 自然/植物类
    "花": {
        "visual": "botanical illustration, pressed flowers, "
                  "delicate petal textures, natural color palette",
        "elements": "flower specimens, leaves, stems, pollen",
    },
    "叶": {
        "visual": "leaf vein close-up, autumn foliage gradient, "
                  "botanical precision, organic fractal patterns",
        "elements": "leaf skeleton, branch structure, natural symmetry",
    },
    # 情感/哲学类
    "等": {
        "visual": "contemplative empty space, single waiting figure silhouette, "
                  "time passing, hourglass metaphor",
        "elements": "empty chair, window light, shadow play",
    },
    "爱": {
        "visual": "warm intimate composition, soft focus elements, "
                  "gentle color temperature, emotional resonance",
        "elements": " intertwined forms, embracing shapes, warmth gradients",
    },
    # 数字/数据类
    "数据": {
        "visual": "data visualization abstract, minimalist chart elements, "
                  "geometric precision, information architecture",
        "elements": "bar charts, scatter plots, network diagrams",
    },
    "思维": {
        "visual": "mind map structure, neural network abstraction, "
                  "connected nodes, logical flow diagrams",
        "elements": "circles, connecting lines, hierarchy tree",
    },
}


def build_product_visual_prompt(title: str, concept: str, base_style_prompt: str) -> str:
    """
    根据产品名和概念中的关键词，生成定制化底图 prompt

    策略：从 PRODUCT_VISUAL_MAP 中匹配关键词，将匹配到的视觉主题
    注入到基础 prompt 中，替代泛泛的新古典人文主义描述
    """
    combined_text = title + " " + concept
    matched_visuals = []
    matched_elements = []

    for keyword, visual_info in PRODUCT_VISUAL_MAP.items():
        if keyword in combined_text:
            matched_visuals.append(visual_info["visual"])
            matched_elements.append(visual_info["elements"])

    if not matched_visuals:
        # 没有匹配到关键词，返回基础 prompt
        return base_style_prompt

    # 组合匹配到的视觉主题
    visual_str = "; ".join(matched_visuals[:2])  # 最多取2个主题避免冲突
    elements_str = "; ".join(matched_elements[:2])

    # 注入到 prompt 中 — 纯英文，零中文字符
    product_prompt = (
        f"Visual subject: {visual_str}. "
        f"Accents: {elements_str}. "
        f"Neo-classical humanism, classical printing texture, "
        f"muted earth tones (cream, peach, terracotta). "
        f"Composition: subject occupies upper 70%, "
        f"lower 30% is pure solid #F5F4F0 negative space. "
    )
    return product_prompt


# ============================================================
# 三种风格预设 Prompt + 文字色彩方案（从配置文件读取颜色）
# ============================================================
STYLE_PROMPTS = {
    # ---- 风格1: 留白美学 (whitespace-aesthetic) - Wiki 方案1 ----
    "whitespace-aesthetic": {
        "positive": (
            "Pure cream white warm paper background #F5F4F0, neo-classical humanism, "
            "Japanese minimalist book cover design, elegant and simple. "
            "Prominent paper texture with visible grain. "
            "High-end, sophisticated, professional. "
            "Inspired by Japanese book cover design."
        ),
        "negative": (
            "decorations, images, photos, illustrations, graphics, patterns, "
            "geometric shapes, circles, lines, frames, grids, borders, "
            "3D rendering, gradients, shadows, neon lights, cyberpunk, "
            "text, letters, watermark, human face, body, messy, chaotic"
        ),
        "title_color": tuple(CONFIG["styles"]["whitespace-aesthetic"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["whitespace-aesthetic"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["whitespace-aesthetic"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["whitespace-aesthetic"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["whitespace-aesthetic"]["hook_color"]),
    },

    # ---- 风格2: 网格系统 (grid-system) - Wiki 方案2 ----
    "grid-system": {
        "positive": (
            "Pure cream white warm paper background #F5F4F0, neo-classical humanism, "
            "minimalist grid system design, visible gray grid lines, "
            "8x12 grid layout, clean and organized. "
            "Prominent paper texture with visible grain. "
            "Academic, professional, systematic. "
            "Inspired by Swiss design and Japanese minimalism."
        ),
        "negative": (
            "decorations, images, photos, illustrations, complex graphics, "
            "3D rendering, gradients, shadows, neon lights, cyberpunk, "
            "text, letters, watermark, human face, body, messy, chaotic"
        ),
        "title_color": tuple(CONFIG["styles"]["grid-system"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["grid-system"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["grid-system"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["grid-system"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["grid-system"]["hook_color"]),
    },

    # ---- 风格3: 对比冲击 (contrast-impact) - Wiki 方案3（推荐）----
    "contrast-impact": {
        "positive": (
            "Pure cream white warm paper background #F5F4F0, neo-classical humanism, "
            "ultra-minimalist design, maximum visual impact through contrast. "
            "Prominent paper texture with warm grain. "
            "Bold, striking, high-end. "
            "Inspired by Japanese minimalist book covers."
        ),
        "negative": (
            "decorations, images, photos, illustrations, graphics, patterns, "
            "geometric shapes, circles, round shapes, lines, frames, grids, borders, "
            "3D rendering, gradients, shadows, neon lights, cyberpunk, "
            "text, letters, watermark, human face, body, messy, chaotic"
        ),
        "title_color": tuple(CONFIG["styles"]["contrast-impact"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["contrast-impact"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["contrast-impact"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["contrast-impact"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["contrast-impact"]["hook_color"]),
    },

    # ---- 兼容旧版：古典印刷 (classic-print) ----
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
        "title_color": tuple(CONFIG["styles"]["classic-print"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["classic-print"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["classic-print"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["classic-print"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["classic-print"]["hook_color"]),
    },

    # ---- 兼容旧版：有机生命体 (organic-botanical) ----
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
        "title_color": tuple(CONFIG["styles"]["organic-botanical"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["organic-botanical"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["organic-botanical"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["organic-botanical"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["organic-botanical"]["hook_color"]),
    },

    # ---- 兼容旧版：学术网格 (academic-grid) ----
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
        "title_color": tuple(CONFIG["styles"]["academic-grid"]["title_color"]),
        "subtitle_color": tuple(CONFIG["styles"]["academic-grid"]["subtitle_color"]),
        "accent_color": tuple(CONFIG["styles"]["academic-grid"]["accent_color"]),
        "meta_color": tuple(CONFIG["styles"]["academic-grid"]["meta_color"]),
        "hook_color": tuple(CONFIG["styles"]["academic-grid"]["hook_color"]),
    },
}

DEFAULT_STYLE = CONFIG["default_style"]


def build_style_prompt(style: str, concept: str = "") -> str:
    """根据风格返回对应的正向提示词"""
    style = style.lower()
    if style in STYLE_PROMPTS:
        prompt = STYLE_PROMPTS[style]["positive"]
    else:
        prompt = STYLE_PROMPTS[DEFAULT_STYLE]["positive"]
    if concept:
        prompt += f" Theme hint: {concept}"
    return prompt


def get_style_negative(style: str) -> str:
    """根据风格返回对应的负向提示词"""
    style = style.lower()
    if style in STYLE_PROMPTS:
        return STYLE_PROMPTS[style]["negative"]
    return STYLE_PROMPTS[DEFAULT_STYLE]["negative"]


def get_style_colors(style: str) -> dict:
    """根据风格返回对应的文字色彩方案"""
    style = style.lower()
    if style in STYLE_PROMPTS:
        return STYLE_PROMPTS[style]
    return STYLE_PROMPTS[DEFAULT_STYLE]

# ============================================================
# 字体加载 - 衬线体(标题) + 无衬线体(副标题)
# ============================================================
def get_artistic_font(size: int):
    """获取艺术字体（行楷/书法体）- 用于情感类标题"""
    artistic_fonts = [
        "C:/Windows/Fonts/STXINGKA.TTF",   # 华文行楷
        "C:/Windows/Fonts/FZSTK.TTF",      # 方正舒体
        "C:/Windows/Fonts/STXINWEI.TTF",   # 华文新魏
        "C:/Windows/Fonts/SIMLI.TTF",      # 隶书
        "C:/Windows/Fonts/simkai.ttf",     # 楷体
    ]
    for path in artistic_fonts:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                print(f"[FONT] 艺术字体加载: {os.path.basename(path)}")
                return font
            except Exception:
                pass
    print("[WARN] 未找到艺术字体，回退到衬线体")
    return get_serif_font(size)


def get_serif_font(size: int, bold: bool = False):
    """获取衬线字体（标题用）- 优先使用支持中文的衬线体"""
    serif_fonts = [
        # 思源宋体（中文衬线，首选）
        "C:/Windows/Fonts/NotoSerifSC-VF.ttf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSerifSC-VF.ttf",
        # 思源宋体备选
        "C:/Windows/Fonts/NotoSerifSC-Regular.otf",
        "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSerifSC-Regular.otf",
        # 宋体（系统中文衬线）
        "C:/Windows/Fonts/simsun.ttc",
        # 楷体（中文衬线）
        "C:/Windows/Fonts/simkai.ttf",
        "C:/Windows/Fonts/STKAITI.TTF",
        # 英文衬线（不支持中文，仅作保底）
        "C:/Windows/Fonts/Georgia.ttf",
        "C:/Windows/Fonts/TIMES.TTF",
    ]
    for path in serif_fonts:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                print(f"[FONT] 衬线字体加载: {os.path.basename(path)}")
                return font
            except Exception:
                pass
    print("[WARN] 未找到衬线字体，使用默认字体")
    return ImageFont.load_default()


def get_sans_font(size: int, bold: bool = False):
    """获取无衬线字体（副标题/元数据用）- 优先使用支持中文的无衬线体"""
    if bold:
        sans_fonts = [
            # 思源黑体（中文无衬线，加粗）
            "C:/Windows/Fonts/NotoSansSC-VF.ttf",
            "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf",
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/NotoSansSC-Bold.otf",
            "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-Bold.otf",
        ]
    else:
        sans_fonts = [
            # 思源黑体（中文无衬线）
            "C:/Windows/Fonts/NotoSansSC-VF.ttf",
            "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-VF.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/NotoSansSC-Regular.otf",
            "C:/Users/Administrator/AppData/Local/Microsoft/Windows/Fonts/NotoSansSC-Regular.otf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
    for path in sans_fonts:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size)
                print(f"[FONT] 无衬线字体加载: {os.path.basename(path)}")
                return font
            except Exception:
                pass
    print("[WARN] 未找到无衬线字体，使用默认字体")
    return ImageFont.load_default()


def get_text_bbox(text: str, font) -> tuple:
    """获取文本 bounding box (left, top, right, bottom)"""
    try:
        return font.getbbox(text)
    except Exception:
        return (0, 0, len(text) * font.size // 2, font.size)


def get_text_width(text: str, font) -> int:
    """获取文本宽度"""
    bbox = get_text_bbox(text, font)
    return bbox[2] - bbox[0]


def get_text_height(text: str, font) -> int:
    """获取文本高度"""
    bbox = get_text_bbox(text, font)
    return bbox[3] - bbox[1]


def clean_text(text: str) -> str:
    """
    清洗文本：移除异常空格和全角空格
    """
    # 移除半角空格和全角空格
    text = text.replace(" ", "").replace("　", "")
    return text.strip()


def parse_text_segments(text: str) -> list:
    """
    将文本拆分为 (is_number, content) 段落列表

    例: "384种颜色" → [(True, "384"), (False, "种颜色")]
    例: "光圈差1档" → [(False, "光圈差"), (True, "1"), (False, "档")]
    """
    import re
    segments = []
    for match in re.finditer(r'(\d+[\d.,%]*|\d+)', text):
        # 数字前的普通文字
        if match.start() > 0:
            segments.append((False, text[match.start():match.start()]))
        segments.append((True, match.group()))
        # 数字后的普通文字（由下次循环处理）
    if not segments:
        return [(False, text)]

    result = []
    pos = 0
    for match in re.finditer(r'(\d+[\d.,%]*|\d+)', text):
        if match.start() > pos:
            result.append((False, text[pos:match.start()]))
        result.append((True, match.group()))
        pos = match.end()
    if pos < len(text):
        result.append((False, text[pos:]))

    return result


def render_text_with_number_highlight(
    draw: ImageDraw, text: str, x: int, y: int,
    font_normal, font_number: int,
    color_normal: tuple, color_number: tuple,
    char_spacing: int = 0
) -> int:
    """
    渲染文本行，自动检测数字并用大号+点缀色高亮

    Args:
        draw: ImageDraw 对象
        text: 要渲染的文本
        x, y: 起始坐标
        font_normal: 普通文字字体
        font_number: 数字字体（字号更大）
        color_normal: 普通文字颜色
        color_number: 数字颜色（点缀色）
        char_spacing: 字间距

    Returns:
        渲染后的底部 Y 坐标
    """
    segments = parse_text_segments(text)
    current_x = x
    max_height = 0

    for is_number, content in segments:
        if is_number:
            font = font_number
            color = color_number
        else:
            font = font_normal
            color = color_normal

        for ch in content:
            draw.text((current_x, y), ch, font=font, fill=color)
            bbox = get_text_bbox(ch, font)
            char_w = bbox[2] - bbox[0]
            char_h = bbox[3] - bbox[1]
            current_x += char_w + char_spacing
            max_height = max(max_height, char_h)

    return y + max_height


def wrap_text_by_width(text: str, font, max_width: int) -> list:
    """
    按像素宽度自动换行（逐字累加算法）

    Args:
        text: 要换行的文本
        font: 字体对象
        max_width: 最大宽度（像素）

    Returns:
        换行后的文本行列表
    """
    lines = []
    current_line = ""

    for char in text:
        # 尝试添加当前字符
        test_line = current_line + char
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            # 未超宽，继续累加
            current_line = test_line
        else:
            # 超宽，当前行结束，开始新行
            if current_line:
                lines.append(current_line)
            current_line = char

    # 添加最后一行
    if current_line:
        lines.append(current_line)

    return lines


def auto_scale_and_wrap(text: str, font_getter, base_size: int, max_width: int, draw) -> tuple:
    """
    动态缩放字体并自动换行

    Args:
        text: 要渲染的文本
        font_getter: 字体获取函数 (如 get_serif_font)
        base_size: 基准字号
        max_width: 最大宽度
        draw: ImageDraw 对象

    Returns:
        (font, lines) - 最终字体对象和拆分后的行列表
    """
    # 清洗文本
    text = clean_text(text)

    # 如果有显式换行符，按换行符拆分
    if '\n' in text:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # 检查每行是否超宽
        font = font_getter(base_size)
        max_line_width = max(get_text_width(line, font) for line in lines)

        # 如果超宽，缩小字号
        if max_line_width > max_width:
            scale_factor = max_width / max_line_width
            new_size = int(base_size * scale_factor * 0.95)  # 留5%安全边距
            font = font_getter(new_size)

        return font, lines

    # 单行文本：先尝试基准字号
    font = font_getter(base_size)
    text_width = get_text_width(text, font)

    # 如果单行超宽，尝试缩小字号
    if text_width > max_width:
        scale_factor = max_width / text_width
        new_size = int(base_size * scale_factor * 0.95)  # 留5%安全边距
        font = font_getter(new_size)
        text_width = get_text_width(text, font)

        # 如果缩小后仍然超宽，强制换行
        if text_width > max_width:
            # 按字符数平均拆分（中文友好）
            mid = len(text) // 2
            lines = [text[:mid], text[mid:]]

            # 再次检查是否超宽
            max_line_width = max(get_text_width(line, font) for line in lines)
            if max_line_width > max_width:
                scale_factor = max_width / max_line_width
                new_size = int(new_size * scale_factor * 0.95)
                font = font_getter(new_size)

            return font, lines

    return font, [text]


def split_title_lines(title: str) -> list:
    """
    智能拆分标题行：
    - 优先保持单行（如果宽度够）
    - 显式 \n 强制换行优先
    - 禁止自动字符级拆行破坏中文词义
    """
    title = title.strip()
    if '\n' in title:
        # 显式换行符优先
        return [line.strip() for line in title.split('\n') if line.strip()]
    # 保持单行（自动换行由调用方控制）
    return [title]


def render_text(draw: ImageDraw, text: str, x: int, y: int, font,
                fill: tuple, align: str = 'left') -> int:
    """
    渲染单行文字，返回该行实际渲染底部 Y 坐标
    align: 'left' | 'center' | 'right'
    """
    bbox = get_text_bbox(text, font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    if align == 'center':
        x = x - text_w // 2
    elif align == 'right':
        x = x - text_w

    draw.text((x, y), text, font=font, fill=fill)
    return y + text_h


# ============================================================
# Step 1: 调用豆包API生成纯背景图
# ============================================================
def generate_background(concept: str, size: str = "2048x2048",
                       custom_prompt: str = None, use_strong_negative: bool = True,
                       style: str = DEFAULT_STYLE, title: str = "") -> str:
    """
    调用豆包文生图API，生成新古典人文主义风格底图
    返回: 下载后的本地文件路径

    Args:
        concept: 核心概念（用于默认prompt占位）
        size: 输出尺寸
        custom_prompt: 可选，覆盖默认正向提示词
        use_strong_negative: 是否使用强化版负向提示词（默认True）
        style: 底图风格 (wabi-sabi / cyber / bauhaus)
        title: 产品标题（用于关键词匹配生成定制prompt）
    """
    if custom_prompt:
        prompt = custom_prompt
        negative = STRONG_NEGATIVE_PROMPT
    elif style and style != "clean":
        base_prompt = build_style_prompt(style, concept)
        # 根据产品标题+概念关键词定制底图 prompt
        prompt = build_product_visual_prompt(title or concept, concept, base_prompt)
        negative = get_style_negative(style)
    else:
        prompt = build_clean_minimal_prompt(concept)
        negative = STRONG_NEGATIVE_PROMPT

    # 强制拼接系统级正向约束 (纯英文, 零中文渗透)
    prompt = prompt.rstrip() + SYSTEM_PROMPT_SUFFIX

    print(f"[Step 1] 调用豆包API生成底图 [style={style}]...")
    print(f"[Step 1] Prompt: {prompt[:120]}...")

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_ID,
        "prompt": prompt,
        "negative_prompt": negative,
        "size": size,
        "quality": "hd"
    }

    response = requests.post(url, headers=headers, json=data, timeout=180)
    if response.status_code != 200:
        raise Exception(f"豆包API错误: {response.status_code} - {response.text}")

    result = response.json()
    if "data" not in result or len(result["data"]) == 0:
        raise Exception(f"API返回格式异常: {result}")

    image_url = result["data"][0]["url"]
    print(f"[Step 1] 获得图片URL: {image_url[:50]}...")

    # 下载到底图目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:8]}_bg.png"
    output_path = os.path.join(assets_dir, filename)

    img_response = requests.get(image_url, timeout=60)
    with open(output_path, "wb") as f:
        f.write(img_response.content)

    print(f"[Step 1] 底图已保存: {filename}")
    return output_path


# ============================================================
# Step 2: PIL渲染封面 - 新古典人文主义视觉系统
# ============================================================
def add_noise_texture(img: Image.Image, intensity: float = 0.03) -> Image.Image:
    """
    添加2-5%单色噪点，模拟纸张纹理
    """
    # 创建噪点层
    noise = Image.new("L", img.size, 0)
    pixels = noise.load()
    width, height = img.size

    # 随机生成噪点
    for y in range(height):
        for x in range(width):
            if random.random() < intensity:
                pixels[x, y] = random.randint(0, 255)

    # 模糊噪点使其更自然
    noise = noise.filter(ImageFilter.GaussianBlur(radius=0.5))

    # 转换为RGB并叠加
    noise_rgb = Image.merge("RGB", [noise, noise, noise])

    # 使用叠加模式混合
    img = img.convert("RGB")
    enhancer = ImageEnhance.Brightness(img)
    darkened = enhancer.enhance(0.97)  # 稍微压暗以便噪点可见

    # 叠加噪点
    result = Image.blend(darkened, noise_rgb, intensity * 0.5)
    return result


def draw_organic_fractal(draw: ImageDraw, canvas_w: int, canvas_h: int):
    """
    在右侧绘制有机分形装饰图形
    呼应 Claude 3 图标的有机分形结构
    """
    # 有机分形装饰区域 (右侧，避开文字)
    center_x = int(canvas_w * 0.78)
    center_y = int(canvas_h * 0.25)  # 向上移动，避免与大标题重叠
    size = 120

    # 外层 - 灰桃色大圆形
    draw.ellipse(
        [center_x - size, center_y - size, center_x + size, center_y + size],
        fill=PEACH_COLOR
    )

    # 中层 - 赤陶色小圆形
    inner_size = int(size * 0.6)
    draw.ellipse(
        [center_x - inner_size, center_y - inner_size,
         center_x + inner_size, center_y + inner_size],
        fill=ACCENT_COLOR
    )

    # 内层 - 白色圆点
    dot_size = int(size * 0.15)
    draw.ellipse(
        [center_x - dot_size, center_y - dot_size,
         center_x + dot_size, center_y + dot_size],
        fill=WHITE
    )

    # 辅助细线装饰
    draw.line(
        [center_x - size * 1.5, center_y, center_x + size * 1.5, center_y],
        fill=PEACH_COLOR, width=1
    )


def render_cover(background_path: str, title: str, concept: str, output_path: str,
                 volume: str = "VOL.01", date: str = None,
                 title_align: str = 'center', subtitle_align: str = 'center',
                 margin_left: int = MARGIN_LEFT,
                 title_line_spacing: int = 30,
                 subtitle_margin_top: int = 85,
                 style: str = DEFAULT_STYLE,
                 hook_text: str = None,
                 description: str = None,
                 platform: str = "poster",
                 account: str = None):
    """
    使用PIL将文字渲染到背景图上
    支持多端复用：poster（海报长文案版）/ douyin（抖音极简大字版）

    平台模式:
    - poster: 完整版，包含主标题、副标题、底部说明文案（120pt/60pt/32pt）
    - douyin: 极简版，仅主副标题，超大字号（180pt/80pt），居中布局，强化对比度

    排版精调:
    - margin_left: X轴统一锚点（默认80）
    - title_line_spacing: 主标题行间距（默认30px）
    - subtitle_margin_top: 主副标题间距（默认85px，呼吸感）
    - style: 风格 (contrast-impact / whitespace-aesthetic / grid-system)，自动适配文字色彩
    - hook_text: 顶部钩子文案（如"留白占了九成"），灰色小字
    - description: 底部说明文案（仅 poster 模式使用）
    - platform: 平台模式 (poster / douyin)
    """
    import datetime

    # ============================================================
    # 0. 账号风格覆盖（优先级高于 style 颜色配置）
    # ============================================================
    account_config = None
    if account and account in CONFIG.get("accounts", {}):
        account_config = CONFIG["accounts"][account]
        print(f"[Step 2] 使用账号风格: {account_config['name']}")
        # 用账号配置覆盖布局参数
        title_align = account_config.get("title_align", title_align)
        subtitle_align = account_config.get("subtitle_align", subtitle_align)
        title_line_spacing = account_config.get("title_line_spacing", title_line_spacing)
        subtitle_margin_top = account_config.get("subtitle_margin_top", subtitle_margin_top)

    # 获取风格对应的文字色彩
    colors = get_style_colors(style)
    title_color = colors["title_color"]
    subtitle_color = colors["subtitle_color"]
    accent_color = colors["accent_color"]
    meta_color = colors["meta_color"]
    hook_color = colors.get("hook_color", GRAY_COLOR)  # 钩子文案颜色

    # 账号颜色覆盖
    if account_config:
        title_color = tuple(account_config.get("title_color", title_color))
        subtitle_color = tuple(account_config.get("subtitle_color", subtitle_color))
        accent_color = tuple(account_config.get("accent_color", accent_color))
        hook_color = tuple(account_config.get("hook_color", hook_color))

    print(f"[Step 2] 开始渲染封面 [style={style}]...")
    print(f"[Step 2] 主标题: {title!r}")
    print(f"[Step 2] 副标题: {concept!r}")
    if hook_text:
        print(f"[Step 2] 钩子文案: {hook_text!r}")
    print(f"[Step 2] X边距: {margin_left} | 主标题行距: {title_line_spacing} | 副标题间距: {subtitle_margin_top}")
    print(f"[Step 2] 标题对齐: {title_align} | 副标题对齐: {subtitle_align}")
    print(f"[Step 2] 文字色彩: title={title_color} subtitle={subtitle_color} accent={accent_color}")

    if date is None:
        date = datetime.datetime.now().strftime("%Y.%m.%d")

    # ============================================================
    # 1. 加载底图 → 宽度铺满 + 渐变蒙版融合
    # ============================================================
    bg_raw = Image.open(background_path).convert("RGBA")
    orig_w, orig_h = bg_raw.size
    print(f"[Step 2] 底图尺寸: {orig_w}x{orig_h}")

    # 裁切右下角水印 (8%)
    crop_right = int(orig_w * 0.08)
    crop_bottom = int(orig_h * 0.08)
    bg_raw = bg_raw.crop((0, 0, orig_w - crop_right, orig_h - crop_bottom))

    # 宽度强制铺满画布
    cw = CANVAS_W
    ch = int(bg_raw.size[1] * (CANVAS_W / bg_raw.size[0]))
    bg_raw = bg_raw.resize((cw, ch), Image.LANCZOS).convert("RGB")

    # 物理裁剪 — 绝对安全边界 MAX_IMG_H = 750
    MAX_H = 750
    if ch > MAX_H:
        bg_raw = bg_raw.crop((0, 0, cw, MAX_H))

    # 贴入 BG_COLOR 画布顶部 (0, 0)
    bg = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    bg.paste(bg_raw, (0, 0))

    print(f"[Step 2] 图片: {cw}x{ch} → 物理裁剪至 {bg_raw.size[1]}px (max={MAX_H})")

    # ============================================================
    # 2. 创建背景层 — 简洁处理 (图像已在上方容器内，下方纯 BG_COLOR)
    # ============================================================
    if style in ["contrast-impact", "whitespace-aesthetic", "grid-system"]:
        # 仅对图像区域做轻微增强
        canvas = bg.copy()
        enhancer = ImageEnhance.Contrast(canvas)
        canvas = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Sharpness(canvas)
        canvas = enhancer.enhance(1.3)
        print(f"[Step 2] 图像区域轻度增强 (contrast=1.2, sharpness=1.3)")
    else:
        canvas = bg.copy()
        print(f"[Step 2] 使用纯色画布 + 上方容器图像")

    # ============================================================
    # 3. 绘制装饰与分割线（根据风格决定）
    # ============================================================
    draw = ImageDraw.Draw(canvas)

    # Wiki 规范风格：装饰线
    if style == "contrast-impact":
        # 方案3：对比冲击 - 顶部+底部赤陶色横线
        draw.line(
            [margin_left, int(CANVAS_H * 0.12), CANVAS_W - margin_left, int(CANVAS_H * 0.12)],
            fill=accent_color, width=2
        )
        draw.line(
            [margin_left, CANVAS_H - 60, CANVAS_W - margin_left, CANVAS_H - 60],
            fill=accent_color, width=2
        )
    elif style == "whitespace-aesthetic":
        # 方案1：留白美学 - 底部赤陶色分隔线
        draw.line(
            [margin_left, CANVAS_H - 60, CANVAS_W - margin_left, CANVAS_H - 60],
            fill=accent_color, width=2
        )
    elif style == "grid-system":
        # 方案2：网格系统 - 绘制可见网格线（2px）
        grid_color = LIGHT_GRAY
        grid_cols = 8
        grid_rows = 12
        col_width = CANVAS_W // grid_cols
        row_height = CANVAS_H // grid_rows

        # 绘制垂直网格线
        for i in range(1, grid_cols):
            x = i * col_width
            draw.line([x, 0, x, CANVAS_H], fill=grid_color, width=2)

        # 绘制水平网格线
        for i in range(1, grid_rows):
            y = i * row_height
            draw.line([0, y, CANVAS_W, y], fill=grid_color, width=2)
    else:
        # 旧版风格保留原有装饰
        if style == "classic-print":
            draw_organic_fractal(draw, CANVAS_W, CANVAS_H)

        # 顶部元数据区分隔线
        draw.line(
            [margin_left, TEXT_AREA_TOP - 30, CANVAS_W - margin_left, TEXT_AREA_TOP - 30],
            fill=accent_color, width=1
        )
        # 底部装饰线
        draw.line(
            [margin_left, CANVAS_H - 50, CANVAS_W - margin_left, CANVAS_H - 50],
            fill=title_color, width=1
        )

    # ============================================================
    # 4. 动态字体加载与文本处理（根据平台调整字号 - 从配置文件读取）
    # ============================================================
    print(f"[Step 2] 平台模式: {platform}")

    # 从配置文件读取平台字号
    PLATFORM_TITLE_SIZE = CONFIG["fonts"][platform]["title"]
    PLATFORM_SUBTITLE_SIZE = CONFIG["fonts"][platform]["subtitle"]
    PLATFORM_META_SIZE = CONFIG["fonts"][platform]["meta"]

    # 账号字号比例覆盖
    if account_config:
        PLATFORM_TITLE_SIZE = int(PLATFORM_TITLE_SIZE * account_config.get("title_size_ratio", 1.0))
        PLATFORM_SUBTITLE_SIZE = int(PLATFORM_SUBTITLE_SIZE * account_config.get("subtitle_size_ratio", 1.0))
        print(f"[Step 2] 账号字号覆盖: title={PLATFORM_TITLE_SIZE}pt, subtitle={PLATFORM_SUBTITLE_SIZE}pt")

    # 从配置文件读取平台间距
    PLATFORM_TITLE_LINE_SPACING = CONFIG["spacing"][platform]["title_line_spacing"]
    PLATFORM_SUBTITLE_MARGIN_TOP = CONFIG["spacing"][platform]["subtitle_margin_top"]
    PLATFORM_DESCRIPTION_MARGIN_TOP = CONFIG["spacing"][platform]["description_margin_top"]

    # 从配置文件读取平台特性
    PLATFORM_FONT_BOLD = CONFIG["platform_features"][platform]["font_bold"]
    PLATFORM_SHOW_CONCEPT = CONFIG["platform_features"][platform]["show_concept"]
    PLATFORM_SHOW_DESCRIPTION = CONFIG["platform_features"][platform]["show_description"]

    # 账号特性覆盖
    if account_config:
        PLATFORM_SHOW_DESCRIPTION = account_config.get("show_description", PLATFORM_SHOW_DESCRIPTION)

    print(f"[Step 2] {platform}模式：主标题 {PLATFORM_TITLE_SIZE}pt，副标题 {PLATFORM_SUBTITLE_SIZE}pt")

    # 计算可用文本宽度（左右边距 MARGIN=80）
    usable_width = CANVAS_W - MARGIN * 2  # 920px

    # 主标题：动态缩放 + 自动换行（设计规范：思源宋体）
    font_title, title_lines = auto_scale_and_wrap(
        title,
        lambda size: get_serif_font(size, bold=PLATFORM_FONT_BOLD),
        PLATFORM_TITLE_SIZE,
        usable_width,
        draw
    )

    # 副标题：动态缩放 + 自动换行（根据平台配置决定是否加粗）
    font_subtitle, subtitle_lines = auto_scale_and_wrap(
        concept,
        lambda size: get_sans_font(size, bold=PLATFORM_FONT_BOLD),
        PLATFORM_SUBTITLE_SIZE,
        usable_width,
        draw
    )

    # 品牌字体
    font_meta = get_sans_font(CONFIG["fonts"]["poster"]["brand"])  # 14pt 品牌/出版社

    print(f"[Step 2] 主标题字号: {PLATFORM_TITLE_SIZE}pt | 行数: {len(title_lines)}")
    print(f"[Step 2] 副标题字号: {PLATFORM_SUBTITLE_SIZE}pt | 行数: {len(subtitle_lines)}")

    # ============================================================
    # 5. 顶部引题 — 已移除 (与 AI 底图重叠，破坏视觉纯净度)
    # ============================================================

    # ============================================================
    # 6. 渲染主标题（根据平台调整布局和效果 - 从配置文件读取Y轴位置）
    # ============================================================

    # 从配置文件读取Y轴起始位置比例
    title_y_ratio = CONFIG["positioning"][platform]["title_start_y_ratio"]
    if account_config:
        title_y_ratio = account_config.get("title_start_y_ratio", title_y_ratio)
    TITLE_START_Y = int(CANVAS_H * title_y_ratio)
    print(f"[Step 2] {platform}模式：主标题起始Y = {TITLE_START_Y} ({title_y_ratio*100}%)")

    current_y = TITLE_START_Y
    title_bottom_y = current_y

    # 字间距收紧系数（负值=收紧，正值=放松）
    CHAR_SPACING = -15  # 收紧15px，让三字标题形成视觉整体

    # 数字高亮：检测标题中的数字，用大号+点缀色渲染
    NUMBER_HIGHLIGHT_SIZE = int(PLATFORM_TITLE_SIZE * 1.3)  # 数字放大30%
    font_title_number = get_serif_font(NUMBER_HIGHLIGHT_SIZE, bold=True)

    for line in title_lines:
        # 计算带数字高亮的总宽度
        segments = parse_text_segments(line)
        char_widths_all = []  # (char, font, is_number) 扁平列表
        for is_num, content in segments:
            fn = font_title_number if is_num else font_title
            for ch in content:
                ch_bbox = get_text_bbox(ch, fn)
                char_widths_all.append((ch, fn, is_num, ch_bbox[2] - ch_bbox[0]))
        total_w = sum(cw for _, _, _, cw in char_widths_all) + CHAR_SPACING * (len(char_widths_all) - 1)
        text_h = get_text_bbox(line, font_title)[3] - get_text_bbox(line, font_title)[1]

        x = MARGIN  # 硬编码左对齐，废除所有居中逻辑

        # 逐字绘制，数字用大号+点缀色
        for ch, fn, is_num, cw in char_widths_all:
            ch_color = accent_color if is_num else title_color
            draw.text((x, current_y), ch, font=fn, fill=ch_color)
            x += cw + CHAR_SPACING

        current_y += text_h + PLATFORM_TITLE_LINE_SPACING

    title_bottom_y = current_y - PLATFORM_TITLE_LINE_SPACING  # 最后一行的真实底部

    print(f"[Step 2] 主标题渲染完成 | 底部Y: {title_bottom_y} | 行数: {len(title_lines)}")

    # ============================================================
    # 7. 渲染副标题（根据平台调整布局和效果 - 从配置文件读取间距）
    # ============================================================
    # 使用配置文件中的主副标题间距
    subtitle_start_y = title_bottom_y + PLATFORM_SUBTITLE_MARGIN_TOP

    current_y = subtitle_start_y

    for line in subtitle_lines:
        bbox = get_text_bbox(line, font_subtitle)
        text_h = bbox[3] - bbox[1]
        text_w = bbox[2] - bbox[0]

        x = MARGIN  # 硬编码左对齐，废除所有居中逻辑

        # 绘制主文本（移除发光效果，使用纯粹深色填充）
        draw.text((x, current_y), line, font=font_subtitle, fill=subtitle_color)
        current_y += text_h + 10

    subtitle_bottom_y = current_y - 10  # 副标题最后一行的底部
    print(f"[Step 2] 副标题渲染完成 | 起始Y: {subtitle_start_y} | 底部Y: {subtitle_bottom_y} | 间距: {PLATFORM_SUBTITLE_MARGIN_TOP}px")

    # ============================================================
    # 8. 底部说明文案（根据配置文件决定是否显示）
    # ============================================================
    if description and PLATFORM_SHOW_DESCRIPTION:
        # 段落间距：副标题底部到说明文案顶部
        description_margin_top = 40

        # 字体降级：32pt，颜色 #666666
        DESCRIPTION_FONT_SIZE = 32
        font_description = get_sans_font(DESCRIPTION_FONT_SIZE)

        # 清洗文本
        description_clean = clean_text(description)

        # 自动换行：按像素宽度逐字累加
        description_lines = wrap_text_by_width(description_clean, font_description, usable_width)

        # 行高：字号的 1.5 倍
        line_height = int(DESCRIPTION_FONT_SIZE * 1.5)

        # 起始 Y 坐标（使用配置文件中的间距）
        description_y = subtitle_bottom_y + PLATFORM_DESCRIPTION_MARGIN_TOP

        # 渲染每一行（强制左对齐，X 坐标 = MARGIN）
        current_y = description_y
        for line in description_lines:
            draw.text((MARGIN, current_y), line, font=font_description, fill=META_COLOR)
            current_y += line_height

        print(f"[Step 2] 底部说明文案: {len(description_lines)}行 | 起始Y: {description_y} | 字号: {DESCRIPTION_FONT_SIZE}pt | 行高: {line_height}px")
    else:
        print(f"[Step 2] {platform}模式：跳过底部说明文案")

    # ============================================================
    # 9. 底部品牌标识（已禁用 - 避免在手机缩略图上造成干扰）
    # ============================================================
    # brand_text = "MERCURY ART GALLERY"
    # brand_y = CANVAS_H - 40
    # brand_bbox = get_text_bbox(brand_text, font_meta)
    # brand_w = brand_bbox[2] - brand_bbox[0]
    # brand_x = (CANVAS_W - brand_w) // 2
    # draw.text((brand_x, brand_y), brand_text, font=font_meta, fill=META_COLOR)

    # ============================================================
    # 9. 噪点纹理 + 保存
    # ============================================================
    canvas = add_noise_texture(canvas, intensity=0.025)
    canvas.save(output_path, "PNG", quality=95)
    print(f"[Step 2] 封面已保存: {output_path}")


# ============================================================
# 主函数
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="全自动封面生成流水线 - 新古典人文主义视觉系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python auto_cover_engine.py --title "人类简史\\n认知革命" --concept "从生物学到历史学" --style organic-botanical
  python auto_cover_engine.py --title "宫崎骏\\n作品集" --concept "七次复出 一生作画" --style classic-print
  python auto_cover_engine.py --title "数据思维" --concept "硬核逻辑与第一性原理" --style academic-grid
  python auto_cover_engine.py --title "极简主义" --concept "少即是多" --volume "VOL.02" --margin-left 120
        """
    )
    parser.add_argument("--title", "-t", required=True, help="产品名称/主标题（支持\\n强制换行，如：'第一行\\n第二行'）")
    parser.add_argument("--concept", "-c", required=True, help="核心概念/副标题")
    parser.add_argument("--description", default=None, help="底部说明文案（如'11部经典作品完整收录'）")
    parser.add_argument("--volume", "-v", default="VOL.01", help="卷号 (默认: VOL.01)")
    parser.add_argument("--date", "-d", default=None, help="日期 (默认: 今天)")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径 (默认: output/封面.png)")
    parser.add_argument("--size", "-s", default="2048x2048", help="底图尺寸 (默认: 2048x2048 1:1)")
    parser.add_argument("--bg", default=None, help="使用自定义底图路径（跳过豆包生成，直接渲染文字）")
    parser.add_argument("--no-text", action="store_true", help="仅生成/使用底图，不叠加文字")
    parser.add_argument("--title-align", default="left", choices=["left", "center", "right"], help="主标题对齐 (默认: left)")
    parser.add_argument("--subtitle-align", default="left", choices=["left", "center", "right"], help="副标题对齐 (默认: left)")
    parser.add_argument("--margin-left", type=int, default=MARGIN_LEFT, help=f"左侧边距X轴锚点 (默认: {MARGIN_LEFT})")
    parser.add_argument("--title-line-spacing", type=int, default=30, help="主标题行间距 px (默认: 30)")
    parser.add_argument("--subtitle-margin-top", type=int, default=85, help="主副标题间距 px (默认: 85)")
    parser.add_argument("--bg-prompt", default=None, help="自定义底图正向提示词（覆盖默认prompt）")
    parser.add_argument("--style", default=DEFAULT_STYLE,
                        choices=["contrast-impact", "whitespace-aesthetic", "grid-system",
                                "classic-print", "organic-botanical", "academic-grid"],
                        help=f"底图风格 (默认: {DEFAULT_STYLE}, Wiki推荐: contrast-impact)")
    parser.add_argument("--clean", action="store_true", help="使用纯净极简底图生成模式")
    parser.add_argument("--hook", default=None, help="顶部钩子文案（如'留白占了九成'），仅用于 contrast-impact 风格")
    parser.add_argument("--platform", default="poster", choices=["poster", "douyin"],
                        help="渲染平台 (poster=海报版长文案, douyin=抖音版极简大字, 默认: poster)")
    parser.add_argument("--account", default=None,
                        choices=["yushangyuan", "jiulimi", "adscout"],
                        help="账号风格 (yushangyuan=余上沅的奇妙屋, jiulimi=九厘米的雾, adscout=Ad Scout)")

    args = parser.parse_args()

    # 修复命令行 \n 被当成字符串的问题
    if args.title:
        args.title = args.title.replace('\\n', '\n')
    if args.concept:
        args.concept = args.concept.replace('\\n', '\n')

    # 确保最小像素 (3686400)
    parts = args.size.split("x")
    if len(parts) == 2:
        w, h = int(parts[0]), int(parts[1])
        if w * h < 3686400:
            print(f"[WARN] 尺寸 {args.size} 像素不足，自动调整为 1920x2560")
            args.size = "1920x2560"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 收件箱路径
    inbox_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "00_InBox_收件箱"))
    os.makedirs(inbox_dir, exist_ok=True)

    # 生成安全文件名(用于收件箱)
    safe_name = args.title.replace("/", "_").replace("\\", "_").replace("\n", "_").replace("\r", "_").replace("\t", "_")[:20]

    # 确定输出路径
    if args.output:
        output_path = args.output if os.path.isabs(args.output) else os.path.join(script_dir, args.output)
    else:
        output_path = os.path.join(output_dir, f"{safe_name}_封面.png")

    # 收件箱输出路径
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d")
    inbox_output_path = os.path.join(inbox_dir, f"{timestamp}-{safe_name}-封面.png")

    # 确定底图 prompt（--bg-prompt 最高优先级，--clean 次之，--style 常规模式）
    custom_prompt = None
    style = DEFAULT_STYLE
    if args.bg_prompt:
        custom_prompt = args.bg_prompt
        print(f"[INFO] 使用自定义底图提示词")
    elif args.clean:
        custom_prompt = build_clean_minimal_prompt(args.concept)
        print(f"[INFO] --clean 模式：使用纯净极简底图提示词")
    else:
        style = args.style
        print(f"[INFO] 使用风格: {style}")

    try:
        # Step 1: 确定底图来源（底图只需生成一次，三种账号共用）
        if args.bg:
            bg_path = args.bg
            print(f"[Step 1] 使用自定义底图: {bg_path}")
        else:
            # Step 1: 生成底图
            bg_path = generate_background(
                args.concept, args.size,
                custom_prompt=custom_prompt,
                use_strong_negative=True,
                style=style,
                title=args.title
            )

        account_list = []
        generated_files = []

        if args.no_text:
            print(f"[INFO] --no-text 模式，仅保存底图")
            import shutil
            shutil.copy(bg_path, output_path)
            shutil.copy(bg_path, inbox_output_path)
            print(f"[SUCCESS] 底图已保存: {output_path}")
            print(f"[SUCCESS] 已复制到收件箱: {inbox_output_path}")
        else:
            # 确定要生成的账号列表
            import shutil
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d")

            if args.account:
                # 指定了账号，只生成1个
                account_list = [args.account]
            else:
                # 未指定账号，默认生成3个版本
                account_list = ["yushangyuan", "jiulimi", "adscout"]
                print(f"[INFO] 未指定 --account，默认生成三套账号版本")

            generated_files = []
            for acct in account_list:
                # 输出文件名带账号后缀
                acct_suffix = CONFIG["accounts"][acct]["name"] if acct in CONFIG.get("accounts", {}) else acct
                if len(account_list) > 1:
                    safe_name_acct = f"{safe_name}_{acct}"
                else:
                    safe_name_acct = safe_name

                acct_output = os.path.join(output_dir, f"{safe_name_acct}_封面.png")
                acct_inbox = os.path.join(inbox_dir, f"{timestamp}-{safe_name_acct}-封面.png")

                # Step 2: 渲染封面（同一张底图，不同账号排版）
                render_cover(bg_path, args.title, args.concept, acct_output,
                            volume=args.volume, date=args.date,
                            title_align=args.title_align, subtitle_align=args.subtitle_align,
                            margin_left=args.margin_left,
                            title_line_spacing=args.title_line_spacing,
                            subtitle_margin_top=args.subtitle_margin_top,
                            style=style,
                            hook_text=args.hook,
                            description=args.description,
                            platform=args.platform,
                            account=acct)

                # 复制到收件箱
                shutil.copy(acct_output, acct_inbox)
                print(f"[SUCCESS] {acct_suffix} → {acct_output}")
                generated_files.append(acct_output)

            output_path = generated_files[0]  # 主输出指向第一个

        print(f"\n========== 完成 ==========")
        if not args.no_text and len(account_list) > 1:
            print(f"已生成 {len(account_list)} 个版本:")
            for f in generated_files:
                print(f"  → {f}")
        else:
            print(f"封面路径: {output_path}")
        print(f"画布尺寸: {CANVAS_W}x{CANVAS_H} (3:4)")
        print(f"风格: 新古典人文主义")

    except Exception as e:
        print(f"[ERROR] 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
