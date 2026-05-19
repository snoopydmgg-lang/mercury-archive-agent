#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绝对锚点封面排版引擎 (Absolute Anchor Cover Layout Engine)
==========================================================
废除相对流式布局 (y = previous_y + height)，所有元素 Y 坐标
基于 CANVAS_H 的固定比例常量，确保多封面在网格视图中精确对齐。

设计约束:
- 严禁 y = previous_y + height 链式依赖
- 所有核心元素 Y = CANVAS_H * 固定比例
- 图像在固定容器内 ImageOps.contain，不推挤文本
- 分割线作为物理对齐锚点
- 文本换行向下延展，绝对不改变基线 Y
"""

import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ============================================================
# 全局视觉常量
# ============================================================
BG_COLOR  = (245, 244, 240)   # #F5F4F0 — 规范主背景色，强制所有画布底色

# ============================================================
# 绝对坐标系常量 — 所有值均为 CANVAS_W/CANVAS_H 的固定比例
# ============================================================
CANVAS_W = 1080
CANVAS_H = 1440

MARGIN_X = int(CANVAS_W * 0.10)            # 108px — 左右统一边距

IMAGE_BOX_TOP    = int(CANVAS_H * 0.08)    # 115px — 图像容器上边界
IMAGE_BOX_BOTTOM = int(CANVAS_H * 0.55)    # 792px — 图像容器下边界
IMAGE_BOX_W      = CANVAS_W - 2 * MARGIN_X # 864px
IMAGE_BOX_H      = IMAGE_BOX_BOTTOM - IMAGE_BOX_TOP  # 677px

DIVIDER_LINE_Y        = int(CANVAS_H * 0.56)    # 806px — 分割线上移，给标题组留呼吸空间

H1_BASE_Y             = int(CANVAS_H * 0.62)    # 892px — 主标题第一行基线 (绝对锚点)
PADDING_TITLE_RATIO   = 0.9                       # H2_BASE_Y = H1_BASE_Y + H1字号 + (H2字号 × 此系数)

MARGIN_BOTTOM         = int(CANVAS_H * 0.08)     # 115px — 底部标签距画布底线

TEXT_MAX_W            = CANVAS_W - 2 * MARGIN_X  # 864px — 文本最大像素宽度


class CoverLayoutEngine:
    """绝对锚点封面排版引擎 — 只负责排版，不涉及颜色/图像生成"""

    def __init__(self, background):
        """
        Args:
            background: PIL Image，已缩放到 CANVAS_W×CANVAS_H 的画布
        """
        self.canvas = background.copy()
        self.draw = ImageDraw.Draw(self.canvas)

    # ================================================================
    # 图像放置 — 宽度铺满 + 物理裁剪 (Hard Crop)
    # ================================================================
    # 绝对安全边界: 图片最大高度 = 750px, H1 在 892px, 中间 142px 纯底色
    MAX_IMG_H = 750

    def place_image(self, image, top_rel=None, bottom_rel=None):
        """
        宽度强制 = CANVAS_W，等比缩放，超出 MAX_IMG_H 的部分物理切除。
        贴入 BG_COLOR 画布顶部 (0, 0)，文字区绝对干净。

        Returns:
            (0, 0, CANVAS_W, visible_h)
        """
        source = image.convert("RGB")
        sw, sh = source.size

        # 1. 宽度强制铺满
        cw = CANVAS_W
        ch = int(sh * (CANVAS_W / sw))
        source = source.resize((cw, ch), Image.Resampling.LANCZOS)

        # 2. 物理裁剪 — 超出 MAX_IMG_H 的部分直接切除
        if ch > self.MAX_IMG_H:
            source = source.crop((0, 0, cw, self.MAX_IMG_H))

        # 3. 贴入 BG_COLOR 画布顶部
        canvas_bg = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
        canvas_bg.paste(source, (0, 0))
        self.canvas = canvas_bg
        self.draw = ImageDraw.Draw(self.canvas)

        return (0, 0, cw, min(ch, self.MAX_IMG_H))

    # ================================================================
    # 分割线 — 物理对齐锚点
    # ================================================================
    def draw_divider(self, color=(211, 107, 77), width=1):
        """在 DIVIDER_LINE_Y 绘制从 MARGIN_X 到 CANVAS_W-MARGIN_X 的细线"""
        self.draw.line(
            [MARGIN_X, DIVIDER_LINE_Y, CANVAS_W - MARGIN_X, DIVIDER_LINE_Y],
            fill=color, width=width
        )
        return DIVIDER_LINE_Y

    # ================================================================
    # 主标题 (H1) — X=MARGIN_X, Y=H1_BASE_Y (绝对锚点)
    # ================================================================
    def render_h1(self, text, font, color=(45, 43, 42), line_spacing=None):
        """
        渲染主标题。
        X 锚点: MARGIN_X (严格左对齐)
        Y 锚点: H1_BASE_Y (绝对，永不改变)
        超宽自动换行，行高固定，向下延展不改变基线。

        Returns:
            list of (line_text, line_top_y)
        """
        if line_spacing is None:
            line_spacing = int(font.size * 1.35)

        # 存储 H1 参数，供 render_h2 做亲密性绑定
        self._h1_font_size   = font.size
        self._h1_line_height = line_spacing
        self._h1_lines_count = 0  # 填充前归零

        lines = self._wrap_pixels(text, font, TEXT_MAX_W)
        result = []
        y = H1_BASE_Y
        for line in lines:
            self.draw.text((MARGIN_X, y), line, font=font, fill=color)
            result.append((line, y))
            y += line_spacing
        self._h1_lines_count = len(lines)
        return result

    # ================================================================
    # 副标题 (H2) — X=MARGIN_X, Y=H2_BASE_Y (绝对锚点)
    # ================================================================
    def render_h2(self, text, font, color=(105, 100, 95), line_spacing=None):
        """
        渲染副标题 — 亲密性绑定在主标题下方。
        X 锚点: MARGIN_X (严格左对齐，与 H1 一致)
        Y 锚点: H1_BASE_Y + H1字号 + (H2字号 × PADDING_TITLE_RATIO)
               即：紧跟在主标题文本底部，不再使用独立绝对锚点。

        Returns:
            list of (line_text, line_top_y)
        """
        if line_spacing is None:
            line_spacing = int(font.size * 1.4)

        # 基于 H1 的亲密性绑定
        h1_size = getattr(self, '_h1_font_size', font.size)
        padding = int(font.size * PADDING_TITLE_RATIO)
        h2_base_y = H1_BASE_Y + h1_size + padding

        lines = self._wrap_pixels(text, font, TEXT_MAX_W)
        result = []
        y = h2_base_y
        for line in lines:
            self.draw.text((MARGIN_X, y), line, font=font, fill=color)
            result.append((line, y))
            y += line_spacing
        return result

    # ================================================================
    # 底部说明文案 — 固定 Y 锚点
    # ================================================================
    def render_description(self, text, font, color=(102, 102, 102),
                           line_spacing=None):
        """
        渲染底部说明文案 — 沉底锚定。
        Y 锚点: CANVAS_H - MARGIN_BOTTOM - font.size (紧贴底部边距)
        X 锚点: MARGIN_X (严格左对齐，与 H1/H2 一致)
        """
        if line_spacing is None:
            line_spacing = int(font.size * 1.5)

        lines = self._wrap_pixels(text, font, TEXT_MAX_W)
        # 最底行贴在距画布下缘 MARGIN_BOTTOM 处
        tag_base_y = CANVAS_H - MARGIN_BOTTOM - font.size
        # 多行时整体上移
        y = tag_base_y - (len(lines) - 1) * line_spacing
        for line in lines:
            self.draw.text((MARGIN_X, y), line, font=font, fill=color)
            y += line_spacing
        return lines

    # ================================================================
    # 像素宽度自动换行
    # ================================================================
    @staticmethod
    def _wrap_pixels(text, font, max_width):
        """逐字累加像素宽度，超宽即换行"""
        lines = []
        current = ""
        for ch in text:
            test = current + ch
            bbox = font.getbbox(test)
            if (bbox[2] - bbox[0]) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
        return lines if lines else [text]

    # ================================================================
    # 全局质感后处理 — 单色高斯噪点叠加
    # ================================================================
    def apply_global_noise(self, intensity=0.03):
        """
        在所有 paste / draw.text / draw.line 完成之后，
        对整张成品叠加 2-4% 单色高斯噪点，模拟物理印刷品的微观粗糙感。

        使用 numpy 生成高斯噪点矩阵 → 三通道叠加 → clip 回 [0,255]。
        必须在 save() 之前调用。
        """
        arr = np.array(self.canvas.convert("RGB"), dtype=np.float32)
        h, w, _ = arr.shape

        # 单色高斯噪点 (μ=0, σ=255*intensity)
        noise = np.random.normal(0, 255 * intensity, (h, w)).astype(np.float32)
        noise_3ch = np.stack([noise] * 3, axis=-1)

        arr = np.clip(arr + noise_3ch, 0, 255).astype(np.uint8)
        self.canvas = Image.fromarray(arr)
        return self

    # ================================================================
    # 保存
    # ================================================================
    def save(self, path, quality=95, noise_intensity=0.03):
        """保存前自动叠加全局噪点"""
        self.apply_global_noise(intensity=noise_intensity)
        self.canvas.save(path, quality=quality)


# ================================================================
# 便捷函数 — 一站式绝对锚点封面生成
# ================================================================
def render_cover_absolute(
    background_path,      # 底图路径
    output_path,          # 输出路径
    title_text,           # 主标题
    subtitle_text,        # 副标题
    title_font,           # PIL ImageFont (主标题)
    subtitle_font,        # PIL ImageFont (副标题)
    title_color=(45, 43, 42),
    subtitle_color=(105, 100, 95),
    divider_color=(211, 107, 77),
    description_text=None,
    description_font=None,
    description_color=(102, 102, 102),
    ai_image_path=None,   # AI 生成的插图路径
):
    """
    一站式绝对锚点封面生成。
    所有元素 Y 坐标使用固定比例常量，确保多封面网格对齐。
    """
    # 1. 加载并缩放底图到画布
    bg = Image.open(background_path).convert("RGB")
    bg = bg.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    engine = CoverLayoutEngine(bg)

    # 2. AI 插图 → 固定容器
    if ai_image_path:
        engine.place_image(Image.open(ai_image_path))

    # 3. 分割线 → 绝对锚点
    engine.draw_divider(color=divider_color, width=1)

    # 4. 主标题 → H1_BASE_Y 绝对锚点
    engine.render_h1(title_text, title_font, color=title_color)

    # 5. 副标题 → 基于 H1 的亲密性绑定
    engine.render_h2(subtitle_text, subtitle_font, color=subtitle_color)

    # 6. 底部说明 → 沉底锚定 (CANVAS_H - MARGIN_BOTTOM)
    if description_text and description_font:
        engine.render_description(description_text, description_font,
                                 color=description_color)

    engine.save(output_path)
    return output_path
