#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 批量转换为 Markdown
使用 Microsoft MarkItDown 工具
"""

import sys
import os
from pathlib import Path
from markitdown import MarkItDown

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

def convert_pdf_to_markdown(pdf_path, output_dir=None):
    """
    将 PDF 转换为 Markdown

    Args:
        pdf_path: PDF 文件路径
        output_dir: 输出目录（默认与 PDF 同目录）

    Returns:
        (success, output_path, error_message)
    """
    try:
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return False, None, f"文件不存在: {pdf_path}"

        if not pdf_path.suffix.lower() == '.pdf':
            return False, None, f"不是 PDF 文件: {pdf_path}"

        # 确定输出路径
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = pdf_path.parent

        output_path = output_dir / f"{pdf_path.stem}.md"

        # 转换
        print(f"正在转换: {pdf_path.name}")
        md = MarkItDown()
        result = md.convert(str(pdf_path))

        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.text_content)

        print(f"✓ 转换成功: {output_path.name}")
        return True, output_path, None

    except Exception as e:
        error_msg = f"转换失败: {str(e)}"
        print(f"✗ {error_msg}")
        return False, None, error_msg


def batch_convert_pdfs(input_dir, output_dir=None, recursive=True):
    """
    批量转换目录中的所有 PDF

    Args:
        input_dir: 输入目录
        output_dir: 输出目录（默认与 PDF 同目录）
        recursive: 是否递归子目录

    Returns:
        (success_count, fail_count, results)
    """
    input_dir = Path(input_dir)

    if not input_dir.exists():
        print(f"目录不存在: {input_dir}")
        return 0, 0, []

    # 查找所有 PDF
    if recursive:
        pdf_files = list(input_dir.rglob("*.pdf"))
    else:
        pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"未找到 PDF 文件: {input_dir}")
        return 0, 0, []

    print(f"\n找到 {len(pdf_files)} 个 PDF 文件")
    print("=" * 60)

    results = []
    success_count = 0
    fail_count = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")

        # 如果指定了输出目录，保持相对路径结构
        if output_dir:
            rel_path = pdf_path.relative_to(input_dir)
            out_dir = Path(output_dir) / rel_path.parent
        else:
            out_dir = None

        success, output_path, error = convert_pdf_to_markdown(pdf_path, out_dir)

        results.append({
            'input': str(pdf_path),
            'output': str(output_path) if output_path else None,
            'success': success,
            'error': error
        })

        if success:
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"\n转换完成:")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")

    return success_count, fail_count, results


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  单个文件: python pdf_to_markdown.py <pdf文件路径>")
        print("  批量转换: python pdf_to_markdown.py <目录路径> [输出目录]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    input_path = Path(input_path)

    if input_path.is_file():
        # 单个文件
        success, output_path, error = convert_pdf_to_markdown(input_path, output_dir)
        if success:
            print(f"\n输出文件: {output_path}")
        else:
            print(f"\n错误: {error}")
            sys.exit(1)

    elif input_path.is_dir():
        # 批量转换
        success_count, fail_count, results = batch_convert_pdfs(input_path, output_dir)

        if fail_count > 0:
            print("\n失败的文件:")
            for r in results:
                if not r['success']:
                    print(f"  - {Path(r['input']).name}: {r['error']}")

    else:
        print(f"路径不存在: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
