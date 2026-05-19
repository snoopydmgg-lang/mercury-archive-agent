"""Bulk DBS fixes: remove AI-flavor words, reduce 主任 density, trim filler phrases."""
from pathlib import Path
import re

OUTPUT_DIR = Path("output")
FILES = [
    "1_全面机制升维_逐页演讲稿.md",
    "2_机制突破_逐页演讲稿.md",
    "3_疗效升维_逐页演讲稿.md",
    "4_安全革新_逐页演讲稿.md",
]

# Category 1: Remove/Replace AI-flavor filler words
AI_FILLER = [
    (r'简单来说[：:]?\s*', ''),
    (r'可以说[，,]?\s*', ''),
    (r'可以这么理解[：:]?\s*', ''),
    (r'换句话说[，,]?\s*', ''),
    (r'值得关注的是[，,]?\s*', ''),
    (r'这一点值得关注[。.]?', ''),
    (r'非常值得关注[。.]?', ''),
    (r'一个值得关注的信号[。.]?', ''),
    (r'在临床上特别值得关注[，。,.]?', ''),
    (r'非常值得关注', '值得留意'),
    (r'非常独特[、，]?', ''),
]

# Category 2: Reduce 主任 density - but this needs per-page context, skip in script
# We'll handle this in agent rewrites

# Category 3: Trim transition pages - mark them for agent
# Category 4: Fix 沟通引导句 patterns

def fix_file(filepath):
    text = filepath.read_text(encoding="utf-8")

    # Apply AI filler removal
    for pattern, replacement in AI_FILLER:
        text = re.sub(pattern, replacement, text)

    # Remove duplicate newlines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix trailing spaces
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)

    filepath.write_text(text, encoding="utf-8")
    return True

def main():
    for fname in FILES:
        fpath = OUTPUT_DIR / fname
        if fpath.exists():
            fix_file(fpath)
            print(f"Fixed: {fname}")

    print("\nBulk fixes done. Nuanced rewrites need agents.")

if __name__ == "__main__":
    main()
