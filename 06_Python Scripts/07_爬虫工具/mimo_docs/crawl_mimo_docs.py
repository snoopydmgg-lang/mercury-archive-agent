"""
MiMo Documentation Crawler
Crawls https://platform.xiaomimimo.com/docs/zh-CN/ using Playwright for JS rendering.
Outputs offline HTML, markdown, and a docs_index.md.
"""
import os
import re
import time
import json
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright
from markdownify import markdownify as mdify


BASE_URL = "https://platform.xiaomimimo.com"
START_PATH = "/docs/zh-CN/welcome"
OUTPUT_DIR = Path(__file__).parent / "output"
HTML_DIR = OUTPUT_DIR / "html"
MD_DIR = OUTPUT_DIR / "markdown"

# Patterns to skip
SKIP_PATTERNS = [
    r"/login", r"/console", r"/blog", r"/tag/",
    r"\.jpg$", r"\.png$", r"\.gif$", r"\.svg$", r"\.mp4$",
    r"/zh-CN$",  # base path without a page
]

# Only crawl docs pages under /docs/zh-CN/
DOCS_PREFIX = "/docs/zh-CN/"


def sanitize_filename(title, url_path):
    """Create an English filename from URL path."""
    # Extract last segment or meaningful part
    path = url_path.replace("/docs/zh-CN/", "").strip("/")
    if not path:
        path = "index"
    # Replace slashes with underscores, remove special chars
    name = path.replace("/", "_").replace("-", "_")
    name = re.sub(r"[^\w_]", "", name)
    name = name.strip("_")
    if not name:
        name = hashlib.md5(url_path.encode()).hexdigest()[:8]
    return name.lower()


def get_doc_links(page):
    """Extract all documentation sidebar links from the rendered page."""
    links = {}

    # Try multiple selectors for sidebar navigation
    selectors = [
        "nav a[href]",
        "aside a[href]",
        ".sidebar a[href]",
        "[class*='sidebar'] a[href]",
        "[class*='nav'] a[href]",
        "a[href*='/docs/zh-CN/']",
    ]

    for selector in selectors:
        try:
            elements = page.query_selector_all(selector)
            for el in elements:
                href = el.get_attribute("href")
                if not href:
                    continue
                # Resolve relative URLs
                full_url = urljoin(BASE_URL, href)
                parsed = urlparse(full_url)

                # Only same domain + under /docs/zh-CN/
                if parsed.netloc and parsed.netloc not in ("platform.xiaomimimo.com", "www.xiaomimimo.com"):
                    continue
                if not parsed.path.startswith(DOCS_PREFIX):
                    continue
                if parsed.path == "/docs/zh-CN/" or parsed.path == "/docs/zh-CN":
                    continue

                # Skip unwanted patterns
                skip = False
                for pat in SKIP_PATTERNS:
                    if re.search(pat, parsed.path):
                        skip = True
                        break
                if skip:
                    continue

                # Get link text
                text = el.inner_text().strip()
                if not text:
                    # Try aria-label or title
                    text = el.get_attribute("aria-label") or el.get_attribute("title") or parsed.path.split("/")[-1]

                # Normalize URL (remove fragment)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url not in links:
                    links[clean_url] = {
                        "title": text[:200],
                        "path": parsed.path,
                    }
        except Exception as e:
            print(f"  Selector '{selector}' error: {e}")

    return links


def wait_for_content(page):
    """Wait for the React app to finish rendering."""
    try:
        # Wait for main content area to have meaningful content
        page.wait_for_function("""
            () => {
                const main = document.querySelector('main') ||
                           document.querySelector('[class*="content"]') ||
                           document.querySelector('article') ||
                           document.body;
                return main && main.innerText.trim().length > 100;
            }
        """, timeout=15000)
    except Exception:
        print("  Warning: content wait timeout, proceeding anyway...")
    # Extra wait for lazy-loaded content
    page.wait_for_timeout(2000)


