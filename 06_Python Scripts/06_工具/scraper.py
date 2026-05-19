#!/usr/bin/env python3
"""
网页爬取工具 - 使用 requests + BeautifulSoup
"""
import sys
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def scrape_url(url):
    """爬取单个URL并转换为Markdown"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除无用标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()

        # 提取主要内容
        main_content = soup.find('main') or soup.find('article') or soup.find('body')

        if main_content:
            # 转换为Markdown
            markdown_content = md(str(main_content))
            return markdown_content
        else:
            return "未找到主要内容"

    except Exception as e:
        return f"爬取失败: {str(e)}"

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("请输入URL: ").strip()

    print(f"正在爬取: {url}")
    content = scrape_url(url)
    print(content)
