"""Scrape TFT comp data from datatft.com using Playwright."""
import json
import sys
from playwright.sync_api import sync_playwright

def scrape_comps():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("[1/4] Navigating to datatft.com/comps ...")
        page.goto("https://www.datatft.com/comps", wait_until="networkidle", timeout=60000)

        # Wait for the iframe to load
        print("[2/4] Waiting for comps data to render ...")
        page.wait_for_timeout(5000)

        # The comps page loads an iframe to intent-wheel.html
        # Let's try to get the iframe content
        frames = page.frames
        print(f"Found {len(frames)} frames")

        # Look for the intent-wheel iframe
        target_frame = None
        for frame in frames:
            if "intent-wheel" in frame.url or "comps" in frame.url:
                target_frame = frame
                print(f"  Target frame: {frame.url[:100]}")
                break

        if not target_frame:
            # Try the main page
            target_frame = page
            print("  Using main page")

        # Wait more for data
        target_frame.wait_for_timeout(3000)

        # Try to extract visible text content
        print("[3/4] Extracting page content ...")

        # Get all text content
        body_text = target_frame.evaluate("() => document.body?.innerText || ''")
        print(f"Body text length: {len(body_text)}")

        # Try to get structured data from the DOM
        # Look for comp cards/items
        comp_data = target_frame.evaluate("""() => {
            const results = [];

            // Try to find comp items
            const compElements = document.querySelectorAll('.comp-item, .comp-card, [class*="comp"], [class*="tier"], .strategy-item');
            console.log('Found elements:', compElements.length);

            compElements.forEach(el => {
                results.push({
                    className: el.className,
                    text: el.innerText?.substring(0, 500),
                    html: el.outerHTML?.substring(0, 1000)
                });
            });

            return results;
        }""")

        print(f"Found {len(comp_data)} comp elements")

        # Also try to intercept network requests for API data
        # Let's check for any data in window/localStorage
        stored_data = target_frame.evaluate("""() => {
            const data = {};
            try {
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key.includes('comp') || key.includes('tier') || key.includes('data') || key.includes('game')) {
                        data[key] = localStorage.getItem(key)?.substring(0, 2000);
                    }
                }
            } catch(e) {}
            return data;
        }""")
        print(f"LocalStorage data keys: {list(stored_data.keys())}")

        # Save what we have
        output = {
            "body_text_preview": body_text[:5000],
            "comp_elements": comp_data[:20],
            "localStorage": stored_data
        }

        output_path = "E:/1.work/douyin/1.shuixing/04_数据分析结果/datatft_comps_raw.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"[4/4] Saved raw data to {output_path}")

        browser.close()
        return output

if __name__ == "__main__":
    data = scrape_comps()
    print("\n--- Preview ---")
    print(data["body_text_preview"][:2000])
