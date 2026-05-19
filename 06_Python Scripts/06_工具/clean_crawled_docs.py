"""
清洗爬取的 AI 文档 v2：
1. DeepSeek: 逐行修复双重编码乱码（UTF-8→Latin-1→UTF-8）
2. MiMo: 去侧边栏/CSS/JS/页脚/面包屑
3. Kimi: 去促销banner/CSS/JS/导航/页脚
"""
import re
from pathlib import Path

BASE = Path(r"E:\1.work\douyin\1.shuixing\Wiki知识库\raw\AI模型对比")

# ============================================================
# DeepSeek: line-by-line double-encoding fix
# ============================================================
def fix_deepseek_text(text: str) -> str:
    """Fix garbled Chinese: each line where all chars are <= U+FF
    is treated as Latin-1-misinterpreted UTF-8."""
    lines = text.split('\n')
    fixed_lines = []
    changed = False
    for line in lines:
        if not line:
            fixed_lines.append(line)
            continue
        # If any char has ordinal > 255, this line has correct non-Latin-1 text
        has_wide = any(ord(c) > 0xFF for c in line)
        if has_wide:
            fixed_lines.append(line)
        else:
            try:
                recovered = line.encode('latin-1').decode('utf-8')
                if recovered != line:
                    changed = True
                fixed_lines.append(recovered)
            except (UnicodeEncodeError, UnicodeDecodeError):
                fixed_lines.append(line)
    return '\n'.join(fixed_lines)


# ============================================================
# MiMo cleanup
# ============================================================
# The sidebar nav block is identical across all pages.
# We can detect it by finding the dense cluster of [/docs/...] links.
MIMO_SIDEBAR_START = re.compile(r'^\[欢迎使用\]\(/docs/zh-CN/welcome\)\s*$')
MIMO_SIDEBAR_END = re.compile(r'^\[隐私政策\]\(/docs/terms/privacy-policy\)\s*$')
MIMO_NAV_LINK = re.compile(r'^\[.*?\]\(/docs/(?:zh-CN/)?[\w\-]+\)\s*$')


def clean_mimo(text: str) -> str:
    lines = text.split('\n')
    result = []

    # Phase 1: find and remove the sidebar block
    sidebar_start_idx = None
    sidebar_end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if MIMO_SIDEBAR_START.match(stripped):
            sidebar_start_idx = i
        if sidebar_start_idx is not None and MIMO_SIDEBAR_END.match(stripped):
            sidebar_end_idx = i
            break

    # Build filtered lines
    skip_until = None
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip sidebar block
        if sidebar_start_idx is not None and sidebar_end_idx is not None:
            if sidebar_start_idx <= i <= sidebar_end_idx:
                continue

        # Skip surrounding junk around sidebar
        if stripped == 'Ctrl':
            continue
        if stripped == '往期新闻':
            continue
        if stripped == '开发者交流群':
            continue
        if stripped.startswith('[免费体验 MiMo Claw'):
            continue
        # Orphaned promo text: "HOT](https://...)"
        if stripped.startswith('HOT](https://'):
            continue
        # Breadcrumb: "1. [text](/docs/...)" or "3. Section Name" or "5. Page Name"
        if re.match(r'^\d+\.\s*\[.*\]\(/docs/', stripped):
            continue
        if re.match(r'^\d+\.\s+\S', stripped):
            continue
        # Previous/Next nav at bottom of content
        if re.match(r'^\[.+\]\(/docs/.+\)\[.+\]\(/docs/.+\)$', stripped):
            continue
        # JS code
        if stripped.startswith('((F,P,Q,U,j,$,N,W)=>') or stripped.startswith('(function('):
            continue
        # Broken card markup like "[### 快速开始"
        if stripped.startswith('[### '):
            continue
        # Orphaned link text from broken cards
        if re.match(r'^.+\]\(/docs/.+\)\[### .+', stripped):
            continue
        # Orphaned text from broken card grid (starts with trailing "](" pattern)
        if re.match(r'^[^\[].+\]\(/(?:docs|console|token-plan)/', stripped):
            continue

        # CSS block
        if stripped.startswith('.menu-bottom-popover'):
            skip_until = '}'
        if skip_until and stripped == skip_until:
            skip_until = None
            continue
        if skip_until:
            continue

        # CSS data attr line
        if re.match(r'^\[data-radix-scroll-area-viewport\]', stripped):
            continue

        # Stop before footer
        if ('Xiaomi MiMo 开放平台服务协议' in stripped or
            stripped.startswith('Copyright©20') or
            '.menu-bottom-popover' in stripped):
            break
        if stripped == '回到顶部':
            continue

        result.append(line)

    text = '\n'.join(result)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove trailing "### 目录" section
    toc_idx = text.rfind('\n### 目录\n')
    if toc_idx > 0:
        text = text[:toc_idx]
    return text.strip() + '\n'


