#!/usr/bin/env python3
"""
Wiki Lint Tool - 知识库健康检查脚本 v2.1
基于 SCHEMA.md 规则和整理教训，覆盖以下维度：

  [1]  死链检查         — index.md 及 wiki/ 中的链接是否真实存在
  [2]  孤立页面         — wiki/ 下没有任何引用指向的文件
  [3a] 索引→磁盘        — index.md 列出的 wiki/ 路径是否在磁盘存在
  [3b] 磁盘→索引        — wiki/ 下文件是否都在 index.md 中有记录
  [3c] 缺失子目录       — index.md 列出的 wiki/ 子目录是否真实存在
  [4]  非MD文件入侵      — wiki/ 只允许 .md
  [5]  raw/ 散落文件    — raw/ 根目录不允许有文件（只能有子目录）
  [6]  raw/ 命名规范    — raw/ 文件名应符合 YYYYMMDD_主题.md 格式
  [7]  Frontmatter     — wiki/ 下的 .md 是否含必要字段
  [8]  无出站链接        — wiki/ 页面至少有一条出站链接
  [9]  未萃取文件        — raw/ 有但 wiki/ 没有对应萃取页面的文件
  [10] log.md 合规      — 不含日志以外的内容，格式符合规范
  [11] index/log 分离   — index.md 不含日志行；log.md 不含目录链接
  [+]  wiki/ 目录白名单  — 出现未定义的一级子目录
"""

import re
import sys
import io
from pathlib import Path
from datetime import datetime

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 路径配置 ──────────────────────────────────────────────────────────────────
BASE       = Path(__file__).parent.parent.parent / "03_Assets_全局库"
WIKI_ROOT  = BASE / "wiki"
RAW_ROOT   = BASE / "raw"
INDEX_FILE = BASE / "index.md"
LOG_FILE   = BASE / "log.md"

# ── SCHEMA 定义的 wiki/ 一级子目录（白名单）────────────────────────────────────
ALLOWED_WIKI_DIRS = {"AI工具谱", "个人成长", "知识库架构", "账号运营", "选题库"}

# wiki/ 下的 README.md 和 index 类文件豁免 frontmatter 检查
FRONTMATTER_EXEMPT = {"README.md"}

# frontmatter 必填字段（根据 SCHEMA.md）
REQUIRED_FRONTMATTER_FIELDS = ["title", "录入日期"]

# raw/ 文件名格式（YYYYMMDD_ 前缀）
RAW_FILENAME_RE = re.compile(r'^\d{8}_')

# log.md 行格式（Append-only 操作日志）
LOG_LINE_RE = re.compile(r'^## \[\d{4}-\d{2}-\d{2}\]')


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════

