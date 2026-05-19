#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从会议照片中提取投影幕布内容并矫正为正面视角
"""

import cv2
import numpy as np
import argparse
import sys


def imread_chinese(file_path):
    """读取中文路径的图片"""
    with open(file_path, 'rb') as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_chinese(file_path, img):
    """保存到中文路径"""
    ext = file_path.split('.')[-1]
    _, encoded = cv2.imencode(f'.{ext}', img)
    with open(file_path, 'wb') as f:
        f.write(encoded)


def extract_screen(image_path, screen_corners, output_path, output_width=1920, output_height=1080):
    """
    从会议照片中提取幕布内容并矫正

    参数:
        image_path: 会议照片路径
        screen_corners: 幕布四个角坐标 [[左上x,y], [右上x,y], [右下x,y], [左下x,y]]
        output_path: 输出路径
        output_width: 输出宽度
        output_height: 输出高度
    """
    img = imread_chinese(image_path)
    if img is None:
        raise Exception(f"无法读取图片: {image_path}")

    print(f"[INFO] 原图尺寸: {img.shape[1]}x{img.shape[0]}")
    print(f"[INFO] 幕布坐标: {screen_corners}")

    # 源坐标（幕布四个角）
    pts_src = np.array(screen_corners, dtype=np.float32)

    # 目标坐标（矩形）
    pts_dst = np.array([
        [0, 0],
        [output_width, 0],
        [output_width, output_height],
        [0, output_height]
    ], dtype=np.float32)

    # 计算透视变换矩阵
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # 执行透视变换
    extracted = cv2.warpPerspective(img, matrix, (output_width, output_height))

    # 保存结果
    imwrite_chinese(output_path, extracted)
    print(f"[SUCCESS] 提取完成！保存路径: {output_path}")
    print(f"[INFO] 输出尺寸: {output_width}x{output_height}")

    return extracted


def main():
    parser = argparse.ArgumentParser(
        description="从会议照片中提取投影幕布内容并矫正为正面视角"
    )
    parser.add_argument("--image", required=True, help="会议照片路径")
    parser.add_argument("--corners", required=True, help="幕布四个角坐标，格式: x1,y1,x2,y2,x3,y3,x4,y4")
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--width", type=int, default=1920, help="输出宽度（默认1920）")
    parser.add_argument("--height", type=int, default=1080, help="输出高度（默认1080）")

    args = parser.parse_args()

    # 解析坐标
    coords = list(map(int, args.corners.split(',')))
    if len(coords) != 8:
        print("[ERROR] --corners 参数格式错误，需要8个数字（4个点的x,y坐标）")
        sys.exit(1)
    screen_corners = [[coords[i], coords[i+1]] for i in range(0, 8, 2)]

    # 执行提取
    try:
        extract_screen(args.image, screen_corners, args.output, args.width, args.height)
    except Exception as e:
        print(f"[ERROR] 提取失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