# ============================================================
# Kimi cleanup
# ============================================================
# The CSS block is injected identically in every Kimi page.
KIMI_CSS_START = ':root {\n--brand-primary: #111111;'
KIMI_CSS_END = 'word-break: break-all;\n  }\n}\n'


def clean_kimi(text: str) -> str:
    # Remove the giant identical CSS block
    css_start = text.find(KIMI_CSS_START)
    if css_start > 0:
        css_end = text.find(KIMI_CSS_END, css_start)
        if css_end > 0:
            text = text[:css_start] + text[css_end + len(KIMI_CSS_END):]

    lines = text.split('\n')
    result = []
    found_content = False
    skip_block = False
    skip_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Promo banner
        if stripped.startswith('🎉 Kimi K2'):
            continue

        # JS blocks
        if stripped.startswith('(function(){') or 'document.documentElement.setAttribute' in stripped:
            skip_block = True
            skip_depth = 1
        if skip_block:
            # Count braces to find end of JS block
            for c in stripped:
                if c == '{':
                    skip_depth += 1
                elif c == '}':
                    skip_depth -= 1
            if skip_depth <= 0:
                skip_block = False
            continue

        # Minified next.js code
        if stripped.startswith('(self.__next_s'):
            continue

        # Top nav junk
        if stripped in ('搜索...', 'Ctrl K', '简体中文', 'Navigation'):
            continue
        if re.match(r'^-\s*\[(?:联系销售|博客|开发工作台|用户中心)\]', stripped):
            continue
        if stripped.startswith('[Kimi API 开放平台 home page]'):
            continue
        if stripped.startswith('[快速开始](/docs/overview)'):
            continue

        # Sidebar nav sections
        if re.match(r'^#####\s+\S', stripped):
            continue
        if re.match(r'^\s*-\s*\[.*\]\(/docs/', stripped):
            continue
        if re.match(r'^\[.*\]\(/docs/', stripped):
            continue

        # Detect content start
        if stripped.startswith('# ') and not found_content:
            found_content = True
            result.append(line)
            continue

        if not found_content:
            continue

        # Stop if we hit CSS or JS injection
        if stripped == ':root {' and i > 20:
            break
        if stripped.startswith('/*') and ('Footer' in stripped or 'Brand' in stripped):
            break

        result.append(line)

    text = '\n'.join(result)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip() + '\n'


# ============================================================
# Main
# ============================================================
def process_deepseek():
    md_dir = BASE / "deepseek_docs" / "markdown"
    count = 0
    for f in sorted(md_dir.glob("*.md")):
        orig = f.read_text(encoding="utf-8")
        fixed = fix_deepseek_text(orig)
        if fixed != orig:
            f.write_text(fixed, encoding="utf-8")
            count += 1
    print(f"[DeepSeek] Fixed encoding in {count}/{len(list(md_dir.glob('*.md')))} files")


def process_kimi_post():
    """Remove orphaned CSS variable lines from Kimi files (content already lost)."""
    md_dir = BASE / "kimi_docs" / "markdown"
    count = 0
    for f in sorted(md_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        lines = text.split('\n')
        # Remove CSS variable lines and closing braces left over from first run
        cleaned_lines = []
        for line in lines:
            s = line.strip()
            if s.startswith('--brand-') or s == '}':
                continue
            cleaned_lines.append(line)
        cleaned = '\n'.join(cleaned_lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.strip() + '\n'
        if cleaned != text:
            f.write_text(cleaned, encoding="utf-8")
            count += 1
    print(f"[Kimi post-clean] Stripped CSS fragments from {count} files")


def process_mimo():
    md_dir = BASE / "mimo_docs" / "markdown"
    count = 0
    for f in sorted(md_dir.glob("*.md")):
        orig = f.read_text(encoding="utf-8")
        cleaned = clean_mimo(orig)
        if cleaned != orig:
            f.write_text(cleaned, encoding="utf-8")
            count += 1
    print(f"[MiMo] Cleaned {count}/{len(list(md_dir.glob('*.md')))} files")


def process_kimi():
    md_dir = BASE / "kimi_docs" / "markdown"
    count = 0
    for f in sorted(md_dir.glob("*.md")):
        orig = f.read_text(encoding="utf-8")
        cleaned = clean_kimi(orig)
        if cleaned != orig:
            f.write_text(cleaned, encoding="utf-8")
            count += 1
    print(f"[Kimi] Cleaned {count}/{len(list(md_dir.glob('*.md')))} files")


if __name__ == "__main__":
    process_deepseek()
    process_mimo()
    process_kimi()
    process_kimi_post()
    print("Done.")
