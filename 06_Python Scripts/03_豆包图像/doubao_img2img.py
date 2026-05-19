#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆包图生图 API 调用的 Python 脚本
功能：接收一张本地图片，调用火山引擎豆包的图生图 API，生成一张新图片并保存到本地
"""

import argparse
import base64
import os
import sys
import requests


def image_to_base64(image_path):
    """
    将本地图片转换为 base64 编码
    """
    with open(image_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")


def get_image_format(image_path):
    """
    根据文件扩展名判断图片格式
    """
    ext = os.path.splitext(image_path)[1].lower()
    if ext == '.png':
        return 'image/png'
    elif ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif ext == '.gif':
        return 'image/gif'
    elif ext == '.webp':
        return 'image/webp'
    else:
        return 'image/png'  # 默认


def generate_image(image_path, prompt, add_cover_rules=True):
    """
    调用豆包图生图 API 生成新图片

    参数:
        image_path: 输入图片的路径
        prompt: 图像生成的提示词
        add_cover_rules: 是否添加封面专用规则（默认True，封面场景用；视频素材等场景设为False）

    返回:
        生成图片的 URL
    """
    # 自动添加比例和风格要求到提示词
    prompt = prompt.strip()
    if "3:4" not in prompt and "3:4" not in prompt and "九宫格" not in prompt:
        prompt = prompt + "，图片比例为3:4（纵向），适用于抖音封面"

    # 添加通用规则：禁止AI相关文字、表情包
    forbidden_rules = "，重要提示：绝对不要在画面中出现任何文字、字母、汉字、'AI'、'AI生成'、'人工智能'等文字、不要添加任何表情包符号或emoji"
    prompt = prompt + forbidden_rules

    # 封面专用规则（仅当add_cover_rules=True时添加）
    if add_cover_rules:
        cover_rules = "、如果有任何文字标语必须使用书籍的名字作为Slogan、封面最上方必须使用书名作为标题"
        prompt = prompt + cover_rules

    # 火山引擎豆包 API 配置
    API_KEY = "3140fe69-b4ea-42fa-9d6b-e8257c3f2ff7"
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    MODEL_ID = "doubao-seedream-5-0-260128"

    # 将图片转换为 base64 编码
    base64_image = image_to_base64(image_path)

    # 获取图片格式
    image_format = get_image_format(image_path)
    image_url = f"data:{image_format};base64,{base64_image}"

    # 设置代理 - 尝试多个端口
    proxies_list = [
        {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"},
        {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"},
        {"http": "http://127.0.0.1:10809", "https": "http://127..0.0.1:10809"},
        {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"},
    ]

    # 调用图生图 API
    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # 设置输出尺寸
    # 根据提示词判断比例：16:9在提示词中则用16:9，否则默认3:4纵向
    # 16:9需要至少2560x1440才能满足最小像素要求
    if "16:9" in prompt or "横版" in prompt or "横向" in prompt:
        size = "2560x1440"  # 16:9, 满足最小像素要求
    else:
        size = "1920x2560"

    data = {
        "model": MODEL_ID,
        "prompt": prompt,
        "image": image_url,
        "size": size,
        "quality": "hd",
        "watermark": False,
        "logo_info": {"add_logo": False}
    }

    # 不使用代理，直接连接
    response = requests.post(url, headers=headers, json=data, timeout=180)

    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")

    result = response.json()
    return result["data"][0]["url"]


def download_and_save_image(image_url, output_path):
    """
    下载图片并保存到本地
    """
    # 不使用代理，直接连接
    response = requests.get(image_url, timeout=60)
    with open(output_path, "wb") as f:
        f.write(response.content)


def generate_image_text2img(prompt, output_path=None):
    """
    调用豆包纯文字生成 API（text2img）生成图片

    参数:
        prompt: 图像生成的提示词
        output_path: 输出图片路径（可选）

    返回:
        生成图片的 URL
    """
    # 火山引擎豆包 API 配置
    API_KEY = "3140fe69-b4ea-42fa-9d6b-e8257c3f2ff7"
    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    MODEL_ID = "doubao-seedream-5-0-260128"

    url = f"{BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 尺寸固定 1920x2560（3:4竖向，API要求最小像素3686400）
    size = "1920x2560"

    data = {
        "model": MODEL_ID,
        "prompt": prompt,
        "size": size,
        "quality": "hd",
        "watermark": False,
        "logo_info": {"add_logo": False}
    }

    print(f"[INFO] 调用 text2img API，尺寸: {size}")
    print(f"[INFO] 请求体: {data}")

    response = requests.post(url, headers=headers, json=data, timeout=180)

    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")

    result = response.json()
    print(f"[INFO] API 返回: {result}")
    return result["data"][0]["url"]


def main():
    """
    主函数：解析命令行参数，调用图生图 API，保存结果
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="豆包图生图工具 - 使用火山引擎豆包 API 将图片转换为指定风格"
    )
    parser.add_argument(
        "--image",
        required=False,
        help="输入图片的路径（img2img模式必需）"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="图像生成的提示词，描述希望生成的图片效果"
    )
    parser.add_argument(
        "--no-cover-rules",
        action="store_true",
        help="禁用封面专用规则（封面规则会要求添加书名标题等文字，用于视频素材等场景时加此参数）"
    )
    parser.add_argument(
        "--text2img",
        action="store_true",
        help="使用纯文字生成模式（text2img），不传入参考图片"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # text2img 模式
    if args.text2img:
        output_image_path = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/0414-飞鸟集-封面-text2img_output.png"
        print(f"[INFO] 使用 text2img 纯文字生成模式")
        print(f"[INFO] 提示词: {args.prompt}")
        print("[INFO] 正在调用豆包 text2img API，请稍候...")

        try:
            image_url = generate_image_text2img(args.prompt)
            download_and_save_image(image_url, output_image_path)
            print(f"[SUCCESS] 图片生成成功！保存路径：{output_image_path}")
        except Exception as e:
            print(f"[ERROR] 图片生成失败: {str(e)}")
            sys.exit(1)
        return

    # img2img 模式
    input_image_path = args.image

    # 检查输入图片是否存在
    if not os.path.exists(input_image_path):
        print(f"[ERROR] 输入图片不存在: {input_image_path}")
        sys.exit(1)

    # 获取输入图片所在目录和文件名（不含扩展名）
    input_dir = os.path.dirname(input_image_path)
    input_filename = os.path.basename(input_image_path)
    input_name_without_ext = os.path.splitext(input_filename)[0]

    # 构造输出图片路径：原文件名 + _output.png
    output_image_path = os.path.join(input_dir, f"{input_name_without_ext}_output.png")

    print(f"[INFO] 输入图片: {input_image_path}")
    print(f"[INFO] 提示词: {args.prompt}")
    print("[INFO] 正在调用豆包图生图 API，请稍候...")

    try:
        # 调用图生图 API
        image_url = generate_image(input_image_path, args.prompt, add_cover_rules=not args.no_cover_rules)

        # 下载并保存图片
        download_and_save_image(image_url, output_image_path)

        # 打印成功消息
        print(f"[SUCCESS] 图片生成成功！保存路径：{output_image_path}")

    except Exception as e:
        # 捕获并打印错误信息
        print(f"[ERROR] 图片生成失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
