"""Parse 4 speech MD files and generate a single swipeable HTML for on-screen presentation."""
from pathlib import Path
import re
import html as html_mod

INBOX = Path(r"E:\1.work\douyin\1.shuixing\00_InBox_收件箱")
FILES = [
    "1_全面机制升维_逐页演讲稿.md",
    "2_机制突破_逐页演讲稿.md",
    "3_疗效升维_逐页演讲稿.md",
    "4_安全革新_逐页演讲稿.md",
]

# Unnumbered section name → number mapping
SECTION_MAP = {
    "本页核心信息": "1",
    "建议演讲稿": "2",
    "利益转化话术": "3",
    "医生沟通引导句": "4",
    "承上启下过渡句": "5",
    "合规提醒": "6",
}


def parse_md(filepath: Path) -> dict:
    text = filepath.read_text(encoding="utf-8")

    title_m = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else filepath.stem

    page_pattern = r"## 第\s*(\d+)\s*页[^\n]*\n"
    splits = list(re.finditer(page_pattern, text))

    pages = []
    for i, m in enumerate(splits):
        page_num = int(m.group(1))
        start = m.end()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        content = text[start:end].strip()

        # Extract page title from header line
        header_line = m.group(0).strip()
        page_title = header_line  # default
        # Try to extract text after 第N页
        title_extra = re.search(r"第\s*\d+\s*页[—\-——·：:\s]*(.+)", header_line)
        if title_extra:
            page_title = title_extra.group(1).strip()

        page = {
            "num": page_num,
            "title_line": header_line,
            "page_title": page_title,
            "sections": {},
        }

        # Try numbered format first: ### 1. 本页核心信息
        sec_numbered = list(re.finditer(r"###\s+(\d+)\.\s+(.+?)\s*\n", content))
        if sec_numbered:
            for j, sm in enumerate(sec_numbered):
                sec_num = sm.group(1)
                sec_name = sm.group(2).strip()
                sec_start = sm.end()
                sec_end = sec_numbered[j + 1].start() if j + 1 < len(sec_numbered) else len(content)
                sec_text = content[sec_start:sec_end].strip()
                page["sections"][sec_num] = {"name": sec_name, "text": sec_text}
        else:
            # Try unnumbered format: ### 本页核心信息 / ### 建议演讲稿
            sec_unnumbered = list(re.finditer(r"###\s+(.+?)\s*\n", content))
            for j, sm in enumerate(sec_unnumbered):
                sec_name_raw = sm.group(1).strip()
                # Skip if it looks like a number prefix (already handled)
                if re.match(r"^\d+\.", sec_name_raw):
                    continue
                sec_num = SECTION_MAP.get(sec_name_raw)
                if sec_num is None:
                    continue
                sec_start = sm.end()
                sec_end = sec_unnumbered[j + 1].start() if j + 1 < len(sec_unnumbered) else len(content)
                sec_text = content[sec_start:sec_end].strip()
                page["sections"][sec_num] = {"name": sec_name_raw, "text": sec_text}

        pages.append(page)

    return {"title": title, "pages": pages}


def escape(s: str) -> str:
    return html_mod.escape(s)