def read_md(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ""


def extract_links(content: str) -> list[tuple[str, str]]:
    """提取所有 Markdown 链接和双链 [[xxx]]"""
    links = []
    for m in re.finditer(r'\[\[([^\]]+)\]\]', content):
        links.append((m.group(1).strip(), "double_bracket"))
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
        url = m.group(2).strip()
        if not url.startswith('http') and (url.endswith('.md') or '/' in url):
            links.append((url, "markdown"))
    return links


def resolve_markdown_link(src_file: Path, href: str, wiki_root: Path) -> Path | None:
    """将 markdown 链接解析为绝对路径（相对于 wiki_root 或 src_file 所在目录）"""
    # 先尝试相对于 wiki_root
    candidates = [
        wiki_root / href,
        src_file.parent / href,
        wiki_root / (href + ".md") if not href.endswith('.md') else None,
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return None


def find_double_bracket_target(name: str, wiki_root: Path) -> Path | None:
    """在 wiki_root 下查找与 [[name]] 匹配的文件"""
    name_clean = name.strip().lstrip('#').strip()
    for f in wiki_root.rglob("*.md"):
        if name_clean == f.stem or name_clean == f.name or name_clean in f.stem:
            return f
    return None


def extract_frontmatter(content: str) -> dict:
    """提取 YAML frontmatter（--- ... ---）"""
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip()
    return fm


# ══════════════════════════════════════════════════════════════════════════════
# 检查模块
# ══════════════════════════════════════════════════════════════════════════════

def check_dead_links() -> list[dict]:
    """[1] 检查死链（双链 + Markdown 链接）"""
    issues = []
    for md_file in WIKI_ROOT.rglob("*.md"):
        content = read_md(md_file)
        for link_text, link_type in extract_links(content):
            if link_type == "markdown":
                target = resolve_markdown_link(md_file, link_text, WIKI_ROOT)
                if target is None:
                    issues.append({
                        "file": md_file.relative_to(WIKI_ROOT).as_posix(),
                        "link": link_text,
                        "type": "markdown"
                    })
            elif link_type == "double_bracket":
                if find_double_bracket_target(link_text, WIKI_ROOT) is None:
                    issues.append({
                        "file": md_file.relative_to(WIKI_ROOT).as_posix(),
                        "link": f"[[{link_text}]]",
                        "type": "double_bracket"
                    })
    return issues


def check_orphans() -> list[str]:
    """[2] 检查 wiki/ 下的孤立页面（没有任何引用指向它）"""
    all_files = {f for f in WIKI_ROOT.rglob("*.md")}
    referenced = set()

    # index.md 里的链接也算引用
    if INDEX_FILE.exists():
        idx_content = read_md(INDEX_FILE)
        for m in re.finditer(r'\[([^\]]+)\]\((wiki/[^)]+)\)', idx_content):
            href = m.group(2).strip()
            if not href.endswith('.md'):
                href += '.md'
            t = BASE / href
            if t.exists():
                referenced.add(t)

    for md_file in WIKI_ROOT.rglob("*.md"):
        content = read_md(md_file)
        for link_text, link_type in extract_links(content):
            if link_type == "double_bracket":
                t = find_double_bracket_target(link_text, WIKI_ROOT)
                if t:
                    referenced.add(t)
            elif link_type == "markdown":
                t = resolve_markdown_link(md_file, link_text, WIKI_ROOT)
                if t:
                    referenced.add(t)

    # README.md 豁免（它们是目录索引，自身即入口）
    orphans = []
    for f in all_files:
        if f not in referenced and f.name not in FRONTMATTER_EXEMPT:
            orphans.append(f.relative_to(WIKI_ROOT).as_posix())
    return sorted(orphans)


def check_index_consistency() -> dict:
    """[3] index.md 与 wiki/ 物理文件一致性（只检查 wiki/ 内文件，排除 raw/）"""
    physical = {f.relative_to(WIKI_ROOT).as_posix() for f in WIKI_ROOT.rglob("*.md")}
    indexed = set()

    if INDEX_FILE.exists():
        content = read_md(INDEX_FILE)
        for m in re.finditer(r'\[([^\]]+)\]\((wiki/[^)]+)\)', content):
            href = m.group(2).strip()
            if not href.endswith('.md'):
                href += '.md'
            # 去掉 "wiki/" 前缀
            inner = href[5:] if href.startswith('wiki/') else href
            indexed.add(inner)

    missing_from_index = sorted(physical - indexed)
    missing_from_disk  = sorted(indexed - physical)

    return {
        "missing_from_index": missing_from_index,
        "missing_from_disk": missing_from_disk
    }


def check_non_md_in_wiki() -> list[str]:
    """[4] wiki/ 下是否有非 .md 文件（只允许 Markdown）"""
    issues = []
    for f in WIKI_ROOT.rglob("*"):
        if f.is_file() and f.suffix.lower() != '.md':
            issues.append(f.relative_to(WIKI_ROOT).as_posix())
    return sorted(issues)


def check_raw_root_files() -> list[str]:
    """[5] raw/ 根目录不允许散落文件（只能有子目录）"""
    issues = []
    for item in RAW_ROOT.iterdir():
        if item.is_file():
            issues.append(item.name)
    return sorted(issues)


def check_raw_filename_convention() -> list[str]:
    """[6] raw/ 子目录下的文件名是否符合 YYYYMMDD_ 前缀规范"""
    issues = []
    for f in RAW_ROOT.rglob("*.md"):
        if f.parent == RAW_ROOT:
            continue  # 根目录散落文件已由 [5] 报告
        if not RAW_FILENAME_RE.match(f.name):
            issues.append(f.relative_to(RAW_ROOT).as_posix())
    return sorted(issues)


def check_wiki_frontmatter() -> list[dict]:
    """[7] wiki/ 下的页面是否含必要 frontmatter 字段（README.md 豁免）"""
    issues = []
    for f in WIKI_ROOT.rglob("*.md"):
        if f.name in FRONTMATTER_EXEMPT:
            continue
        content = read_md(f)
        fm = extract_frontmatter(content)
        missing = [field for field in REQUIRED_FRONTMATTER_FIELDS if field not in fm]
        if missing:
            issues.append({
                "file": f.relative_to(WIKI_ROOT).as_posix(),
                "missing_fields": missing
            })
    return issues


def check_wiki_outbound_links() -> list[str]:
    """[8] wiki/ 下每个页面至少有一条出站链接（README.md 豁免）"""
    issues = []
    for f in WIKI_ROOT.rglob("*.md"):
        if f.name in FRONTMATTER_EXEMPT:
            continue
        content = read_md(f)
        links = extract_links(content)
        if not links:
            issues.append(f.relative_to(WIKI_ROOT).as_posix())
    return sorted(issues)


def check_log_integrity() -> list[str]:
    """[9] log.md 存在 + 每行日志符合格式（## [YYYY-MM-DD] 动作 | 描述）"""
    issues = []
    if not LOG_FILE.exists():
        return ["log.md 文件不存在"]
    content = read_md(LOG_FILE)
    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        # 只检查 ## 开头的非标题行
        if line.startswith('## ') and not LOG_LINE_RE.match(line) and '---' not in line:
            issues.append(f"第{i}行格式异常: {line[:80]}")
    return issues


def check_index_log_separation() -> dict:
    """[10] index.md 不含操作日志行；log.md 不含目录链接"""
    idx_log_leaks = []
    log_idx_leaks = []

    if INDEX_FILE.exists():
        for i, line in enumerate(read_md(INDEX_FILE).splitlines(), 1):
            if LOG_LINE_RE.match(line):
                idx_log_leaks.append(f"第{i}行: {line[:80]}")

    if LOG_FILE.exists():
        for i, line in enumerate(read_md(LOG_FILE).splitlines(), 1):
            if re.search(r'\[.+\]\(wiki/', line):
                log_idx_leaks.append(f"第{i}行: {line[:80]}")

    return {
        "index_has_log": idx_log_leaks,
        "log_has_index": log_idx_leaks
    }


def check_unextracted_raw() -> list[dict]:
    """[9] raw/ 下有文件，但 wiki/ 中没有对应萃取页面

    判断策略：
    - 取 raw/ 文件的「主题关键词」部分（去掉日期前缀和 .md 后缀）
    - 在 wiki/ 所有 .md 文件名中模糊匹配（stem 包含关键词）
    - 若无任何匹配，标记为「未萃取」
    - 豁免：文件名极短（<4字）或为通用文件（README、index 等）
    """
    EXEMPT_STEMS = {"README", "index", "SCHEMA", "log"}
    issues = []
    wiki_stems = [f.stem.lower() for f in WIKI_ROOT.rglob("*.md")]

    for raw_file in RAW_ROOT.rglob("*.md"):
        stem = raw_file.stem
        # 去掉 YYYYMMDD_ 前缀
        clean = re.sub(r'^\d{8}_?', '', stem).strip()
        if not clean or clean in EXEMPT_STEMS or len(clean) < 4:
            continue
        clean_lower = clean.lower()
        # 检查 wiki/ 是否存在名称包含关键词的文件
        matched = any(clean_lower in ws or ws in clean_lower for ws in wiki_stems)
        if not matched:
            issues.append({
                "raw_file": raw_file.relative_to(RAW_ROOT).as_posix(),
                "keyword": clean
            })
    return issues


def check_index_missing_dirs() -> list[str]:
    """[3c] index.md 中列出的 wiki/ 子目录标题，是否对应真实磁盘目录"""
    issues = []
    if not INDEX_FILE.exists():
        return []
    content = read_md(INDEX_FILE)
    # 提取 ## 二级标题（假设它们对应 wiki/ 子目录）
    for m in re.finditer(r'^## (.+)', content, re.MULTILINE):
        section_name = m.group(1).strip()
        # 跳过「原始资料」「日志」等非目录标题
        skip_keywords = {"原始资料", "日志", "log", "raw"}
        if any(k in section_name.lower() for k in skip_keywords):
            continue
        dir_path = WIKI_ROOT / section_name
        if not dir_path.exists():
            issues.append(section_name)
    return issues


def check_wiki_dir_structure() -> list[str]:
    """[+] wiki/ 下出现未在白名单的一级子目录"""
    issues = []
    if not WIKI_ROOT.exists():
        return []
    for item in WIKI_ROOT.iterdir():
        if item.is_dir() and item.name not in ALLOWED_WIKI_DIRS:
            issues.append(item.name)
    return sorted(issues)


# ══════════════════════════════════════════════════════════════════════════════
# 报告输出
# ══════════════════════════════════════════════════════════════════════════════

def section(title: str, ok_msg: str, items, formatter=None):
    count = len(items)
    print(f"\n{'─'*60}")
    print(f"  {title}  ({count} 项)")
    print('─'*60)
    if not items:
        print(f"  OK  {ok_msg}")
    else:
        for item in items:
            print("  " + (formatter(item) if formatter else str(item)))


def print_report(results: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("\n" + "="*60)
    print(f"  WIKI LINT REPORT  —  {now}")
    print("="*60)
    print(f"  wiki/ 路径: {WIKI_ROOT}")
    print(f"  wiki/ 文件数: {len(list(WIKI_ROOT.rglob('*.md')))}")
    print(f"  raw/  文件数: {len(list(RAW_ROOT.rglob('*.md')))}")

    section("[1] 死链",
            "无死链",
            results["dead_links"],
            lambda x: f"DEAD  {x['file']}  →  {x['link']}")

    section("[2] 孤立页面（无引用指向）",
            "无孤立页面",
            results["orphans"],
            lambda x: f"ORPHAN  {x}")

    section("[3a] index.md 引用但磁盘不存在（死路径）",
            "index.md 无悬空引用",
            results["consistency"]["missing_from_disk"],
            lambda x: f"MISSING_FILE  wiki/{x}")

    section("[3b] 磁盘存在但未入 index.md",
            "所有 wiki 文件均已索引",
            results["consistency"]["missing_from_index"],
            lambda x: f"NOT_INDEXED  wiki/{x}")

    section("[3c] index.md 列出的子目录在磁盘不存在",
            "所有分类目录均存在",
            results["missing_dirs"],
            lambda x: f"MISSING_DIR  wiki/{x}/")

    section("[4] wiki/ 非 .md 文件",
            "wiki/ 目录整洁",
            results["non_md"],
            lambda x: f"BAD_EXT  {x}")

    section("[5] raw/ 根目录散落文件",
            "raw/ 根目录干净",
            results["raw_root_files"],
            lambda x: f"STRAY  raw/{x}")

    section("[6] raw/ 文件名不符合规范（缺 YYYYMMDD_ 前缀）",
            "raw/ 文件名格式正确",
            results["raw_naming"],
            lambda x: f"BAD_NAME  raw/{x}")

    section("[7] wiki/ 缺少 frontmatter 字段",
            "frontmatter 完整",
            results["frontmatter"],
            lambda x: f"MISSING_FM  {x['file']}  缺: {', '.join(x['missing_fields'])}")

    section("[8] wiki/ 页面无出站链接（孤岛）",
            "所有页面均有出站链接",
            results["no_outbound"],
            lambda x: f"NO_LINK  {x}")

    section("[9] raw/ 有但 wiki/ 无对应萃取页面（未萃取）",
            "所有 raw/ 文件均有对应 wiki 萃取页",
            results["unextracted"],
            lambda x: f"NO_WIKI  raw/{x['raw_file']}  (关键词: {x['keyword']})")

    section("[10] log.md 格式异常行",
            "log.md 格式正常",
            results["log_issues"],
            lambda x: f"LOG_FMT  {x}")

    idx_log = results["separation"]["index_has_log"]
    log_idx = results["separation"]["log_has_index"]
    section("[11a] index.md 泄漏了操作日志行",
            "index.md 无日志污染",
            idx_log,
            lambda x: f"LEAK  {x}")
    section("[11b] log.md 含目录链接（应只在 index.md）",
            "log.md 无目录污染",
            log_idx,
            lambda x: f"LEAK  {x}")

    section("[+] wiki/ 出现未知一级子目录",
            "目录结构符合白名单",
            results["unknown_dirs"],
            lambda x: f"UNKNOWN_DIR  wiki/{x}/  (允许: {', '.join(sorted(ALLOWED_WIKI_DIRS))})")

    # 汇总
    all_issues = (
        results["dead_links"] + results["orphans"]
        + results["consistency"]["missing_from_index"]
        + results["consistency"]["missing_from_disk"]
        + results["missing_dirs"]
        + results["non_md"] + results["raw_root_files"] + results["raw_naming"]
        + results["frontmatter"] + results["no_outbound"]
        + results["unextracted"]
        + results["log_issues"]
        + results["separation"]["index_has_log"]
        + results["separation"]["log_has_index"]
        + results["unknown_dirs"]
    )
    total = len(all_issues)

    print("\n" + "="*60)
    if total == 0:
        print("  STATUS: ALL CLEAN  (0 issues)")
    else:
        print(f"  STATUS: {total} ISSUE(S) FOUND")
    print("="*60 + "\n")
    return total


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not WIKI_ROOT.exists():
        print(f"Error: wiki/ 目录不存在: {WIKI_ROOT}")
        sys.exit(1)
    if not RAW_ROOT.exists():
        print(f"Error: raw/ 目录不存在: {RAW_ROOT}")
        sys.exit(1)

    print(f"Scanning {BASE} ...")

    sep = check_index_log_separation()
    results = {
        "dead_links":      check_dead_links(),
        "orphans":         check_orphans(),
        "consistency":     check_index_consistency(),
        "missing_dirs":    check_index_missing_dirs(),
        "non_md":          check_non_md_in_wiki(),
        "raw_root_files":  check_raw_root_files(),
        "raw_naming":      check_raw_filename_convention(),
        "frontmatter":     check_wiki_frontmatter(),
        "no_outbound":     check_wiki_outbound_links(),
        "unextracted":     check_unextracted_raw(),
        "log_issues":      check_log_integrity(),
        "separation":      sep,
        "unknown_dirs":    check_wiki_dir_structure(),
    }

    total = print_report(results)
    sys.exit(1 if total > 0 else 0)


if __name__ == "__main__":
    main()
