"""
飞鸟集封面资产注入脚本
功能：将分形/装饰图案资产叠加到基础封面上
依赖：Pillow
"""
from PIL import Image, ImageEnhance
import os
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def composite_asset(base_cover_path, asset_path, output_path):
    """
    将图形资产注入到基础封面

    Args:
        base_cover_path: 基础封面路径
        asset_path: 图形资产路径（PNG 透明底）
        output_path: 最终封面输出路径
    """
    if not os.path.exists(base_cover_path):
        print(f"错误：基础封面文件不存在 {base_cover_path}")
        return False

    if not os.path.exists(asset_path):
        print(f"错误：图形资产文件不存在 {asset_path}")
        print("提示：请准备一个透明底的 PNG 图形资产文件")
        return False

    # 加载底图与资产
    base_img = Image.open(base_cover_path).convert("RGBA")
    asset_img = Image.open(asset_path).convert("RGBA")

    print(f"基础封面尺寸：{base_img.size}")
    print(f"资产原始尺寸：{asset_img.size}")

    # 1. 资产尺寸与位置计算（锚定右侧留白区域）
    # 设定资产目标宽度为 500px
    target_width = 500
    ratio = target_width / asset_img.width
    target_height = int(asset_img.height * ratio)
    asset_img = asset_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    print(f"资产缩放后尺寸：{asset_img.size}")

    # 计算绝对坐标：靠右放置，垂直居中偏上
    pos_x = 1080 - 60 - target_width - 40  # 右边距60，额外缩进40
    pos_y = 450

    print(f"资产放置位置：({pos_x}, {pos_y})")

    # 2. 创建合成图层
    composite_layer = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    composite_layer.paste(asset_img, (pos_x, pos_y), asset_img)

    # 3. 透明度微调（克制感）
    # 降低资产的不透明度至 85%，确保不喧宾夺主
    alpha = composite_layer.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.85)
    composite_layer.putalpha(alpha)

    print("已调整资产透明度至 85%")

    # 4. 执行合成
    final_img = Image.alpha_composite(base_img, composite_layer)

    # 转换为 RGB 并保存
    final_img = final_img.convert("RGB")
    final_img.save(output_path, quality=95)
    print(f"资产已注入，最终封面生成：{output_path}")
    return True


if __name__ == "__main__":
    # 基础封面
    base_cover = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-规范版.png"

    # 图形资产（需要用户提供）
    # 可以是：分形图案、装饰纹样、抽象几何等
    asset_file = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/raw/个人视觉系统设计/fractal_asset.png"

    # 最终输出
    output_file = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-最终完全体.png"

    composite_asset(base_cover, asset_file, output_file)
