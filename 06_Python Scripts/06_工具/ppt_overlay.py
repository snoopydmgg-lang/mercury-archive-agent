#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PPT投影合成工具 - 使用透视变换将PPT页面精确合成到会议照片的投影幕布上
避免AI重绘导致的人物边缘模糊问题
"""

import cv2
import numpy as np
import argparse
import sys


def imread_chinese(file_path):
    """
    读取中文路径的图片
    """
    with open(file_path, 'rb') as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_chinese(file_path, img):
    """
    保存到中文路径
    """
    ext = file_path.split('.')[-1]
    _, encoded = cv2.imencode(f'.{ext}', img)
    with open(file_path, 'wb') as f:
        f.write(encoded)


def overlay_ppt(room_img_path, ppt_img_path, screen_corners, output_path, brightness=0.85):
    """
    将PPT图片透视变换后叠加到会议室照片的投影幕布区域

    参数:
        room_img_path: 会议室照片路径
        ppt_img_path: PPT页面图片路径
        screen_corners: 幕布四个角的坐标 [[左上x,y], [右上x,y], [右下x,y], [左下x,y]]
        output_path: 输出图片路径
        brightness: PPT亮度调整系数（模拟投影效果，默认0.85）
    """
    # 读取图片（支持中文路径）
    bg_img = imread_chinese(room_img_path)
    ppt_img = imread_chinese(ppt_img_path)

    if bg_img is None:
        raise Exception(f"无法读取会议室照片: {room_img_path}")
    if ppt_img is None:
        raise Exception(f"无法读取PPT图片: {ppt_img_path}")

    print(f"[INFO] 会议室照片尺寸: {bg_img.shape[1]}x{bg_img.shape[0]}")
    print(f"[INFO] PPT图片尺寸: {ppt_img.shape[1]}x{ppt_img.shape[0]}")

    # 调整PPT亮度（模拟投影效果）
    ppt_img = (ppt_img * brightness).astype(np.uint8)

    # PPT原始四个角坐标
    h, w = ppt_img.shape[:2]
    pts_src = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)

    # 目标幕布坐标
    pts_dst = np.array(screen_corners, dtype=np.float32)

    print(f"[INFO] 幕布坐标: {screen_corners}")

    # 计算透视变换矩阵
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)

    # 对PPT进行透视变换
    warped_ppt = cv2.warpPerspective(ppt_img, matrix, (bg_img.shape[1], bg_img.shape[0]))

    # 创建mask（只在幕布区域内叠加）
    mask = np.zeros((bg_img.shape[0], bg_img.shape[1]), dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts_dst.astype(np.int32), 255)

    # 将mask扩展为3通道
    mask_3ch = cv2.merge([mask, mask, mask])

    # 叠加：在mask区域内用warped_ppt替换bg_img
    result = np.where(mask_3ch == 255, warped_ppt, bg_img)

    # 保存结果（支持中文路径）
    imwrite_chinese(output_path, result)
    print(f"[SUCCESS] 合成完成！保存路径: {output_path}")

    return result


def interactive_select_corners(image_path):
    """
    交互式选择幕布四个角的坐标
    """
    img = imread_chinese(image_path)
    if img is None:
        raise Exception(f"无法读取图片: {image_path}")

    # 缩放图片以适应屏幕
    scale = min(1.0, 1200 / max(img.shape[0], img.shape[1]))
    display_img = cv2.resize(img, None, fx=scale, fy=scale)

    corners = []
    corner_names = ["左上角", "右上角", "右下角", "左下角"]

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
            # 转换回原始坐标
            orig_x = int(x / scale)
            orig_y = int(y / scale)
            corners.append([orig_x, orig_y])

            # 在显示图上标记
            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(display_img, corner_names[len(corners)-1], (x+10, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow("选择幕布四个角", display_img)

            print(f"[INFO] 已选择 {corner_names[len(corners)-1]}: ({orig_x}, {orig_y})")

            if len(corners) == 4:
                print("[INFO] 四个角已选择完毕，按任意键继续...")

    cv2.imshow("选择幕布四个角", display_img)
    cv2.setMouseCallback("选择幕布四个角", mouse_callback)

    print("[INFO] 请依次点击幕布的四个角：左上 -> 右上 -> 右下 -> 左下")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return corners


def main():
    parser = argparse.ArgumentParser(
        description="PPT投影合成工具 - 将PPT页面透视变换后合成到会议照片"
    )
    parser.add_argument("--room", required=True, help="会议室照片路径")
    parser.add_argument("--ppt", required=True, help="PPT页面图片路径")
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--corners", help="幕布四个角坐标，格式: x1,y1,x2,y2,x3,y3,x4,y4")
    parser.add_argument("--interactive", action="store_true", help="交互式选择幕布坐标")
    parser.add_argument("--brightness", type=float, default=0.85, help="PPT亮度系数（默认0.85）")

    args = parser.parse_args()

    # 获取幕布坐标
    if args.interactive:
        print("[INFO] 进入交互模式，请在图片上选择幕布四个角...")
        screen_corners = interactive_select_corners(args.room)
    elif args.corners:
        coords = list(map(int, args.corners.split(',')))
        if len(coords) != 8:
            print("[ERROR] --corners 参数格式错误，需要8个数字（4个点的x,y坐标）")
            sys.exit(1)
        screen_corners = [[coords[i], coords[i+1]] for i in range(0, 8, 2)]
    else:
        print("[ERROR] 请使用 --corners 指定坐标，或使用 --interactive 交互选择")
        sys.exit(1)

    # 执行合成
    try:
        overlay_ppt(args.room, args.ppt, screen_corners, args.output, args.brightness)
    except Exception as e:
        print(f"[ERROR] 合成失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
