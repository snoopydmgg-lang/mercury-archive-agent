#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析工具脚本与 Skills 的集成情况
"""

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 工具脚本目录
tools_dir = Path("E:/1.work/douyin/1.shuixing/06_Python Scripts/06_工具")
skills_dir = Path("C:/Users/Administrator/.claude/skills")

# 获取所有工具脚本
tools = [f.stem for f in tools_dir.glob("*.py")]
tools.sort()

# 获取所有 Skills
skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
skills.sort()

# 已集成的工具（根据命名推断）
integrated = []
not_integrated = []

# 工具到 Skill 的映射关系
tool_skill_mapping = {
    'wiki_lint': 'wiki-manager',
    'wiki_lint_obsidian': 'wiki-manager',
    'wiki_moc_generator': 'wiki-manager',
    'batch_classify_notes': 'wiki-manager',
    'ccswitch_cli': 'ccswitch',
    'video_analyzer': 'video-folder-workflow',
    'ics_generator': 'ics-schedule',
    'habit_tracker': 'tomato-todo',
    'docx_to_md': 'wiki-manager',
    'pdf_to_markdown': 'wiki-manager',
    'clean_zhihu_md': None,  # 未集成
    'dropit': 'folder-organizer',
    'extract_screen_content': None,
    'generate_avatar': None,
    'generate_cover_grid': 'cover-generator',
    'generate_cover_with_asset': 'cover-generator',
    'generate_standard_cover': 'cover-generator',
    'generate_fractal_final': 'cover-generator',
    'generate_fractal_variants': 'cover-generator',
    'generate_bird_fractal': 'cover-generator',
    'generate_bold_fractal': 'cover-generator',
    'generate_claude_fractal': 'cover-generator',
    'inject_bold_asset': 'cover-generator',
    'inject_fractal_asset': 'cover-generator',
    'render_cover_patch': 'cover-generator',
    'render_cover_text': 'cover-generator',
    'image_organizer': 'folder-organizer',
    'notion_to_obsidian': None,
    'openrouter_pricing': 'openrouter-agent',
    'parse_feishu_records': 'lark-base',
    'ppt_overlay': None,
    'download_covers': None,
}

# 分类
for tool in tools:
    skill = tool_skill_mapping.get(tool)
    if skill and skill in skills:
        integrated.append((tool, skill))
    else:
        not_integrated.append((tool, skill))

# 生成报告
print("=" * 80)
print("工具脚本与 Skills 集成情况分析")
print("=" * 80)
print()

print(f"📊 统计概览")
print(f"  - 工具脚本总数: {len(tools)} 个")
print(f"  - Skills 总数: {len(skills)} 个")
print(f"  - 已集成: {len(integrated)} 个")
print(f"  - 未集成: {len(not_integrated)} 个")
print()

print("=" * 80)
print("✅ 已集成的工具")
print("=" * 80)
print()

for tool, skill in integrated:
    print(f"  {tool}.py → {skill}")

print()
print("=" * 80)
print("❌ 未集成的工具")
print("=" * 80)
print()

for tool, skill in not_integrated:
    if skill:
        print(f"  {tool}.py → {skill} (Skill 不存在)")
    else:
        print(f"  {tool}.py → (未映射)")

print()
print("=" * 80)
print("💡 集成建议")
print("=" * 80)
print()

# 按功能分类未集成的工具
categories = {
    '文档处理': ['clean_zhihu_md', 'notion_to_obsidian'],
    '图像处理': ['extract_screen_content', 'generate_avatar', 'ppt_overlay'],
    '资源管理': ['download_covers'],
}

for category, tools_list in categories.items():
    matching = [t for t, _ in not_integrated if t in tools_list]
    if matching:
        print(f"【{category}】")
        for tool in matching:
            print(f"  - {tool}.py")
        print()