def extract_main_content(page):
    """Extract the main content HTML from a rendered docs page."""
    selectors = [
        "main",
        "article",
        "[class*='content']",
        ".markdown-body",
        "[class*='doc-content']",
        "#content",
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

    # Fallback: try to get document body minus nav/footer
    try:
        page.evaluate("""
            () => {
                const nav = document.querySelector('nav');
                const footer = document.querySelector('footer');
                if (nav) nav.remove();
                if (footer) footer.remove();
            }
        """)
        body = page.query_selector("body")
        if body:
            return body.inner_html()
    except Exception:
        pass

    return page.content()


def html_to_markdown(html_content):
    """Convert HTML to Markdown."""
    try:
        md = mdify(
            html_content,
            heading_style="ATX",
            bullets="-",
            strip=["script", "style", "img", "svg"],
        )
        return md
    except Exception as e:
        print(f"  Markdown conversion error: {e}")
        return ""


def crawl():
    """Main crawl function."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("MiMo Documentation Crawler")
    print(f"Start URL: {BASE_URL}{START_PATH}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        # Step 1: Load the welcome page and discover links
        print(f"\n[1] Loading start page: {BASE_URL}{START_PATH}")
        page.goto(f"{BASE_URL}{START_PATH}", wait_until="networkidle", timeout=30000)
        wait_for_content(page)

        # Extract sidebar links
        print("[2] Extracting documentation links from sidebar...")
        links = get_doc_links(page)
        print(f"    Found {len(links)} documentation pages.")

        if not links:
            print("\n[Fallback] Trying to extract links from entire page source...")
            # Try to get links from all rendered content
            all_links = page.query_selector_all("a[href*='/docs/zh-CN/']")
            for el in all_links:
                href = el.get_attribute("href")
                if href:
                    full_url = urljoin(BASE_URL, href)
                    parsed = urlparse(full_url)
                    if parsed.path.startswith(DOCS_PREFIX) and parsed.path != "/docs/zh-CN/":
                        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        text = el.inner_text().strip() or parsed.path.split("/")[-1]
                        if clean_url not in links:
                            links[clean_url] = {"title": text[:200], "path": parsed.path}
            print(f"    Fallback found {len(links)} pages.")

        if not links:
            print("ERROR: No documentation links found. Printing page title for debug:")
            print(f"  Title: {page.title()}")
            print(f"  URL: {page.url}")
            page.screenshot(path=str(OUTPUT_DIR / "debug_screenshot.png"))
            print(f"  Screenshot saved to {OUTPUT_DIR / 'debug_screenshot.png'}")
            browser.close()
            return

        # Print discovered pages
        for url, info in links.items():
            print(f"    - {info['title']} -> {info['path']}")

        # Step 2: Crawl each page
        print(f"\n[3] Crawling {len(links)} pages...")
        index_entries = []
        success = 0
        failed = 0

        for i, (url, info) in enumerate(links.items(), 1):
            path = info["path"]
            title = info["title"]
            filename = sanitize_filename(title, path)

            print(f"\n  [{i}/{len(links)}] {title}")
            print(f"    URL: {url}")
            print(f"    File: {filename}")

            try:
                # Navigate to page
                page.goto(url, wait_until="networkidle", timeout=30000)
                wait_for_content(page)

                # Wait a moment for any animations/modal popups
                page.wait_for_timeout(500)

                # Remove any modals/popups
                page.evaluate("""
                    () => {
                        document.querySelectorAll('[class*="modal"], [class*="popup"], [class*="overlay"], [class*="banner"]').forEach(el => el.remove());
                    }
                """)

                # Get actual page title
                actual_title = page.title()
                if actual_title and "Xiaomi MiMo" not in actual_title:
                    title = actual_title

                # Extract content
                html_content = extract_main_content(page)

                if html_content and len(html_content) > 200:
                    # Save HTML
                    html_path = HTML_DIR / f"{filename}.html"
                    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<meta name="source-url" content="{url}"/>
</head>
<body>
{html_content}
</body>
</html>"""
                    html_path.write_text(full_html, encoding="utf-8")

                    # Convert and save Markdown
                    md_content = html_to_markdown(html_content)
                    md_path = MD_DIR / f"{filename}.md"
                    md_header = f"# {title}\n\n> Source: {url}\n\n---\n\n"
                    md_path.write_text(md_header + md_content, encoding="utf-8")

                    index_entries.append({
                        "title": title,
                        "url": url,
                        "html": str(html_path.relative_to(OUTPUT_DIR)),
                        "markdown": str(md_path.relative_to(OUTPUT_DIR)),
                    })
                    success += 1
                    print(f"    OK (HTML: {len(full_html)} chars, MD: {len(md_content)} chars)")
                else:
                    failed += 1
                    print(f"    SKIP: insufficient content")

            except Exception as e:
                failed += 1
                print(f"    FAIL: {e}")

            # Rate limiting
            if i < len(links):
                time.sleep(1.5)

        browser.close()

    # Step 3: Generate docs_index.md
    print(f"\n[4] Generating docs_index.md...")
    index_lines = [
        "# MiMo Documentation Index",
        "",
        f"Crawled: {len(links)} pages | Success: {success} | Failed: {failed}",
        f"Source: {BASE_URL}{START_PATH}",
        "",
        "| # | Title | Original URL | HTML | Markdown |",
        "|---|-------|-------------|------|----------|",
    ]

    for i, entry in enumerate(index_entries, 1):
        index_lines.append(
            f"| {i} | {entry['title']} | {entry['url']} | "
            f"[html]({entry['html']}) | [md]({entry['markdown']}) |"
        )

    index_path = OUTPUT_DIR / "docs_index.md"
    index_path.write_text("\n".join(index_lines), encoding="utf-8")

    # Step 4: Summary
    print(f"\n{'=' * 60}")
    print(f"CRAWL COMPLETE")
    print(f"  Pages found:    {len(links)}")
    print(f"  Successful:     {success}")
    print(f"  Failed:         {failed}")
    print(f"  Output:         {OUTPUT_DIR}")
    print(f"  Index:          {index_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    crawl()
