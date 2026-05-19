#!/usr/bin/env python3
"""
Markdown 转 PDF 简历生成器
使用 weasyprint 将 Markdown 简历转换为专业 PDF
"""

import sys
import os
import argparse
from pathlib import Path
import markdown
from weasyprint import HTML, CSS

def markdown_to_html(md_content):
    """将 Markdown 转换为 HTML"""
    # 配置 markdown 扩展
    extensions = [
        'markdown.extensions.extra',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
    ]

    html_content = markdown.markdown(md_content, extensions=extensions)
    return html_content

def create_full_html(body_html, css_path):
    """创建完整的 HTML 文档"""
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简历</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
    {body_html}
</body>
</html>"""
    return html_template

def convert_markdown_to_pdf(input_path, output_path, css_path):
    """将 Markdown 文件转换为 PDF"""
    try:
        # 读取 Markdown 文件
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 转换为 HTML
        body_html = markdown_to_html(md_content)

        # 创建完整 HTML
        full_html = create_full_html(body_html, css_path)

        # 转换为 PDF
        html = HTML(string=full_html, base_url=str(Path(input_path).parent))
        html.write_pdf(output_path)

        print(f"✓ PDF 生成成功: {output_path}")
        return True

    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='将 Markdown 简历转换为 PDF')
    parser.add_argument('--input', '-i', required=True, help='输入 Markdown 文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出 PDF 文件路径')
    parser.add_argument('--css', '-c', help='CSS 样式表路径（可选）')

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"✗ 输入文件不存在: {args.input}")
        sys.exit(1)

    # 确定 CSS 路径
    if args.css:
        css_path = args.css
    else:
        # 使用默认 CSS（与脚本同目录）
        script_dir = Path(__file__).parent
        css_path = script_dir / "resume_style.css"

    if not os.path.exists(css_path):
        print(f"✗ CSS 文件不存在: {css_path}")
        sys.exit(1)

    # 转换
    print(f"正在转换: {args.input}")
    print(f"使用样式: {css_path}")

    success = convert_markdown_to_pdf(args.input, args.output, css_path)

    if success:
        file_size = os.path.getsize(args.output) / 1024
        print(f"文件大小: {file_size:.1f} KB")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
