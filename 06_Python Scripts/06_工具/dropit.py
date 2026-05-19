#!/usr/bin/env python3
"""
DROPIT 协议 - 收件箱自动分类脚本

根据文件类型和特征自动将收件箱中的文件分类到对应目录
"""

import os
import shutil
from pathlib import Path

# 配置路径
INBOX_DIR = Path(r"E:\1.work\douyin\1.shuixing\00_InBox_收件箱")
DATA_ANALYSIS_DIR = Path(r"E:\1.work\douyin\1.shuixing\04_数据分析结果")
PROJECTS_DIR = Path(r"E:\1.work\douyin\1.shuixing\01_Projects_制作中")

# 分类规则
RULES = [
    # (条件函数, 目标目录, 说明)
    (lambda f: f.name.startswith("~$"), "DELETE", "Windows临时文件"),
    (lambda f: f.suffix.lower() in [".xlsx", ".xls"], DATA_ANALYSIS_DIR, "Excel数据文件"),
    (lambda f: f.suffix.lower() == ".pdf", DATA_ANALYSIS_DIR, "PDF分析报告"),
    (lambda f: f.suffix.lower() in [".docx", ".doc"], PROJECTS_DIR, "Word文档"),
    (lambda f: f.suffix.lower() in [".txt", ".md"], PROJECTS_DIR, "文本文件"),
]


def classify_file(file_path: Path) -> tuple:
    """根据规则对文件进行分类"""
    for rule, target, description in RULES:
        if rule(file_path):
            return target, description
    return None, "未匹配规则"


def move_file(src: Path, target_dir: Path) -> bool:
    """移动文件到目标目录"""
    if target_dir == "DELETE":
        print(f"  [删除] {src.name}")
        try:
            src.unlink()
            return True
        except Exception as e:
            print(f"  [错误] 删除失败: {e}")
            return False

    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)

    dest = target_dir / src.name

    # 处理文件名冲突
    if dest.exists():
        base = src.stem
        suffix = src.suffix
        counter = 1
        while dest.exists():
            dest = target_dir / f"{base}_{counter}{suffix}"
            counter += 1

    try:
        shutil.move(str(src), str(dest))
        print(f"  [移动] {src.name} -> {dest.parent.name}/{dest.name}")
        return True
    except Exception as e:
        print(f"  [错误] 移动失败: {e}")
        return False


def main():
    print("=" * 50)
    print("DROPIT 协议 - 收件箱自动分类")
    print("=" * 50)
    print(f"\n收件箱: {INBOX_DIR}\n")

    if not INBOX_DIR.exists():
        print(f"[错误] 收件箱目录不存在: {INBOX_DIR}")
        return

    # 获取收件箱中的所有文件
    files = [f for f in INBOX_DIR.iterdir() if f.is_file()]

    if not files:
        print("收件箱已是空的，无需整理。")
        return

    print(f"发现 {len(files)} 个文件待处理:\n")

    stats = {"moved": 0, "deleted": 0, "skipped": 0}

    for file_path in files:
        target, description = classify_file(file_path)

        if target is None:
            print(f"  [跳过] {file_path.name} (未匹配规则)")
            stats["skipped"] += 1
            continue

        print(f"处理: {file_path.name}")
        print(f"  原因: {description}")

        if move_file(file_path, target):
            if target == "DELETE":
                stats["deleted"] += 1
            else:
                stats["moved"] += 1
        else:
            stats["skipped"] += 1

    print("\n" + "=" * 50)
    print("处理完成!")
    print(f"  已移动: {stats['moved']} 个文件")
    print(f"  已删除: {stats['deleted']} 个文件")
    print(f"  跳过:   {stats['skipped']} 个文件")
    print("=" * 50)


if __name__ == "__main__":
    main()
