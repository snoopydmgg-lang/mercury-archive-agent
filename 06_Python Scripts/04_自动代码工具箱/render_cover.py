from PIL import Image, ImageDraw, ImageFont
import os

# 封面尺寸 1080x1440 (3:4)
W, H = 1080, 1440

# 颜色
BG = (245, 244, 240)       # #F5F4F0
INK = (45, 43, 42)         # #2D2B2A
ACCENT = (211, 107, 77)    # #D36B4D
GRAY = (138, 133, 128)      # #8A8580

# 字体 - 全部使用微软雅黑
font_path = "C:/Windows/Fonts/msyh.ttc"
font_big = ImageFont.truetype(font_path, 88)
font_large = ImageFont.truetype(font_path, 96)
font_xlarge = ImageFont.truetype(font_path, 120)
font_mid = ImageFont.truetype(font_path, 28)
font_small = ImageFont.truetype(font_path, 20)
font_title = ImageFont.truetype(font_path, 15)

# =====================
# 封面02 - 留白风格
# =====================
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# 边框线
draw.rectangle([50, 50, W-50, H-50], outline=INK, width=2)
draw.line([50, 180, W-50, 180], fill=INK, width=1)
draw.line([50, 1260, W-50, 1260], fill=INK, width=1)

# 顶部文字
draw.text((80, 110), "LAYOUT PRINCIPLES", font=font_small, fill=INK)
draw.text((W-80, 110), "VOL.02", font=font_small, fill=ACCENT)

# 主标题 - 使用大号字体
draw.text((80, 420), "留白，", font=font_large, fill=INK)
draw.text((80, 540), "不是空着。", font=font_large, fill=INK)

# 赤陶色装饰线
draw.line([80, 680, 400, 680], fill=ACCENT, width=3)

# 副标题
draw.text((80, 760), "日本设计大师的版式哲学", font=font_mid, fill=GRAY)

# 底部标签
draw.rectangle([80, 1100, 280, 1144], fill=INK)
draw.text((180, 1128), "6大创意风格", font=font_title, fill=BG, anchor="mm")

draw.rectangle([310, 1100, 510, 1144], outline=INK, width=2)
draw.text((410, 1128), "77种版式策略", font=font_title, fill=INK, anchor="mm")

draw.rectangle([540, 1100, 740, 1144], outline=ACCENT, width=2)
draw.text((640, 1128), "18位大师亲授", font=font_title, fill=ACCENT, anchor="mm")

# 右下角几何图形
draw.rectangle([780, 820, 960, 1000], fill=(230, 200, 181))
draw.rectangle([805, 845, 935, 975], fill=ACCENT)
draw.rectangle([830, 870, 910, 950], fill=BG)
draw.ellipse([870, 910, 900, 940], fill=INK)

# 底部出版社
draw.text((W-80, 1280), "SendPoints 善本", font=font_title, fill=GRAY, anchor="rs")
draw.text((W-80, 1310), "版式之道", font=font_title, fill=GRAY, anchor="rs")

img.save("E:/1.work/douyin/1.shuixing/01_Projects_制作中/版式之道/00_封面设计/版式之道_VOL.02_封面_留白.png", quality=95)
print("vol02 ok")

# =====================
# 封面03 - 网格风格
# =====================
img2 = Image.new("RGB", (W, H), BG)
draw2 = ImageDraw.Draw(img2)

# 网格线
for y in [360, 720, 1080]:
    draw2.line([0, y, W, y], fill=INK, width=1)
for x in [270, 540, 810]:
    draw2.line([x, 0, x, H], fill=INK, width=1)

# 左侧强调线
draw2.line([70, 80, 70, 1360], fill=ACCENT, width=4)

# 顶部
draw2.text((100, 110), "GRAPHIC DESIGN", font=font_small, fill=GRAY)
draw2.text((100, 140), "LAYOUT SYSTEM", font=font_small, fill=GRAY)
draw2.text((W-80, 110), "VOL.03", font=font_small, fill=ACCENT)

# 主标题
draw2.text((100, 420), "版式", font=font_large, fill=INK)
draw2.text((100, 540), "之道", font=font_large, fill=INK)

# 副标题
draw2.text((100, 660), "对比 · 重复 · 对齐 · 亲密性", font=font_mid, fill=GRAY)

# 分割线
draw2.line([100, 700, 450, 700], fill=ACCENT, width=2)

# 数据 - 使用数字字体
font_num_large = ImageFont.truetype(font_path, 120)
font_num_mid = ImageFont.truetype(font_path, 72)

draw2.text((100, 800), "18", font=font_num_large, fill=INK)
draw2.text((320, 850), "位日本大师", font=font_mid, fill=GRAY)

draw2.text((100, 940), "77", font=font_num_mid, fill=ACCENT)
draw2.text((280, 990), "种版式策略", font=font_title, fill=GRAY)

# 右下角圆形装饰
draw2.ellipse([920, 1000, 1040, 1120], fill=(230, 200, 181))
draw2.ellipse([940, 1020, 1020, 1100], fill=ACCENT)
draw2.ellipse([960, 980, 1000, 1020], fill=INK)
draw2.ellipse([930, 1040, 955, 1065], fill=BG)

# 出版社
draw2.text((W-80, 1260), "SENDPOINTS", font=font_title, fill=INK, anchor="rs")
draw2.text((W-80, 1290), "善本出版社", font=font_title, fill=GRAY, anchor="rs")

# 日期
draw2.text((100, 1380), "2026", font=font_small, fill=GRAY)

img2.save("E:/1.work/douyin/1.shuixing/01_Projects_制作中/版式之道/00_封面设计/版式之道_VOL.03_封面_网格.png", quality=95)
print("vol03 ok")
