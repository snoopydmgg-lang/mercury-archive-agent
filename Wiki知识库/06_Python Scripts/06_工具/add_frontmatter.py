#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动为 wiki 文件添加 Frontmatter 元数据
"""

import os
import re
from pathlib import Path
from datetime import datetime

WIKI_ROOT = Path(r"E:\1.work\douyin\1.shuixing\Wiki知识库\wiki")

def has_frontmatter(content):
    """检查文件是否已有 Frontmatter"""
    return content.strip().startswith('---')

def extract_title(content):
    """从内容中提取标题"""
    # 尝试提取第一个 # 标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def generate_tags(file_path):
    """根据文件路径生成标签"""
    tags = []
    parts = file_path.parts

    # 从路径提取分类标签
    if '文案创作' in parts:
        tags.append('文案创作')
    if '视频制作' in parts:
        tags.append('视频制作')
    if '工具与系统' in parts:
        tags.append('工具与系统')
    if '个人' in parts:
        tags.append('个人成长')

    # 从文件名提取关键词
    filename = file_path.stem
    if 'AI' in filename or 'ai' in filename.lower():
        tags.append('AI')
    if '知识库' in filename:
        tags.append('知识库')
    if '围棋' in filename:
        tags.append('围棋')
    if '博主' in filename or '文案' in filename:
        tags.append('文案参考')

    return tags if tags else ['待分类']

def generate_aliases(title):
    """生成别名"""
    if not title:
        return []

    aliases = []
    # 如果标题很长，生成简短别名
    if len(title) > 15:
        # 提取关键词
        keywords = re.findall(r'[\u4e00-\u9fa5]+', title)
        if keywords:
            aliases.append(keywords[0])

    return aliases

def create_frontmatter(file_path, content):
    """创建 Frontmatter"""
    title = extract_title(content)
    if not title:
        title = file_path.stem

    tags = generate_tags(file_path)
    aliases = generate_aliases(title)

    frontmatter = "---\n"
    frontmatter += f"title: {title}\n"
    frontmatter += "tags:\n"
    for tag in tags:
        frontmatter += f"  - {tag}\n"

    if aliases:
        frontmatter += "aliases:\n"
        for alias in aliases:
            frontmatter += f"  - {alias}\n"

    frontmatter += "关联笔记: []\n"
    frontmatter += f"录入日期: {datetime.now().strftime('%Y-%m-%d')}\n"
    frontmatter += "---\n\n"

    return frontmatter

def process_file(file_path):
    """处理单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if has_frontmatter(content):
            return False, "已有 Frontmatter"

        # 跳过特殊文件
        if file_path.name in ['README.md', 'index.md', 'log.md']:
            return False, "特殊文件，跳过"

        frontmatter = create_frontmatter(file_path, content)
        new_content = frontmatter + content

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True, "已添加 Frontmatter"

    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    import sys
    import io

    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("扫描 wiki 目录...")

    md_files = list(WIKI_ROOT.rglob("*.md"))
    print(f"找到 {len(md_files)} 个 Markdown 文件")

    processed = 0
    skipped = 0
    errors = 0

    for file_path in md_files:
        success, message = process_file(file_path)

        if success:
            processed += 1
            rel_path = file_path.relative_to(WIKI_ROOT)
            print(f"[OK] {rel_path}")
        else:
            if "错误" in message:
                errors += 1
                print(f"[ERROR] {file_path.name}: {message}")
            else:
                skipped += 1

    print("\n" + "="*60)
    print(f"处理完成:")
    print(f"  - 已处理: {processed} 个文件")
    print(f"  - 已跳过: {skipped} 个文件")
    print(f"  - 错误: {errors} 个文件")
    print("="*60)

if __name__ == "__main__":
    main()
