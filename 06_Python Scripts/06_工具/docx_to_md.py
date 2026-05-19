#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 文档批量转换为 Markdown
使用 mammoth 库转换 .doc/.docx 文件
"""

import os
import sys
import mammoth
from pathlib import Path

def convert_docx_to_md(docx_path, output_dir=None):
    """
    转换单个 Word 文档为 Markdown

    Args:
        docx_path: Word 文档路径
        output_dir: 输出目录（默认与源文件同目录）

    Returns:
        转换后的 MD 文件路径
    """
    docx_path = Path(docx_path)

    if not docx_path.exists():
        print(f"[ERROR] 文件不存在: {docx_path}")
        return None

    # 确定输出路径
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / f"{docx_path.stem}.md"
    else:
        md_path = docx_path.with_suffix('.md')

    try:
        # 转换文档
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown_content = result.value

            # 添加文件头
            header = f"# {docx_path.stem}\n\n"
            header += f"> 原始文件：{docx_path.name}\n\n"
            header += "---\n\n"

            full_content = header + markdown_content

            # 写入 MD 文件
            with open(md_path, 'w', encoding='utf-8') as md_file:
                md_file.write(full_content)

            print(f"[SUCCESS] {docx_path.name} -> {md_path.name}")

            # 显示警告信息
            if result.messages:
                for message in result.messages:
                    print(f"  [WARNING] {message}")

            return md_path

    except Exception as e:
        print(f"[ERROR] 转换失败 {docx_path.name}: {e}")
        return None


def batch_convert(root_dir, delete_original=False):
    """
    批量转换目录下所有 Word 文档

    Args:
        root_dir: 根目录
        delete_original: 是否删除原始文件
    """
    root_dir = Path(root_dir)

    # 查找所有 Word 文档
    doc_files = list(root_dir.rglob("*.doc")) + list(root_dir.rglob("*.docx"))

    if not doc_files:
        print("[INFO] 未找到 Word 文档")
        return

    print(f"[INFO] 找到 {len(doc_files)} 个 Word 文档\n")

    success_count = 0
    fail_count = 0

    for doc_file in doc_files:
        md_path = convert_docx_to_md(doc_file)

        if md_path:
            success_count += 1

            # 删除原始文件
            if delete_original:
                try:
                    doc_file.unlink()
                    print(f"  [DELETE] 已删除原始文件: {doc_file.name}")
                except Exception as e:
                    print(f"  [ERROR] 删除失败: {e}")
        else:
            fail_count += 1

    print(f"\n[SUMMARY] 成功: {success_count}, 失败: {fail_count}")


if __name__ == "__main__":
    # 知识库路径
    wiki_root = Path(r"E:\1.work\douyin\1.shuixing\Wiki知识库\raw")

    # 批量转换（不删除原始文件）
    batch_convert(wiki_root, delete_original=False)
