import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# 获取用户输入的URL列表
def get_user_urls():
    print("请输入要抓取的URL，多个URL请用逗号分隔：")
    user_input = input("URLs: ")
    # 分割输入的URL并去除空白
    urls = [url.strip() for url in user_input.split(',') if url.strip()]
    if not urls:
        print("未输入URL，使用默认URL列表")
        # 默认URL列表
        return [
            "https://www.claude-cn.org/posts/Claude-code-complete-guide",
            "https://www.claude-cn.org/posts/Claude-code-commands-guide",
            "https://www.claude-cn.org/posts/Claude-code-16-practical-tips",
            "https://www.claude-cn.org/posts/Claude-code-best-practices",
            "https://www.claude-cn.org/claude-code-tutorials",
            "https://www.claude-cn.org/docs/"
        ]
    return urls

async def fetch_and_parse(page, url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 使用 domcontentloaded 提升执行速度，无需等待所有图片加载
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html_content = await page.content()
            
            # DOM 清洗：移除无用标签
            soup = BeautifulSoup(html_content, 'html.parser')
            for element in soup(['nav', 'footer', 'script', 'style', 'aside']):
                element.decompose()
                
            # 提取核心内容区
            if "claude-cn.org" in url:
                # 针对 claude-cn.org 的 DOM 结构，优先提取 class 为 prose 或 article 的 div
                main_content = soup.find('div', class_='prose') or soup.find('div', class_='article') or soup.find('main') or soup.find('body')
            else:
                # 其他网站使用默认策略
                main_content = soup.find('main') or soup.find('body')
            
            if not main_content:
                return f"## {url}\n\n**Error**: 无法定位核心内容块。\n\n---\n\n"
                
            # 转换为 Markdown
            markdown_text = md(str(main_content), heading_style="ATX")
            return f"## Source: {url}\n\n{markdown_text}\n\n---\n\n"
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[!] 抓取 {url} 失败，第 {attempt + 1} 次尝试，将重试...")
                await page.wait_for_timeout(1000 * (attempt + 1))  # 递增延迟
                continue
            return f"## {url}\n\n**Error**: {str(e)}\n\n---\n\n"

async def main():
    async with async_playwright() as p:
        # 启动无头浏览器，使用系统安装的Chrome
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 获取用户输入的URL列表
        target_urls = get_user_urls()
        
        with open("Claude_Code_Manual.md", "w", encoding="utf-8") as f:
            f.write("# Claude Code 知识库汇总\n\n")
            
            for url in target_urls:
                print(f"[*] 正在抓取: {url}")
                md_content = await fetch_and_parse(page, url)
                f.write(md_content)
                # 随机延迟，降低被封禁概率
                await page.wait_for_timeout(2000) 
                
        await browser.close()
        print("[+] 抓取完成，数据已写入 Claude_Code_Manual.md")

if __name__ == "__main__":
    asyncio.run(main())
