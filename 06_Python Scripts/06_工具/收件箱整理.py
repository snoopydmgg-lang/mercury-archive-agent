#!/usr/bin/env python3
"""
收件箱整理脚本
功能：
1. 为文件名添加修改日期后缀
2. 按文件名规则自动分类到对应目录
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================
INBOX_DIR = Path(r"E:\1.work\douyin\1.shuixing\00_InBox_收件箱")
DATA_DIR = Path(r"E:\1.work\douyin\1.shuixing\04_数据分析结果")
PROJECTS_DIR = Path(r"E:\1.work\douyin\1.shuixing\01_Projects_制作中")

# ==================== 分类规则 ====================
# 格式: (文件名关键字, 目标目录, 说明)
CLASSIFY_RULES = [
    ("达人监测", DATA_DIR / "达人监测", "达人监测数据"),
    ("抖音数据", DATA_DIR / "抖音数据", "抖音数据"),
    ("水星艺术馆", DATA_DIR / "水星艺术馆", "水星艺术馆"),
    ("数据表现", DATA_DIR / "数据表现", "数据表现"),
    ("作品列表", DATA_DIR / "作品列表", "作品列表"),
    ("data", DATA_DIR / "data", "data文件"),
    # Word 文档移到项目文件夹
    (".docx", PROJECTS_DIR, "Word文档"),
    (".doc", PROJECTS_DIR, "Word文档"),
    # 文本文件
    (".txt", PROJECTS_DIR, "文本文件"),
    (".md", PROJECTS_DIR, "文本文件"),
]

# ==================== 函数 ====================

def get_file_mtime(file_path: Path) -> str:
    """获取文件修改日期，格式为 YYYYMMDD"""
    timestamp = file_path.stat().st_mtime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y%m%d")

def add_date_to_filename(file_path: Path) -> Path:
    """为文件名添加日期后缀（如果还没有日期的话）"""
    stem = file_path.stem
    suffix = file_path.suffix

    # 检查是否已经包含日期格式 (8位数字如 20260313)
    if any(char.isdigit() for char in stem):
        # 简单检查：如果末尾有长数字，认为已有日期
        import re
        if re.search(r'\d{8}$', stem):
            return file_path  # 已有日期，不处理

    # 获取修改日期
    date_str = get_file_mtime(file_path)

    # 新文件名: 原名_日期.扩展名
    new_stem = f"{stem}_{date_str}"
    new_name = f"{new_stem}{suffix}"
    new_path = file_path.parent / new_name

    # 如果新文件名已存在，加个计数器
    if new_path.exists():
        counter = 1
        while new_path.exists():
            new_stem = f"{stem}_{date_str}_{counter}"
            new_name = f"{new_stem}{suffix}"
            new_path = file_path.parent / new_name
            counter += 1

    # 重命名文件
    file_path.rename(new_path)
    print(f"  [重命名] {file_path.name} -> {new_name}")
    return new_path

def classify_file(file_path: Path) -> tuple:
    """根据规则对文件进行分类"""
    filename = file_path.name

    # 跳过临时文件
    if filename.startswith("~$"):
        return "DELETE", "Windows临时文件"

    # 按规则匹配
    for keyword, target_dir, description in CLASSIFY_RULES:
        if filename.startswith(keyword) or keyword in filename:
            return target_dir, description

    return None, "未匹配规则"

def process_file(file_path: Path) -> bool:
    """处理单个文件：添加日期 + 分类"""
    print(f"\n处理: {file_path.name}")

    # 第1步：添加日期到文件名
    try:
        file_path = add_date_to_filename(file_path)
    except Exception as e:
        print(f"  [错误] 添加日期失败: {e}")
        return False

    # 第2步：分类
    target_dir, description = classify_file(file_path)

    if target_dir == "DELETE":
        print(f"  [删除] {description}")
        try:
            file_path.unlink()
            return True
        except Exception as e:
            print(f"  [错误] 删除失败: {e}")
            return False

    if target_dir is None:
        print(f"  [跳过] {description}")
        return False

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    dest = target_dir / file_path.name

    # 处理文件名冲突
    if dest.exists():
        base = file_path.stem
        suffix = file_path.suffix
        counter = 1
        while dest.exists():
            dest = target_dir / f"{base}_{counter}{suffix}"
            counter += 1

    # 移动文件
    try:
        shutil.move(str(file_path), str(dest))
        print(f"  [移动] -> {target_dir.name}/{dest.name}")
        return True
    except Exception as e:
        print(f"  [错误] 移动失败: {e}")
        return False

def main():
    print("=" * 60)
    print("收件箱整理脚本")
    print("功能：1. 为文件名添加修改日期  2. 按文件名分类")
    print("=" * 60)
    print(f"\n收件箱: {INBOX_DIR}\n")

    if not INBOX_DIR.exists():
        print(f"[错误] 收件箱目录不存在: {INBOX_DIR}")
        return

    # 获取收件箱中的所有文件（排除目录和协议文件）
    files = [
        f for f in INBOX_DIR.iterdir()
        if f.is_file() and not f.name.endswith(".ini") and not f.name.endswith(".md")
    ]

    if not files:
        print("收件箱已是空的，无需整理。")
        return

    print(f"发现 {len(files)} 个文件待处理\n")

    stats = {"success": 0, "deleted": 0, "skipped": 0}

    for file_path in files:
        if process_file(file_path):
            if file_path.name.startswith("~$"):
                stats["deleted"] += 1
            else:
                stats["success"] += 1
        else:
            stats["skipped"] += 1

    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"  成功分类: {stats['success']} 个文件")
    print(f"  已删除:   {stats['deleted']} 个文件")
    print(f"  跳过:     {stats['skipped']} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