def md_to_html(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    lines = text.split("\n")
    out = []
    in_list = False
    for line in lines:
        list_m = re.match(r"^(\d+)\.\s+(.+)", line)
        if list_m:
            if not in_list:
                out.append('<ol class="guide-list">')
                in_list = True
            out.append(f"<li>{list_m.group(2)}</li>")
            continue
        else:
            if in_list:
                out.append("</ol>")
                in_list = False
        if re.match(r"^---+$", line.strip()):
            out.append("<hr>")
            continue
        if not line.strip():
            out.append("<br>")
            continue
        if line.startswith("- ") and not line.startswith("- **"):
            out.append(f"<p class='dash-item'>— {line[2:]}</p>")
            continue
        out.append(f"<p>{line}</p>")
    if in_list:
        out.append("</ol>")
    return "\n".join(out)


def build_html(all_data: list) -> str:
    # Build deck data as JSON for JS
    decks = []
    for data in all_data:
        pages_out = []
        for page in data["pages"]:
            speech = page["sections"].get("2", {}).get("text", "")
            core = page["sections"].get("1", {}).get("text", "")
            benefit = page["sections"].get("3", {}).get("text", "")
            guide = page["sections"].get("4", {}).get("text", "")
            transition = page["sections"].get("5", {}).get("text", "")
            compliance = page["sections"].get("6", {}).get("text", "")

            pages_out.append({
                "num": page["num"],
                "title": page["page_title"],
                "speech": md_to_html(speech),
                "core": md_to_html(core),
                "benefit": md_to_html(benefit),
                "guide": md_to_html(guide),
                "transition": md_to_html(transition),
                "compliance": md_to_html(compliance),
            })
        decks.append({
            "title": data["title"],
            "pages": pages_out,
        })

    decks_json = json.dumps(decks, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>凯捷乐® 科室会演讲稿</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
    background: #F5F4F0;
    color: #2D2B2A;
    overflow: hidden;
    height: 100vh;
    height: 100dvh;
    width: 100vw;
    user-select: none;
    -webkit-user-select: none;
    touch-action: pan-x;
}}

