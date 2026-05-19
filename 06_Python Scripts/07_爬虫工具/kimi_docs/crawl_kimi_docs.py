"""
Kimi Platform Docs Crawler
Uses Playwright for Next.js App Router SSR/CSR hybrid pages.
URL list from sitemap.xml.
"""
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from markdownify import markdownify as mdify


BASE_URL = "https://platform.kimi.com"
SITEMAP_URL = f"{BASE_URL}/docs/sitemap.xml"
OUTPUT_DIR = Path(__file__).parent / "output"
HTML_DIR = OUTPUT_DIR / "html"
MD_DIR = OUTPUT_DIR / "markdown"

SKIP_PATTERNS = [
    r"/agreement/",  # legal docs
    r"\.jpg$", r"\.png$", r"\.gif$", r"\.svg$",
]


def sanitize_filename(url_path):
    path = url_path.replace("/docs/", "").strip("/")
    if not path:
        path = "index"
    name = path.replace("/", "_").replace("-", "_")
    name = re.sub(r"[^\w_]", "", name)
    return name.lower()[:100]


def get_sitemap_urls():
    """Extract all /docs/ URLs from sitemap."""
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(SITEMAP_URL, headers={
        "User-Agent": "Mozilla/5.0"
    }, timeout=15)
    soup = BeautifulSoup(resp.content, "html.parser")
    urls = []
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        if "/docs/" in url and not any(re.search(p, url) for p in SKIP_PATTERNS):
            urls.append(url)
    return sorted(set(urls))


def extract_main_content(page):
    selectors = [
        "article",
        "main",
        "[class*='content']",
        ".prose",
        ".markdown",
        "[class*='markdown']",
        "[class*='doc-content']",
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                html = el.inner_html()
                if html and len(html) > 200:
                    return html
        except Exception:
            continue

    try:
        body = page.query_selector("body")
        if body:
            return body.inner_html()
    except Exception:
        pass
    return page.content()


def crawl():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Kimi Platform Docs Crawler")
    print("=" * 60)

    # Get URLs from sitemap
    print("\n[1] Fetching sitemap...")
    urls = get_sitemap_urls()
    print(f"    Found {len(urls)} documentation pages.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        print(f"\n[2] Crawling {len(urls)} pages...")
        index_entries = []
        success = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            path = url.replace(BASE_URL, "")
            filename = sanitize_filename(path)
            print(f"\n  [{i}/{len(urls)}] {path}")

            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)

                # Remove banners, popups
                page.evaluate("""
                    () => {
                        document.querySelectorAll('[class*="banner"], [class*="popup"], [class*="modal"], [class*="overlay"]').forEach(el => el.remove());
                    }
                """)

                # Get title
                title = page.title()
                if "|" in title:
                    title = title.split("|")[0].strip()
                title = title.replace(" - Kimi Platform", "").replace(" - Kimi", "").strip()

                html_content = extract_main_content(page)

                if html_content and len(html_content) > 100:
                    # Save HTML
                    html_path = HTML_DIR / f"{filename}.html"
                    wrapper = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><title>{title}</title>
<meta name="source-url" content="{url}"/></head>
<body>{html_content}</body></html>"""
                    html_path.write_text(wrapper, encoding="utf-8")

                    # Save Markdown
                    md_content = mdify(html_content, heading_style="ATX", bullets="-",
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
                    print(f"    OK: {title} ({len(html_content)} chars)")
                else:
                    failed += 1
                    print(f"    SKIP: insufficient content ({len(html_content) if html_content else 0} chars)")

            except Exception as e:
                failed += 1
                print(f"    FAIL: {e}")

            if i < len(urls):
                time.sleep(1.5)

        browser.close()

    # Generate index
    print(f"\n[3] Generating docs_index.md...")
    index_lines = [
        "# Kimi Platform Documentation Index",
        "",
        f"Crawled: {len(urls)} pages | Success: {success} | Failed: {failed}",
        f"Source: {SITEMAP_URL}",
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
    print(f"  Pages found:    {len(urls)}")
    print(f"  Successful:     {success}")
    print(f"  Failed:         {failed}")
    print(f"  Output:         {OUTPUT_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    crawl()
