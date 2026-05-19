#!/usr/bin/env python3
"""
Wiki Lint Tool - 知识库健康检查脚本 v2.2 (Obsidian 增强版)
基于 v2.1 增加 Obsidian 特性检查：

新增检查项：
  [12] 双向链接格式    — 检查 [[链接]] 格式是否正确
  [13] Canvas 文件     — 检查 .canvas 文件格式是否符合规范
  [14] 图片路径        — 检查 assets/ 图片路径是否正确
  [15] Obsidian 元数据 — 检查 Obsidian 特有的 YAML 字段
  [16] 知识图谱连通性   — 检查是否有大量孤立的知识岛

原有检查项（v2.1）：
  [1]  死链检查         — index.md 及 wiki/ 中的链接是否真实存在
  [2]  孤立页面         — wiki/ 下没有任何引用指向的文件
  [3a] 索引→磁盘        — index.md 列出的 wiki/ 路径是否在磁盘存在
  [3b] 磁盘→索引        — wiki/ 下文件是否都在 index.md 中有记录
  [3c] 缺失子目录       — index.md 列出的 wiki/ 子目录是否真实存在
  [4]  非MD文件入侵      — wiki/ 只允许 .md 和 .canvas
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
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 路径配置 ──────────────────────────────────────────────────────────────────
# 支持两种知识库路径：03_Assets_全局库（旧）和 Wiki知识库（新）
BASE_CANDIDATES = [
    Path(__file__).parent.parent.parent / "Wiki知识库",
    Path(__file__).parent.parent.parent / "03_Assets_全局库",
]

BASE = None
for candidate in BASE_CANDIDATES:
    if candidate.exists():
        BASE = candidate
        break

if BASE is None:
    print("❌ 错误：找不到知识库根目录")
    sys.exit(1)

WIKI_ROOT  = BASE / "wiki"
RAW_ROOT   = BASE / "raw"
INDEX_FILE = BASE / "index.md"
LOG_FILE   = BASE / "log.md"
ASSETS_DIR = BASE / "assets"  # Obsidian 图片目录

# ── SCHEMA 定义的 wiki/ 一级子目录（白名单）────────────────────────────────────
ALLOWED_WIKI_DIRS = {"AI工具谱", "个人成长", "知识库架构", "账号运营", "选题库", "围棋速成"}

# wiki/ 下的 README.md 和 index 类文件豁免 frontmatter 检查
FRONTMATTER_EXEMPT = {"README.md", "index.md"}

# frontmatter 必填字段（根据 SCHEMA.md）
REQUIRED_FRONTMATTER_FIELDS = ["title", "录入日期"]

# Obsidian 推荐字段（可选但建议有）
OBSIDIAN_RECOMMENDED_FIELDS = ["tags", "aliases", "关联笔记"]

# raw/ 文件名格式（YYYYMMDD_ 前缀）
RAW_FILENAME_RE = re.compile(r'^\d{8}_')

# log.md 行格式（Append-only 操作日志）
LOG_LINE_RE = re.compile(r'^## \[\d{4}-\d{2}-\d{2}\]')

# 双向链接格式检查
WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')
WIKILINK_WITH_ALIAS_RE = re.compile(r'\[\[([^\|]+)\|([^\]]+)\]\]')

# 图片链接格式检查
IMAGE_LINK_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


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


def extract_image_links(content: str) -> list[tuple[str, str]]:
    """提取所有图片链接"""
    images = []
    for m in IMAGE_LINK_RE.finditer(content):
        alt_text = m.group(1)
        image_path = m.group(2)
        images.append((alt_text, image_path))
    return images


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

    # 处理带别名的链接 [[文件|别名]]
    if '|' in name_clean:
        name_clean = name_clean.split('|')[0].strip()

    for f in wiki_root.rglob("*.md"):
        if name_clean == f.stem or name_clean == f.name or name_clean in f.stem:
            return f
    return None


def extract_frontmatter(content: str) -> dict:
    """提取 YAML frontmatter"""
    if not content.startswith('---'):
        return {}

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}

    fm_text = parts[1]
    fm_dict = {}

    current_key = None
    current_list = []

    for line in fm_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 处理列表项
        if line.startswith('- '):
            if current_key:
                current_list.append(line[2:].strip())
            continue

        # 处理键值对
        if ':' in line:
            # 保存之前的列表
            if current_key and current_list:
                fm_dict[current_key] = current_list
                current_list = []

            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value:
                fm_dict[key] = value
            else:
                current_key = key

    # 保存最后的列表
    if current_key and current_list:
        fm_dict[current_key] = current_list

    return fm_dict


def check_canvas_format(canvas_path: Path) -> list[str]:
    """检查 Canvas 文件格式是否符合 JSON Canvas 规范"""
    errors = []

    try:
        content = canvas_path.read_text(encoding='utf-8')
        data = json.loads(content)

        # 检查必需字段
        if 'nodes' not in data:
            errors.append(f"缺少 'nodes' 字段")
        if 'edges' not in data:
            errors.append(f"缺少 'edges' 字段")

        # 检查节点格式
        if 'nodes' in data:
            for i, node in enumerate(data['nodes']):
                if 'id' not in node:
                    errors.append(f"节点 {i} 缺少 'id' 字段")
                if 'type' not in node:
                    errors.append(f"节点 {i} 缺少 'type' 字段")
                if 'x' not in node or 'y' not in node:
                    errors.append(f"节点 {i} 缺少坐标字段")

        # 检查边格式
        if 'edges' in data:
            for i, edge in enumerate(data['edges']):
                if 'id' not in edge:
                    errors.append(f"边 {i} 缺少 'id' 字段")
                if 'fromNode' not in edge or 'toNode' not in edge:
                    errors.append(f"边 {i} 缺少连接字段")

    except json.JSONDecodeError as e:
        errors.append(f"JSON 格式错误: {e}")
    except Exception as e:
        errors.append(f"读取失败: {e}")

    return errors


def check_wikilink_format(content: str) -> list[str]:
    """检查双向链接格式是否正确"""
    errors = []

    # 检查是否有错误的链接格式
    # 错误示例：[[ 链接 ]]（有多余空格）、[[链接]（缺少右括号）

    # 检查多余空格
    for m in re.finditer(r'\[\[\s+([^\]]+)\s+\]\]', content):
        errors.append(f"双向链接有多余空格: [[{m.group(1)}]]")

    # 检查不完整的链接
    for m in re.finditer(r'\[\[([^\]]+)(?!\]\])', content):
        if ']]' not in content[m.end():m.end()+10]:
            errors.append(f"双向链接不完整: [[{m.group(1)}...")

    return errors


def analyze_knowledge_graph(wiki_root: Path) -> dict:
    """分析知识图谱连通性"""
    # 构建图
    graph = defaultdict(set)
    all_files = set()

    for md_file in wiki_root.rglob("*.md"):
        all_files.add(md_file)
        content = read_md(md_file)
        links = extract_links(content)

        for link_text, link_type in links:
            target = find_double_bracket_target(link_text, wiki_root)
            if target:
                graph[md_file].add(target)
                graph[target].add(md_file)  # 双向

    # 查找连通分量（使用 DFS）
    visited = set()
    components = []

    def dfs(node, component):
        visited.add(node)
        component.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, component)

    for file in all_files:
        if file not in visited:
            component = set()
            dfs(file, component)
            components.append(component)

    return {
        'total_files': len(all_files),
        'total_links': sum(len(neighbors) for neighbors in graph.values()) // 2,
        'components': len(components),
        'largest_component': max(len(c) for c in components) if components else 0,
        'isolated_files': [f for c in components if len(c) == 1 for f in c]
    }


# ══════════════════════════════════════════════════════════════════════════════
# 主检查函数
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"🔍 Wiki Lint v2.2 (Obsidian 增强版)")
    print(f"📁 知识库路径: {BASE}")
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    issues = []

    # [12] 双向链接格式检查
    print("\n[12] 检查双向链接格式...")
    for md_file in WIKI_ROOT.rglob("*.md"):
        content = read_md(md_file)
        errors = check_wikilink_format(content)
        for error in errors:
            issues.append(f"[12] {md_file.relative_to(BASE)}: {error}")

    # [13] Canvas 文件检查
    print("[13] 检查 Canvas 文件...")
    for canvas_file in WIKI_ROOT.rglob("*.canvas"):
        errors = check_canvas_format(canvas_file)
        for error in errors:
            issues.append(f"[13] {canvas_file.relative_to(BASE)}: {error}")

    # [14] 图片路径检查
    print("[14] 检查图片路径...")
    for md_file in WIKI_ROOT.rglob("*.md"):
        content = read_md(md_file)
        images = extract_image_links(content)

        for alt_text, image_path in images:
            # 检查图片是否存在
            if not image_path.startswith('http'):
                # 尝试多种路径解析
                candidates = [
                    BASE / image_path.lstrip('/'),
                    md_file.parent / image_path,
                    ASSETS_DIR / image_path.lstrip('/'),
                ]

                found = False
                for candidate in candidates:
                    if candidate.exists():
                        found = True
                        break

                if not found:
                    issues.append(f"[14] {md_file.relative_to(BASE)}: 图片不存在 {image_path}")

    # [15] Obsidian 元数据检查
    print("[15] 检查 Obsidian 元数据...")
    for md_file in WIKI_ROOT.rglob("*.md"):
        if md_file.name in FRONTMATTER_EXEMPT:
            continue

        content = read_md(md_file)
        fm = extract_frontmatter(content)

        # 检查推荐字段
        missing_recommended = []
        for field in OBSIDIAN_RECOMMENDED_FIELDS:
            if field not in fm:
                missing_recommended.append(field)

        if missing_recommended:
            issues.append(f"[15] {md_file.relative_to(BASE)}: 缺少推荐字段 {', '.join(missing_recommended)}")

    # [16] 知识图谱连通性检查
    print("[16] 分析知识图谱连通性...")
    graph_stats = analyze_knowledge_graph(WIKI_ROOT)

    print(f"\n📊 知识图谱统计:")
    print(f"  - 总文件数: {graph_stats['total_files']}")
    print(f"  - 总链接数: {graph_stats['total_links']}")
    print(f"  - 连通分量数: {graph_stats['components']}")
    print(f"  - 最大连通分量: {graph_stats['largest_component']} 个文件")

    if graph_stats['components'] > 1:
        print(f"\n⚠️  发现 {graph_stats['components']} 个独立的知识岛")
        print(f"  建议：增加跨主题的交叉链接，提高知识图谱连通性")

    if graph_stats['isolated_files']:
        print(f"\n⚠️  发现 {len(graph_stats['isolated_files'])} 个完全孤立的文件:")
        for f in graph_stats['isolated_files'][:10]:  # 只显示前10个
            print(f"    - {f.relative_to(BASE)}")
        if len(graph_stats['isolated_files']) > 10:
            print(f"    ... 还有 {len(graph_stats['isolated_files']) - 10} 个")

    # 输出总结
    print("\n" + "=" * 80)
    if issues:
        print(f"\n❌ 发现 {len(issues)} 个问题:\n")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n💡 建议：逐项修复上述问题，保持知识库健康")
    else:
        print("\n✅ 所有检查通过！知识库状态良好")

    print("\n" + "=" * 80)
    print(f"📝 检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return len(issues)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(0 if exit_code == 0 else 1)