/* Top bar */
.top-bar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 6px 20px;
    background: #fff;
    border-bottom: 1px solid #e0dcd5;
}}
.top-bar .brand {{ font-size: 14px; color: #D36B4D; font-weight: 700; }}
.deck-tabs {{ display: flex; gap: 4px; flex-wrap: wrap; }}
.deck-tab {{
    padding: 5px 12px; border: 1.5px solid #D36B4D; background: #fff;
    color: #D36B4D; border-radius: 4px; cursor: pointer; font-size: 12px;
    font-weight: 600; transition: all 0.15s;
}}
.deck-tab:hover {{ background: #fdf0eb; }}
.deck-tab.active {{ background: #D36B4D; color: #fff; }}
.top-bar .right-info {{ font-size: 12px; color: #999; }}

/* Main stage */
.stage {{
    position: fixed; top: 42px; left: 0; right: 0; bottom: 56px;
    display: flex; align-items: flex-start; justify-content: flex-start;
    padding: 16px;
    transition: right 0.25s ease;
}}
.stage.shifted {{ right: 380px; }}
.page-card {{
    display: none;
    width: 100%; max-width: 900px; height: 100%;
    padding: 28px 40px;
    overflow-y: auto;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    -webkit-overflow-scrolling: touch;
}}
.page-card.active {{ display: block; }}

.page-num-badge {{
    display: inline-block;
    font-size: 12px; font-weight: 700; color: #D36B4D;
    background: #fdf0eb;
    padding: 3px 14px; border-radius: 20px; letter-spacing: 1px;
    margin-bottom: 16px;
}}

.speech-body {{ font-size: 19px; line-height: 2.1; color: #2D2B2A; }}
.speech-body p {{ margin-bottom: 6px; }}
.speech-body strong {{ color: #D36B4D; font-weight: 700; }}
.speech-body code {{ background: #f7f5f2; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}

/* Aux panel */
.aux-toggle {{
    position: fixed; right: 16px; bottom: 72px; z-index: 90;
    width: 40px; height: 40px; border-radius: 50%; border: 1.5px solid #D36B4D;
    background: #fff; color: #D36B4D; font-size: 18px; cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: all 0.2s;
}}
.aux-toggle:hover {{ background: #D36B4D; color: #fff; }}

.aux-panel {{
    position: fixed; right: 0; top: 42px; bottom: 56px; z-index: 95;
    width: 380px; max-width: 85vw; background: #fff; border-left: 1px solid #e0dcd5;
    overflow-y: auto; padding: 16px 20px;
    transform: translateX(100%); transition: transform 0.25s ease;
    box-shadow: -4px 0 20px rgba(0,0,0,0.08);
    -webkit-overflow-scrolling: touch;
}}
.aux-panel.open {{ transform: translateX(0); }}

.aux-close {{
    position: sticky; top: 0; float: right;
    width: 32px; height: 32px; border-radius: 50%; border: none;
    background: #f0ece6; color: #666; font-size: 18px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    z-index: 10; margin-bottom: -24px;
}}
.aux-close:hover {{ background: #D36B4D; color: #fff; }}

.aux-panel h4 {{
    font-size: 11px; color: #D36B4D; letter-spacing: 1.5px;
    margin: 16px 0 6px; text-transform: uppercase;
}}
.aux-panel h4:first-child {{ margin-top: 0; }}
.aux-panel p, .aux-panel li {{
    font-size: 14px; color: #666; line-height: 1.6;
}}
.aux-panel ol {{ padding-left: 18px; }}
.aux-panel .guide-list li {{ margin-bottom: 4px; }}

/* Bottom bar */
.bot-bar {{
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
    display: flex; align-items: center; justify-content: center; gap: 12px;
    padding: 8px 16px; background: #fff; border-top: 1px solid #e0dcd5;
}}
.bot-bar button {{
    background: #fff; border: 1.5px solid #D36B4D; color: #D36B4D;
    padding: 5px 16px; border-radius: 6px; cursor: pointer; font-size: 13px;
    font-weight: 600; transition: all 0.15s;
}}
.bot-bar button:hover {{ background: #D36B4D; color: #fff; }}
.bot-bar button:disabled {{ opacity: 0.25; cursor: default; border-color: #ccc; color: #ccc; }}
.bot-bar button:disabled:hover {{ background: #fff; color: #ccc; }}
.page-counter {{
    font-size: 14px; color: #D36B4D; font-weight: 600; min-width: 56px; text-align: center;
}}
.page-jump {{
    display: flex; align-items: center; gap: 4px;
}}
.page-jump input {{
    width: 44px; padding: 5px 6px; border: 1.5px solid #d5cfc7;
    border-radius: 4px; text-align: center; font-size: 13px; font-weight: 600;
    color: #2D2B2A; background: #fdfcf9;
}}
.page-jump input:focus {{ outline: none; border-color: #D36B4D; }}
.page-jump span {{ font-size: 12px; color: #999; }}

/* Swipe hint animation */
.swipe-hint {{
    position: fixed; bottom: 70px; left: 50%; transform: translateX(-50%);
    font-size: 12px; color: #ccc; pointer-events: none;
    animation: fadeHint 3s ease-out forwards;
}}
@keyframes fadeHint {{
    0% {{ opacity: 0; }}
    20% {{ opacity: 1; }}
    80% {{ opacity: 1; }}
    100% {{ opacity: 0; }}
}}

/* Print */
@media print {{
    body {{ background: #fff; color: #000; overflow: visible; height: auto; }}
    .top-bar, .bot-bar, .aux-toggle, .aux-panel, .swipe-hint {{ display: none !important; }}
    .stage {{ position: static; }}
    .page-card {{ display: block !important; background: #fff; box-shadow: none;
        border: 1px solid #ddd; margin-bottom: 16px; page-break-inside: avoid;
        border-radius: 0; max-width: 100%; height: auto; padding: 16px 20px; }}
    .page-card.active {{ display: block !important; }}
    .speech-body {{ font-size: 13px; line-height: 1.6; color: #000; }}
    .speech-body strong {{ color: #000; }}
    .page-num-badge {{ background: #eee; color: #555; }}
}}

/* Tablet & Mobile tweaks */
@media (max-width: 900px) {{
    .top-bar {{ padding: 5px 12px; }}
    .top-bar .brand {{ font-size: 13px; }}
    .deck-tab {{ padding: 5px 10px; font-size: 11px; }}
    .top-bar .right-info {{ display: none; }}
    .stage {{ top: 40px; bottom: 52px; padding: 10px; justify-content: center; }}
    .stage.shifted {{ right: 0; }}
    .page-card {{ padding: 24px 24px; border-radius: 8px; max-width: 100%; }}
    .speech-body {{ font-size: 18px; line-height: 2; }}
    .bot-bar {{ padding: 7px 12px; gap: 8px; }}
    .bot-bar button {{ padding: 6px 14px; font-size: 13px; }}
    .page-jump input {{ width: 40px; padding: 5px 4px; font-size: 13px; }}
    .aux-panel {{ width: 100vw; max-width: 100vw; }}
    .aux-panel.open + .stage {{ right: 0; }} /* on mobile, panel overlays fully */
    .aux-toggle {{ right: 10px; bottom: 68px; width: 44px; height: 44px; font-size: 20px; }}
}}
</style>
</head>
<body>

<div class="top-bar">
    <span class="brand">凯捷乐<sup>&reg;</sup> 科室会演讲稿</span>
    <div class="deck-tabs" id="deckTabs"></div>
    <span class="right-info">演讲人：贺杉</span>
</div>

<div class="stage" id="stage"></div>

<div class="swipe-hint" id="swipeHint">← 左右滑动翻页 →</div>

<button class="aux-toggle" id="auxToggle" title="辅助信息面板">i</button>
<div class="aux-panel" id="auxPanel">
    <button class="aux-close" id="auxClose" title="关闭面板">&times;</button>
    <div id="auxContent"></div>
</div>

<div class="bot-bar">
    <button id="btnPrev">← 上一页</button>
    <span class="page-counter" id="pageCounter">1 / 1</span>
    <button id="btnNext">下一页 →</button>
    <div class="page-jump">
        <input type="number" id="jumpInput" min="1" placeholder="页" title="输入页码后回车跳转">
        <span id="jumpTotal">/ 1</span>
    </div>
</div>

<script>
var DECKS = {decks_json};
var currentDeck = 0;
var currentPage = 0;

function renderDeckTabs() {{
    var html = '';
    DECKS.forEach(function(d, i) {{
        var cls = i === currentDeck ? 'active' : '';
        var label = (i + 1) + '. ' + d.title.replace(/——逐页演讲稿/, '').replace(/《|》/g, '').slice(0, 14);
        html += '<button class="deck-tab ' + cls + '" onclick="switchDeck(' + i + ')">' + label + '</button>';
    }});
    document.getElementById('deckTabs').innerHTML = html;
}}

var stageEl = null;
function renderStage() {{
    var deck = DECKS[currentDeck];
    var html = '';
    deck.pages.forEach(function(p, i) {{
        var cls = i === currentPage ? 'active' : '';
        html += '<div class="page-card ' + cls + '" data-idx="' + i + '">';
        html += '<div class="page-num-badge">第 ' + p.num + ' 页 · ' + escapeHtml(p.title) + '</div>';
        html += '<div class="speech-body">' + p.speech + '</div>';
        html += '</div>';
    }});
    document.getElementById('stage').innerHTML = html;
    stageEl = document.getElementById('stage');
    updateCounter();
    updateAuxPanel();
    // Scroll active card to top
    var active = document.querySelector('.page-card.active');
    if (active) active.scrollTop = 0;
}}

function escapeHtml(s) {{
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function updateCounter() {{
    var deck = DECKS[currentDeck];
    var total = deck.pages.length;
    document.getElementById('pageCounter').textContent = (currentPage + 1) + ' / ' + total;
    document.getElementById('btnPrev').disabled = currentPage === 0;
    document.getElementById('btnNext').disabled = currentPage === total - 1;
    document.getElementById('jumpTotal').textContent = '/ ' + total;
    document.getElementById('jumpInput').max = total;
    document.getElementById('jumpInput').value = '';
}}

function updateAuxPanel() {{
    var p = DECKS[currentDeck].pages[currentPage];
    var html = '<h4>核心信息</h4>' + (p.core || '<p>—</p>');
    html += '<h4>利益转化</h4>' + (p.benefit || '<p>—</p>');
    html += '<h4>沟通引导句</h4>' + (p.guide || '<p>—</p>');
    html += '<h4>过渡句</h4>' + (p.transition || '<p>—</p>');
    html += '<h4>合规提醒</h4>' + (p.compliance || '<p>—</p>');
    document.getElementById('auxContent').innerHTML = html;
}}

function closeAux() {{
    auxOpen = false;
    document.getElementById('auxPanel').classList.remove('open');
    document.getElementById('stage').classList.remove('shifted');
}}

function openAux() {{
    auxOpen = true;
    document.getElementById('auxPanel').classList.add('open');
    document.getElementById('stage').classList.add('shifted');
}}

function switchDeck(idx) {{
    currentDeck = idx;
    currentPage = 0;
    renderDeckTabs();
    renderStage();
}}

function goToPage(n) {{
    var deck = DECKS[currentDeck];
    var idx = n - 1;
    if (idx >= 0 && idx < deck.pages.length) {{
        currentPage = idx;
        renderStage();
    }}
}}

function goNext() {{
    var deck = DECKS[currentDeck];
    if (currentPage < deck.pages.length - 1) {{
        currentPage++;
        renderStage();
    }}
}}

function goPrev() {{
    if (currentPage > 0) {{
        currentPage--;
        renderStage();
    }}
}}

// Button bindings
document.getElementById('btnNext').addEventListener('click', goNext);
document.getElementById('btnPrev').addEventListener('click', goPrev);

// Page jump
document.getElementById('jumpInput').addEventListener('keydown', function(e) {{
    if (e.key === 'Enter') {{
        var n = parseInt(this.value, 10);
        if (n >= 1) goToPage(n);
        this.value = '';
    }}
}});

// Aux toggle
var auxOpen = false;
document.getElementById('auxToggle').addEventListener('click', function() {{
    auxOpen ? closeAux() : openAux();
}});
document.getElementById('auxClose').addEventListener('click', closeAux);

// Close aux by tapping outside (on the stage area)
document.getElementById('stage').addEventListener('click', function(e) {{
    if (auxOpen && e.target === document.getElementById('stage')) closeAux();
}});

// Swipe hint - show once, then auto-hide
var hintShown = false;
function showSwipeHint() {{
    if (hintShown) return;
    hintShown = true;
    var hint = document.getElementById('swipeHint');
    hint.style.display = 'block';
    setTimeout(function() {{ hint.style.display = 'none'; }}, 3000);
}}

// Keyboard
document.addEventListener('keydown', function(e) {{
    if (e.target.tagName === 'INPUT') return; // don't hijack input fields
    switch(e.key) {{
        case 'ArrowRight': case 'ArrowDown': case 'PageDown': goNext(); break;
        case 'ArrowLeft': case 'ArrowUp': case 'PageUp': goPrev(); break;
        case 'Home': goToPage(1); break;
        case 'End': goToPage(DECKS[currentDeck].pages.length); break;
        case 'a': case 'A': auxOpen ? closeAux() : openAux(); break;
        case 'p': case 'P': window.print(); break;
        case '1': switchDeck(0); break;
        case '2': switchDeck(1); break;
        case '3': switchDeck(2); break;
        case '4': switchDeck(3); break;
    }}
}});

// Touch swipe
var touchStartX = 0, touchStartY = 0;
document.addEventListener('touchstart', function(e) {{
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
}}, {{ passive: true }});
document.addEventListener('touchend', function(e) {{
    var dx = e.changedTouches[0].clientX - touchStartX;
    var dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 40) {{
        if (dx < 0) goNext(); else goPrev();
    }}
}});

// Mouse wheel horizontal scroll on trackpad
var wheelAccum = 0;
document.addEventListener('wheel', function(e) {{
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {{
        wheelAccum += e.deltaX;
        if (wheelAccum > 80) {{ goNext(); wheelAccum = 0; }}
        else if (wheelAccum < -80) {{ goPrev(); wheelAccum = 0; }}
    }}
}}, {{ passive: true }});

// Init
renderDeckTabs();
renderStage();
showSwipeHint();
</script>
</body>
</html>"""


def main():
    import json as _json
    global json
    json = _json

    all_data = []
    for fname in FILES:
        fpath = INBOX / fname
        if fpath.exists():
            data = parse_md(fpath)
            all_data.append(data)
            speech_count = sum(1 for p in data["pages"] if p["sections"].get("2"))
            print(f"Parsed: {fname} ({len(data['pages'])} pages, {speech_count} with speech)")
        else:
            print(f"MISSING: {fname}")

    html = build_html(all_data)
    out_path = INBOX / "凯捷乐_科室会演讲稿.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"\nHTML written: {out_path}")
    print(f"File size: {out_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
