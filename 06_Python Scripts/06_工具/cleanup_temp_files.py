"""
临时文件垃圾回收脚本
自动清理根目录和收件箱的临时文件
"""
import os
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 清理规则配置
CLEANUP_RULES = {
    "root": {
        "path": BASE_DIR,
        "patterns": [
            "*.log",
            "*.tmp",
            "temp_*.txt",
            "output*.txt",
            "*.bat"  # 临时批处理文件
        ],
        "whitelist": [
            ".git",
            ".claude",
            ".obsidian",
            ".vscode",
            "CLAUDE.md",
            "memory"
        ]
    },
    "inbox": {
        "path": BASE_DIR / "00_InBox_收件箱",
        "patterns": [
            "*.json",  # Obsidian 配置文件
            "*.py"     # 临时脚本
        ],
        "whitelist": [],
        "age_days": 2  # 只清理 2 天前的文件
    }
}

def get_file_size(filepath):
    """获取文件大小（KB）"""
    try:
        return os.path.getsize(filepath) / 1024
    except:
        return 0

def should_clean(filepath, rule):
    """判断文件是否应该被清理"""
    filename = os.path.basename(filepath)

    # 检查白名单
    if filename in rule.get("whitelist", []):
        return False

    # 检查文件年龄
    if "age_days" in rule:
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            age = datetime.now() - file_time
            if age.days < rule["age_days"]:
                return False
        except:
            return False

    return True

def scan_directory(rule_name, rule, dry_run=True):
    """扫描目录并收集待清理文件"""
    path = rule["path"]
    patterns = rule["patterns"]

    if not path.exists():
        print(f"  ⚠ 目录不存在: {path}")
        return []

    files_to_clean = []

    for pattern in patterns:
        for filepath in path.glob(pattern):
            # 只处理文件，不处理目录
            if not filepath.is_file():
                continue

            # 跳过子目录中的文件（只清理根目录）
            if rule_name == "root" and filepath.parent != path:
                continue

            # 检查是否应该清理
            if should_clean(filepath, rule):
                files_to_clean.append(filepath)

    return files_to_clean

def format_size(size_kb):
    """格式化文件大小"""
    if size_kb < 1:
        return f"{size_kb * 1024:.0f} B"
    elif size_kb < 1024:
        return f"{size_kb:.1f} KB"
    else:
        return f"{size_kb / 1024:.1f} MB"

def format_age(filepath):
    """格式化文件年龄"""
    try:
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        age = datetime.now() - file_time
        if age.days == 0:
            return "今天"
        elif age.days == 1:
            return "1 天前"
        else:
            return f"{age.days} 天前"
    except:
        return "未知"

def main(execute=False):
    """主函数"""
    print("=" * 70)
    print("临时文件垃圾回收扫描")
    print("=" * 70)
    print()

    all_files = []
    total_size = 0

    # 扫描所有规则
    for idx, (rule_name, rule) in enumerate(CLEANUP_RULES.items(), 1):
        print(f"[{idx}/{len(CLEANUP_RULES)}] 扫描{rule_name}...")

        files = scan_directory(rule_name, rule, dry_run=not execute)

        if files:
            print(f"  发现 {len(files)} 个{'待清理' if rule_name == 'inbox' else '临时'}文件：")
            for f in files:
                size = get_file_size(f)
                age = format_age(f) if rule_name == "inbox" else ""
                age_str = f" ({age}, {format_size(size)})" if age else f" ({format_size(size)})"
                print(f"    - {f.name}{age_str}")
                total_size += size
            all_files.extend(files)
        else:
            print(f"  ✓ 无需清理")
        print()

    # 总结
    print("=" * 70)
    print(f"总计：{len(all_files)} 个文件，{format_size(total_size)}")
    print("=" * 70)
    print()

    # 执行清理
    if execute:
        if not all_files:
            print("✓ 没有需要清理的文件")
            return

        print("开始清理...")
        success_count = 0
        fail_count = 0

        for filepath in all_files:
            try:
                os.remove(filepath)
                print(f"  ✓ 已删除: {filepath.name}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ 删除失败: {filepath.name} ({e})")
                fail_count += 1

        print()
        print(f"清理完成：成功 {success_count} 个，失败 {fail_count} 个")
    else:
        print("预览模式：未执行删除操作")
        print(f"如需执行删除，请运行：python {Path(__file__).name} --execute")

    print()

if __name__ == "__main__":
    # 检查命令行参数
    execute = "--execute" in sys.argv
    main(execute=execute)
