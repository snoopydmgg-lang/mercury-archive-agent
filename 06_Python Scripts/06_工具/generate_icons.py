"""生成水星艺术馆品牌图标 - .ico 多尺寸"""
import os, struct, random
from PIL import Image, ImageDraw, ImageFilter

BG      = (245, 244, 240)  # #F5F4F0
TEXT    = (45,  43,  42)   # #2D2B2A
ACCENT  = (211, 107, 77)   # #D36B4D
OUT_DIR = r"E:\1.work\douyin\1.shuixing\00_InBox_收件箱\icon_samples"
os.makedirs(OUT_DIR, exist_ok=True)

def add_noise(img, amount=0.03):
    """添加 2-5% 噪点"""
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if random.random() < amount:
                noise = random.randint(-25, 25)
                pixels[x, y] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise)),
                    a
                )
    return img

def rounded_rect(draw, xy, r, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=r, fill=fill)

def make_icon(name, draw_func, sizes=[16, 32, 48, 256]):
    """生成多尺寸 .ico - 手动构造 ICO 格式"""
    import io, struct

    png_datas = []
    for s in sizes:
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        draw_func(img, s)
        img = add_noise(img, random.uniform(0.02, 0.05))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_datas.append(buf.getvalue())

    # Build ICO header
    path = os.path.join(OUT_DIR, f"{name}.ico")
    with open(path, "wb") as f:
        count = len(sizes)
        f.write(struct.pack("<HHH", 0, 1, count))  # reserved, type=ICO, count

        # Directory entries
        offset = 6 + 16 * count
        for s, png_data in zip(sizes, png_datas):
            w = 0 if s == 256 else s
            h = 0 if s == 256 else s
            f.write(struct.pack("<BBBBHHII",
                w, h,          # width, height (0 = 256)
                0,             # color palette
                0,             # reserved
                1,             # planes
                32,            # bpp
                len(png_data), # size
                offset         # offset
            ))
            offset += len(png_data)

        # Image data
        for png_data in png_datas:
            f.write(png_data)

    # Verification
    v_img = Image.open(path)
    v_sizes = []
    i = 0
    while True:
        try:
            v_img.seek(i)
            v_sizes.append(v_img.size)
            i += 1
        except EOFError:
            break

    # 256x256 PNG 预览
    preview_img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw_func(preview_img, 256)
    preview_img = add_noise(preview_img, random.uniform(0.02, 0.05))
    png_path = os.path.join(OUT_DIR, f"{name}_preview.png")
    preview_img.save(png_path)

    print(f"  {name}.ico ({len(v_sizes)} sizes: {v_sizes}) + preview.png")
    return path

# ============================================================
# 图标 1: 主文件夹 - 水星品牌色
# ============================================================
def draw_folder_icon(img, size):
    draw = ImageDraw.Draw(img)
    m = size * 0.08  # margin
    tab_w = size * 0.28
    tab_h = size * 0.08

    # 文件夹标签
    rounded_rect(draw, (m, m + tab_h, m + tab_w, m + tab_h * 2), size * 0.04, fill=ACCENT)
    # 文件夹主体
    rounded_rect(draw, (m, m + tab_h, size - m, size - m), size * 0.06, fill=BG + (255,))
    draw.rectangle((m, m + tab_h * 2, size - m, size - m), fill=BG + (255,))
    # 边框
    rounded_rect(draw, (m, m + tab_h, size - m, size - m), size * 0.06, fill=None)
    draw.rounded_rectangle((m, m + tab_h, size - m, size - m), radius=size*0.06, outline=TEXT + (80,), width=max(1, size//64))
    # 标签边框
    draw.rounded_rectangle((m, m + tab_h, m + tab_w, m + tab_h * 2), radius=size*0.04, outline=TEXT + (60,), width=max(1, size//64))

# ============================================================
# 图标 2: 视频制作 (播放三角 + 点缀色)
# ============================================================
def draw_video_icon(img, size):
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.38

    # 圆形背景
    rounded_rect(draw, (cx - r, cy - r, cx + r, cy + r), r, fill=BG + (255,))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=TEXT + (60,), width=max(1, size//48))

    # 播放三角
    tri = size * 0.18
    offset_x = size * 0.04
    draw.polygon([
        (cx - tri * 0.7 + offset_x, cy - tri),
        (cx - tri * 0.7 + offset_x, cy + tri),
        (cx + tri * 1.1 + offset_x, cy)
    ], fill=ACCENT)

# ============================================================
# 图标 3: 知识库 (书本)
# ============================================================
def draw_book_icon(img, size):
    draw = ImageDraw.Draw(img)
    m = size * 0.12
    spine = size * 0.12

    # 封面
    rounded_rect(draw, (m + spine, m, size - m, size - m), size * 0.04, fill=BG + (255,))
    # 书脊
    draw.rectangle((m, m, m + spine, size - m), fill=ACCENT + (200,))
    # 封面边框
    draw.rounded_rectangle((m + spine, m, size - m, size - m), radius=size*0.04, outline=TEXT + (80,), width=max(1, size//48))
    # 内页线
    line_x = m + spine + size * 0.12
    draw.line((line_x, m + size * 0.18, line_x, size - m - size * 0.18), fill=TEXT + (30,), width=max(1, size//64))

# ============================================================
# 图标 4: 文案/编辑 (笔)
# ============================================================
def draw_edit_icon(img, size):
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.38

    # 圆形背景
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BG + (255,), outline=TEXT + (60,), width=max(1, size//48))

    # 笔尖
    pw = size * 0.06
    pen_top = (cx, cy - size * 0.22)
    pen_bot = (cx, cy + size * 0.22)
    draw.line((pen_top, pen_bot), fill=ACCENT, width=max(3, size//16))
    # 横线
    lw = size * 0.14
    for i, y_off in enumerate([-0.05, 0.08, 0.21]):
        y = cy + y_off * size
        draw.line((cx - lw, y, cx + lw, y), fill=TEXT + (70,), width=max(1, size//48))

# ============================================================
# 图标 5: 选品/评分 (菱形钻石)
# ============================================================
def draw_gem_icon(img, size):
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.32

    # 菱形
    diamond = [
        (cx, cy - r),
        (cx + r, cy),
        (cx, cy + r),
        (cx - r, cy)
    ]
    draw.polygon(diamond, fill=BG + (255,), outline=TEXT + (80,))
    # 内菱形
    inner_r = r * 0.35
    inner = [
        (cx, cy - inner_r),
        (cx + inner_r, cy),
        (cx, cy + inner_r),
        (cx - inner_r, cy)
    ]
    draw.polygon(inner, fill=ACCENT)

# ============================================================
# 图标 6: 主 Logo (水星-环形)
# ============================================================
def draw_logo_icon(img, size):
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    outer_r = size * 0.36
    inner_r = size * 0.24
    ring_w = max(3, size // 24)

    # 外环
    draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
                 outline=TEXT + (180,), width=ring_w)
    # 内环 (点缀色)
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
                 outline=ACCENT + (200,), width=ring_w)
    # 中心点
    dot_r = size * 0.06
    draw.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=ACCENT)

# ============================================================
# 生成所有图标
# ============================================================
print("生成品牌图标...")
make_icon("folder",    draw_folder_icon)
make_icon("video",     draw_video_icon)
make_icon("book",      draw_book_icon)
make_icon("edit",      draw_edit_icon)
make_icon("gem",       draw_gem_icon)
make_icon("logo",      draw_logo_icon)
print(f"\n完成 -> {OUT_DIR}")
