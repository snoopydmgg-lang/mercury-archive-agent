"""
DeepSeek API Docs Crawler
Uses requests + BeautifulSoup for Docusaurus SSR site.
"""
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as mdify


BASE_URL = "https://api-docs.deepseek.com"
LANG_PREFIX = "/zh-cn"
START_URL = f"{BASE_URL}{LANG_PREFIX}/"

OUTPUT_DIR = Path(__file__).parent / "output"
HTML_DIR = OUTPUT_DIR / "html"
MD_DIR = OUTPUT_DIR / "markdown"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Pages to skip
SKIP_PATTERNS = [
    r"/tag/", r"/blog/",
    r"\.jpg$", r"\.png$", r"\.gif$", r"\.svg$", r"\.mp4$",
    r"/api_samples/",   # code samples only
    r"/markdown-page",  # placeholder
    r"/prompt-library", # not core docs
    r"/PromptLibrary",
]


def sanitize_filename(url_path):
    """Create English filename from URL path."""
    path = url_path.replace(LANG_PREFIX, "").strip("/")
    if not path:
        path = "index"
    name = path.replace("/", "_").replace("-", "_")
    name = re.sub(r"[^\w_]", "", name)
    return name.lower()


def discover_links(session):
    """Discover all documentation pages from sitemap and sidebar."""
    links = {}

    # Method 1: Sitemap
    try:
        resp = session.get(f"{BASE_URL}/sitemap.xml", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, "html.parser")
        for loc in soup.find_all("loc"):
            url = loc.text.strip()
            path = url.replace(BASE_URL, "")
            if any(re.search(p, url) for p in SKIP_PATTERNS):
                continue
            zh_url = f"{BASE_URL}{LANG_PREFIX}{path}" if path.startswith("/") else url
            if zh_url not in links:
                links[zh_url] = path
    except Exception as e:
        print(f"  Sitemap error: {e}")

    # Method 2: Parse sidebar from home page
    try:
        resp = session.get(START_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.content, "html.parser")
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if href.startswith(LANG_PREFIX) and not any(re.search(p, href) for p in SKIP_PATTERNS):
                if not href.endswith((".css", ".js", ".svg", ".png", ".jpg")):
                    full_url = urljoin(BASE_URL, href)
                    if full_url not in links:
                        links[full_url] = href
    except Exception as e:
        print(f"  Sidebar parse error: {e}")

    return links


def extract_content(html, url):
    """Extract main content from Docusaurus HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav, footer, sidebar, TOC
    for tag in soup.select("nav, footer, .theme-doc-sidebar-container, "
                           ".theme-doc-toc-desktop, .theme-doc-breadcrumbs, "
                           ".pagination-nav, script, style"):
        tag.decompose()

    # Try Docusaurus article container
    article = soup.select_one("article") or soup.select_one(".theme-doc-markdown")
    if article:
        return str(article)

    # Fallback
    main = soup.select_one("main") or soup.select_one(".main-wrapper")
    if main:
        return str(main)

    return str(soup.body) if soup.body else ""


def get_page_title(soup, url):
    """Extract page title."""
    # Docusaurus title
    h1 = soup.select_one("article h1") or soup.select_one("h1")
    if h1:
        return h1.get_text(strip=True)
    # Meta title
    title_tag = soup.select_one("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
        return title.replace(" | DeepSeek API Docs", "").strip()
    return url.split("/")[-1] or "index"


def crawl():
    """Main crawl function."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("DeepSeek API Docs Crawler")
    print(f"Start URL: {START_URL}")
    print("=" * 60)

    session = requests.Session()
    session.headers.update(HEADERS)

    # Step 1: Discover links
    print("\n[1] Discovering documentation pages...")
    links = discover_links(session)
    print(f"    Found {len(links)} pages.")

    # Print for review
    for url, path in sorted(links.items(), key=lambda x: x[1]):
        print(f"    - {path}")

    # Step 2: Crawl each page
    print(f"\n[2] Crawling {len(links)} pages...")
    index_entries = []
    success = 0
    failed = 0

    for i, (url, path) in enumerate(links.items(), 1):
        filename = sanitize_filename(path)
        print(f"\n  [{i}/{len(links)}] {path}")

        try:
            resp = session.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                print(f"    HTTP {resp.status_code}")
                failed += 1
                continue

            soup = BeautifulSoup(resp.content, "html.parser")
            title = get_page_title(soup, url)

            # Extract main content
            content_html = extract_content(resp.text, url)

            if content_html and len(content_html) > 100:
                # Save HTML
                html_path = HTML_DIR / f"{filename}.html"
                wrapper = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"/><title>{title}</title>
<meta name="source-url" content="{url}"/></head>
<body>{content_html}</body></html>"""
                html_path.write_text(wrapper, encoding="utf-8")

                # Save Markdown
                md_content = mdify(content_html, heading_style="ATX", bullets="-",
                                   strip=["script", "style", "img", "svg"])
                md_path = MD_DIR / f"{filename}.md"
                md_header = f"# {title}\n\n> Source: {url}\n\n---\n\n"
                md_path.write_text(md_header + md_content, encoding="utf-8")

                index_entries.append({
                    "title": title,
                    "url": url,
                    "html": f"html/{filename}.html",
                    "markdown": f"markdown/{filename}.md",
                })
                success += 1
                print(f"    OK: {title} ({len(content_html)} chars)")
            else:
                failed += 1
                print(f"    SKIP: insufficient content")

        except Exception as e:
            failed += 1
            print(f"    FAIL: {e}")

        # Rate limit
        if i < len(links):
            time.sleep(1.2)

    # Step 3: Generate index
    print(f"\n[3] Generating docs_index.md...")
    index_lines = [
        "# DeepSeek API Documentation Index",
        "",
        f"Crawled: {len(links)} pages | Success: {success} | Failed: {failed}",
        f"Source: {START_URL}",
        "",
        "| # | Title | Original URL | HTML | Markdown |",
        "|---|-------|-------------|------|----------|",
    ]
    for i, entry in enumerate(index_entries, 1):
        index_lines.append(
            f"| {i} | {entry['title']} | {entry['url']} | "
            f"[html]({entry['html']}) | [md]({entry['markdown']}) |"
        )
    (OUTPUT_DIR / "docs_index.md").write_text("\n".join(index_lines), encoding="utf-8")

    print(f"\n{'=' * 60}")
    print(f"CRAWL COMPLETE")
    print(f"  Pages found:    {len(links)}")
    print(f"  Successful:     {success}")
    print(f"  Failed:         {failed}")
    print(f"  Output:         {OUTPUT_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    crawl()
