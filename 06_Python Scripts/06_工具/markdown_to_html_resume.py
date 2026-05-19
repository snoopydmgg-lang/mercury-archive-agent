#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 HTML 简历生成器（浏览器打印版）
生成可在浏览器中打开并打印为 PDF 的 HTML 文件
"""

import sys
import os
import argparse
from pathlib import Path
import markdown

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def markdown_to_html(md_content):
    """将 Markdown 转换为 HTML"""
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
    ]
    html_content = markdown.markdown(md_content, extensions=extensions)
    return html_content

def create_standalone_html(body_html):
    """创建独立的 HTML 文档（内嵌 CSS）"""
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贺杉 - 简历</title>
    <style>
        @page {
            size: A4;
            margin: 2cm 2.5cm;
        }

        @media print {
            @page {
                margin: 2cm 2.5cm;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #FFFFFF;
            color: #2D2B2A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, "Microsoft YaHei", sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
        }

        /* 照片样式 */
        img {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 120px;
            height: 160px;
            object-fit: cover;
            border: 1px solid #d0d0d0;
        }

        h1 {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 28pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8pt;
            letter-spacing: 0.5pt;
        }

        h2 {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 14pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-top: 20pt;
            margin-bottom: 10pt;
            padding-bottom: 4pt;
            border-bottom: 2px solid #2D2B2A;
        }

        h3 {
            font-size: 12pt;
            font-weight: 700;
            color: #2D2B2A;
            margin-top: 12pt;
            margin-bottom: 6pt;
        }

        p {
            margin-bottom: 8pt;
        }

        strong {
            font-weight: 600;
            color: #1a1a1a;
        }

        ul {
            margin-left: 20pt;
            margin-bottom: 10pt;
        }

        li {
            margin-bottom: 4pt;
            line-height: 1.5;
        }

        hr {
            border: none;
            border-top: 1px solid #d0d0d0;
            margin: 16pt 0;
        }

        h1 + p {
            font-size: 10pt;
            color: #666;
            margin-bottom: 4pt;
        }

        h3 + p strong {
            font-weight: 600;
            color: #555;
        }

        a {
            color: #2D2B2A;
            text-decoration: none;
        }

        h2, h3 {
            page-break-after: avoid;
        }

        li {
            page-break-inside: avoid;
        }

        @media print {
            body {
                padding: 0;
            }
        }

        .print-instructions {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #2D2B2A;
        }

        @media print {
            .print-instructions {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="print-instructions">
        <strong>打印说明：</strong>按 Ctrl+P（或 Cmd+P）打开打印对话框，选择"另存为 PDF"即可保存为 PDF 文件。
    </div>
    """ + body_html + """
</body>
</html>"""
    return html_template

def convert_markdown_to_html(input_path, output_path):
    """将 Markdown 文件转换为独立 HTML"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        body_html = markdown_to_html(md_content)
        full_html = create_standalone_html(body_html)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

        print(f"✓ HTML 生成成功: {output_path}")
        print(f"\n使用方法：")
        print(f"1. 在浏览器中打开: {output_path}")
        print(f"2. 按 Ctrl+P（Windows）或 Cmd+P（Mac）")
        print(f"3. 选择 '另存为 PDF'")
        print(f"4. 保存为: 贺杉简历-精简版2.pdf")
        return True

    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='将 Markdown 简历转换为 HTML（可打印为 PDF）')
    parser.add_argument('--input', '-i', required=True, help='输入 Markdown 文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出 HTML 文件路径')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"✗ 输入文件不存在: {args.input}")
        sys.exit(1)

    print(f"正在转换: {args.input}")
    success = convert_markdown_to_html(args.input, args.output)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
