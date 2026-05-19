#!/usr/bin/env python3
"""
Wiki Metadata Fixer - 批量修复元数据 + 整理文件夹结构
"""
import os
import re
import shutil
from pathlib import Path

WIKI_ROOT = Path(r"E:\1.work\douyin\1.shuixing\Wiki知识库")
WIKI_DIR = WIKI_ROOT / "wiki"

def get_category_from_path(file_path: Path) -> str:
    """根据路径推断分类"""
    rel = file_path.relative_to(WIKI_DIR)
    parts = rel.parts
    if len(parts) > 1:
        return parts[0]
    return "根目录"

def extract_title(content: str) -> str:
    """从内容中提取标题"""
    match = re.match(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""

def generate_frontmatter(file_path: Path, content: str) -> dict:
    """生成frontmatter"""
    title = extract_title(content)
    category = get_category_from_path(file_path)

    tags = [category] if category != "根目录" else []

    rel = file_path.relative_to(WIKI_DIR)
    for part in rel.parts[:-1]:
        if part not in tags and part != "wiki":
            tags.append(part)

    fm = {
        "title": title or file_path.stem,
        "created": "2026-04-26",
        "updated": "2026-04-26",
        "tags": tags if tags else None,
        "aliases": None,
        "关联笔记": None,
    }
    return fm

def has_frontmatter(content: str) -> bool:
    """检查是否已有frontmatter"""
    return bool(re.match(r'^---\s*\n', content))

def add_frontmatter(content: str, fm: dict) -> str:
    """添加frontmatter到内容"""
    fm_lines = ["---"]
    for key, val in fm.items():
        if val is None:
            fm_lines.append(f"{key}: null")
        elif isinstance(val, list):
            fm_lines.append(f"{key}:")
            for item in val:
                fm_lines.append(f"  - \"{item}\"")
        else:
            fm_lines.append(f"{key}: \"{val}\"")
    fm_lines.append("---")
    fm_lines.append("")

    return "\n".join(fm_lines) + content

def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        content = file_path.read_text(encoding="utf-8")

        if has_frontmatter(content):
            return False

        fm = generate_frontmatter(file_path, content)
        new_content = add_frontmatter(content, fm)

        file_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  [ERROR] {file_path.name}: {e}")
        return False

def main():
    print("Wiki Metadata Fixer")
    print("=" * 60)

    # 1. 修复孤立文件夹：将 wiki\AI工具谱 移动到 wiki\工具与系统\AI工具谱
    orphan_ai_tools = WIKI_DIR / "AI工具谱"
    target_ai_tools = WIKI_DIR / "工具与系统" / "AI工具谱"

    if orphan_ai_tools.exists() and orphan_ai_tools.is_dir():
        print(f"\n[FIX] 修复孤立文件夹: {orphan_ai_tools.name}")
        if target_ai_tools.exists():
            for f in orphan_ai_tools.glob("*.md"):
                target = target_ai_tools / f.name
                if not target.exists():
                    shutil.copy2(f, target)
                    print(f"  [OK] 复制: {f.name} -> {target_ai_tools.name}/")
                else:
                    print(f"  [SKIP] 跳过(已存在): {f.name}")
            shutil.rmtree(orphan_ai_tools)
            print(f"  [DEL] 删除孤立文件夹: {orphan_ai_tools.name}")
        else:
            shutil.move(str(orphan_ai_tools), str(target_ai_tools))
            print(f"  [OK] 移动: {orphan_ai_tools} -> {target_ai_tools}")

    # 2. 修复重复选题库：删除 wiki\选题库（保留文案创作\选题库）
    orphan_topic = WIKI_DIR / "选题库"
    target_topic = WIKI_DIR / "文案创作" / "选题库"

    if orphan_topic.exists() and orphan_topic.is_dir():
        print(f"\n[FIX] 修复重复选题库: {orphan_topic.name}")
        for f in orphan_topic.glob("*.md"):
            target = target_topic / f.name
            if not target.exists():
                shutil.copy2(f, target)
                print(f"  [OK] 复制: {f.name} -> 文案创作/选题库/")
            else:
                print(f"  [SKIP] 跳过(已存在): {f.name}")
        shutil.rmtree(orphan_topic)
        print(f"  [DEL] 删除重复文件夹: {orphan_topic.name}")

    # 3. 批量添加 frontmatter
    print("\n[INFO] 批量添加元数据...")
    files_fixed = 0
    files_skipped = 0

    for md_file in WIKI_DIR.rglob("*.md"):
        if "node_modules" in str(md_file):
            continue

        if process_file(md_file):
            print(f"  [OK] {md_file.relative_to(WIKI_DIR)}")
            files_fixed += 1
        else:
            files_skipped += 1

    print(f"\n[STAT] 元数据统计:")
    print(f"  - 已添加: {files_fixed}")
    print(f"  - 已有/跳过: {files_skipped}")

    # 4. 整理 raw/ 散落文件
    print("\n[INFO] 检查 raw/ 文件夹结构...")
    raw_root = WIKI_ROOT / "raw"

    # raw/ 文件夹使用数字前缀命名法
    raw_loose_files = [
        ("0418-复盘报告-业务成果与工作流优化.md", "账号数据"),
        ("0418-宫崎骏作品集-数据诊断报告.md", "账号数据"),
        ("0418-版式之道爆款文案拆解报告.md", "账号数据"),
        ("0420-执行总结.md", "账号数据"),
        ("0420-流量低迷诊断报告.md", "账号数据"),
        ("DeepSeek-V4 预览版：迈入百万上下文普惠时代.md", "AI模型对比"),
        ("男士留长发完整指南-Perplexity搜索结果.md", "04_学习笔记"),
        ("视频管理.md", "06_媒体资源"),
    ]

    loose_moved = 0
    for f, dest_folder in raw_loose_files:
        src = raw_root / f
        if src.exists():
            dest_dir = raw_root / dest_folder
            dest_dir.mkdir(exist_ok=True)
            dest = dest_dir / f
            if not dest.exists():
                shutil.move(str(src), str(dest))
                print(f"  [OK] {f} -> {dest_folder}/")
                loose_moved += 1
            else:
                print(f"  [SKIP] 跳过(已存在): {f}")

    if loose_moved > 0:
        print(f"  [STAT] 已整理 {loose_moved} 个散落文件")
    else:
        print("  [OK] raw/ 文件夹结构正常")

    print("\n[DONE] 完成!")

if __name__ == "__main__":
    main()
