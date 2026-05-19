#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Chrome Headless 将 HTML 转换为 PDF
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def find_chrome():
    """查找 Chrome 可执行文件路径"""
    possible_paths = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def html_to_pdf_chrome(html_path, pdf_path):
    """使用 Chrome Headless 将 HTML 转换为 PDF"""
    chrome_path = find_chrome()

    if not chrome_path:
        print("错误: 未找到 Chrome 浏览器")
        return False

    # 转换为绝对路径
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)

    # 构建 Chrome 命令
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=" + pdf_path,
        "--no-margins",
        "--print-to-pdf-no-header",
        "file:///" + html_path.replace("\\", "/")
    ]

    try:
        print(f"正在使用 Chrome 生成 PDF...")
        print(f"输入: {html_path}")
        print(f"输出: {pdf_path}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024
            print(f"✓ PDF 生成成功")
            print(f"文件大小: {file_size:.1f} KB")
            return True
        else:
            print(f"错误: PDF 文件未生成")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("错误: Chrome 执行超时")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='使用 Chrome 将 HTML 转换为 PDF')
    parser.add_argument('--input', '-i', required=True, help='输入 HTML 文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出 PDF 文件路径')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)

    success = html_to_pdf_chrome(args.input, args.output)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
