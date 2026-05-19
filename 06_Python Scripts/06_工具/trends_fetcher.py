"""
Trends fetcher for /cheat-trends
Fetches from enabled sources, normalizes to candidate schema, rough-scores.
"""
import json
import hashlib
import sys
import os
import re
import urllib.request
import urllib.error
import ssl

COOKIE_FILE = ".cheat/cache/douyin_cookie.txt"
OUTPUT_FILE = ".cheat/cache/trends_fetched.json"

def fetch_douyin_hot():
    """Fetch douyin hot search list using stored cookie."""
    cookie_path = os.path.join(os.path.dirname(__file__), "..", "..", COOKIE_FILE)
    cookie_path = os.path.normpath(cookie_path)
    if not os.path.exists(cookie_path):
        return [], "cookie_not_found"

    with open(cookie_path, "r", encoding="utf-8") as f:
        cookie = f.read().strip()

    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?detail_list=1&count=30"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/hot",
        "Cookie": cookie
    })

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return [], f"fetch_error: {e}"

    items = []
    trending = data.get("data", {}).get("trending_list", [])
    for t in trending[:20]:
        word = t.get("word", "")
        count = t.get("video_count", 0)
        label = t.get("label", 0)
        hot = t.get("hot_value", 0)
        tag_name = {2009: "社会", 2010: "娱乐", 2011: "体育", 2012: "时尚", 2016: "知识"}.get(t.get("sentence_tag", 0), f"tag_{t.get('sentence_tag','')}")
        items.append({
            "title": word,
            "source": "douyin-hot",
            "url": f"https://www.douyin.com/hot/{t.get('group_id','')}",
            "snippet": f"抖音热搜 | 视频数:{count} | 热度:{hot} | 分类:{tag_name} | 标签:{label}",
            "raw_stats": {"video_count": count, "hot_value": hot, "tag": tag_name, "label": label}
        })
    return items, None

def fetch_bilibili_popular():
    """Fetch B站 popular videos."""
    url = "https://api.bilibili.com/x/web-interface/popular?ps=25"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return [], f"fetch_error: {e}"

    items = []
    dlist = data.get("data", {})
    if dlist is None:
        return [], f"empty_data"
    videos = dlist.get("list", [])
    if not videos:
        # Try alternative key "archives" used by some ranking endpoints
        videos = dlist.get("archives", [])
    for v in videos[:20]:
        stat = v.get("stat", {})
        owner = v.get("owner", {})
        items.append({
            "title": v.get("title", ""),
            "source": "bilibili-popular",
            "url": v.get("short_link_v2", f"https://www.bilibili.com/video/{v.get('bvid','')}"),
            "snippet": f"B站热门 | UP:{owner.get('name','')} | 播放:{stat.get('view',0)} | 点赞:{stat.get('like',0)} | {v.get('tname','')}",
            "raw_stats": {
                "view": stat.get("view", 0),
                "like": stat.get("like", 0),
                "danmaku": stat.get("danmaku", 0),
                "share": stat.get("share", 0),
                "tname": v.get("tname", ""),
                "owner": owner.get("name", ""),
                "duration": v.get("duration", 0)
            }
        })
    return items, None

# B站垂类: rid -> (source_label, niche)
BILIBILI_CATEGORIES = {
    1:   ("bilibili-anime", "动漫"),      # 动画(含MAD/AMV/MMD)
    129: ("bilibili-art", "绘画"),        # 绘画
    211: ("bilibili-design", "设计"),     # 设计
    155: ("bilibili-fashion", "时尚"),    # 时尚
    36:  ("bilibili-knowledge", "知识"),  # 知识(含社科/人文/读书)
    13:  ("bilibili-fanart", "同人"),     # 同人/手书(二次元)
}

def fetch_bilibili_category(rid, source_label, niche_name):
    """Fetch B站 category-specific ranking."""
    url = f"https://api.bilibili.com/x/web-interface/ranking/v2?rid={rid}&type=all&ps=12"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        return [], f"fetch_error: {e}"

    items = []
    dlist = data.get("data", {})
    if dlist is None:
        return [], f"empty_data"
    videos = dlist.get("list", [])
    if not videos:
        # Try alternative key "archives" used by some ranking endpoints
        videos = dlist.get("archives", [])
    for v in videos[:12]:
        stat = v.get("stat", {})
        owner = v.get("owner", {})
        items.append({
            "title": v.get("title", ""),
            "source": source_label,
            "url": v.get("short_link_v2", f"https://www.bilibili.com/video/{v.get('bvid','')}"),
            "snippet": f"B站{niche_name} | UP:{owner.get('name','')} | 播放:{stat.get('view',0)} | 点赞:{stat.get('like',0)} | {v.get('tname','')}",
            "raw_stats": {
                "view": stat.get("view", 0),
                "like": stat.get("like", 0),
                "danmaku": stat.get("danmaku", 0),
                "share": stat.get("share", 0),
                "tname": v.get("tname", ""),
                "owner": owner.get("name", ""),
                "duration": v.get("duration", 0)
            }
        })
    return items, None

def make_id(source, title, url):
    """Generate dedupe id: sha256(source + normalized_title + url_path)[:12]"""
    title_norm = re.sub(r'[^\w一-鿿]', '', title.lower())[:30]
    url_path = re.sub(r'https?://[^/]+', '', url)[:50]
    raw = f"{source}{title_norm}{url_path}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def rough_score(item):
    """
    Rough rubric v0 scoring based on snapshot title + metadata only.
    v0 dims: ER, HP, QL, NA, AB, SR, SAT. Each 0-5.
    composite = (ER+HP+QL+NA+AB+SR+SAT) / 7 * 2.0
    NOTE: Only title/metadata available; HP/QL/NA/SAT are inherently uncertain
    from title alone. We score what we can and mark the rest as neutral (2-3).
    """
    title = item.get("title", "")
    source = item.get("source", "")
    stats = item.get("raw_stats", {})

    # --- AB: Audience Breadth (best signal from hot-list data) ---
    if source == "douyin-hot":
        vc = stats.get("video_count", 1)
        label = stats.get("label", 0)
        scores_ab = 3 if vc >= 3 else (2 if vc >= 2 else 1)
        if label >= 8:
            scores_ab = min(5, scores_ab + 1)
    elif source == "bilibili-popular":
        view = stats.get("view", 0)
        if view > 3_000_000:
            scores_ab = 5
        elif view > 1_000_000:
            scores_ab = 4
        elif view > 400_000:
            scores_ab = 3
        else:
            scores_ab = 2
    else:
        scores_ab = 2

    # --- SR: Social Resonance (topic signals from title) ---
    sr_strong = ["裁员", "失业", "房价", "工资", "内卷", "躺平", "焦虑", "教育", "结婚", "离婚",
                  "AI", "人工智能", "算法", "大数据", "隐私", "环保", "性别", "阶层"]
    sr_mild = ["工作", "生活", "父母", "孩子", "朋友", "关系", "钱", "健康", "社会", "00后",
               "年轻人", "职场", "高考", "考研", "考公", "县城", "农村", "城市"]
    sr_strong_hits = sum(1 for k in sr_strong if k in title)
    sr_mild_hits = sum(1 for k in sr_mild if k in title)
    scores_sr = min(5, 2 + sr_strong_hits * 2 + sr_mild_hits)

    # --- ER: Emotional Resonance (weak signal from title words) ---
    er_strong = ["泪目", "破防", "感动", "心疼", "崩溃", "绝望", "骄傲", "震撼", "愤怒", "不甘"]
    er_mild = ["终于", "真的", "为什么", "凭什么", "无奈", "遗憾", "幸好", "还好"]
    er_strong_hits = sum(1 for k in er_strong if k in title)
    er_mild_hits = sum(1 for k in er_mild if k in title)
    scores_er = min(5, 2 + er_strong_hits * 2 + er_mild_hits)

    # --- HP: Hook Potential (weak signal: title structure) ---
    hook_signals = ["为什么", "竟然", "居然", "原来", "终于知道", "真相", "秘密", "揭秘",
                    "!", "？", "..." , "…"]
    hook_hits = sum(1 for k in hook_signals if k in title)
    scores_hp = min(5, 2 + hook_hits)

    # --- QL: Quotable Lines (weak signal: title length & structure) ---
    if len(title) <= 10:
        scores_ql = 3
    elif len(title) <= 20:
        scores_ql = 2
    else:
        scores_ql = 1
    # Bonus if title contains a quotable structure
    if any(c in title for c in ["「", "」", '"', '"', "：", "|"]):
        scores_ql = min(5, scores_ql + 1)

    # --- NA: Narrativity (weakest signal from title) ---
    narrative_signals = ["从...到", "经历了", "那天", "当我", "后来", "然后", "最后", "终于"]
    na_hits = sum(1 for k in narrative_signals if k in title)
    scores_na = min(5, 2 + na_hits)

    # --- SAT: Satire Depth (usually 2-3 for sincere content; title rarely reveals) ---
    satire_signals = ["讽刺", "反讽", "自嘲", "幽默", "荒诞", "黑色幽默", "一本正经"]
    sat_hits = sum(1 for k in satire_signals if k in title)
    scores_sat = min(5, 2 + sat_hits)

    # Composite
    dims = {"ER": scores_er, "HP": scores_hp, "QL": scores_ql, "NA": scores_na,
            "AB": scores_ab, "SR": scores_sr, "SAT": scores_sat}
    composite = sum(dims.values()) / 7 * 2.0
    composite = round(composite, 1)

    # Bucket (percentile-style, rough)
    if composite >= 8.0:
        bucket = "30-100w+"
    elif composite >= 7.0:
        bucket = "10-30w"
    elif composite >= 6.0:
        bucket = "1-10w"
    else:
        bucket = "<1w"

    # Rationale: which dims stand out
    top_dims = sorted(dims.items(), key=lambda x: x[1], reverse=True)
    high_dims = [d for d, s in top_dims if s >= 4]
    if high_dims:
        rationale = f"{'+'.join(high_dims[:3])}高"
    elif top_dims[0][1] >= 3:
        rationale = f"{top_dims[0][0]}中等偏高"
    else:
        rationale = "各维度偏低，需展开稿后才能判断"

    return {
        "composite": composite,
        "scores": dims,
        "bucket": bucket,
        "rationale": rationale
    }

def main():
    os.chdir(os.path.join(os.path.dirname(__file__), "..", ".."))

    all_items = []
    errors = {}

    # Fetch douyin-hot
    dy_items, dy_err = fetch_douyin_hot()
    if dy_err:
        errors["douyin-hot"] = dy_err
        print(f"  douyin-hot: {dy_err}", file=sys.stderr)
    else:
        print(f"  douyin-hot: {len(dy_items)} 条", file=sys.stderr)

    # Fetch bilibili-popular
    bl_items, bl_err = fetch_bilibili_popular()
    if bl_err:
        errors["bilibili-popular"] = bl_err
        print(f"  bilibili-popular: {bl_err}", file=sys.stderr)
    else:
        print(f"  bilibili-popular: {len(bl_items)} 条", file=sys.stderr)

    # Fetch B站 垂类 (art/design/anime/books)
    cat_items = []
    for rid, (src_label, niche_name) in BILIBILI_CATEGORIES.items():
        items, err = fetch_bilibili_category(rid, src_label, niche_name)
        if err:
            errors[src_label] = err
            print(f"  {src_label} ({niche_name}): {err}", file=sys.stderr)
        else:
            cat_items.extend(items)
            print(f"  {src_label} ({niche_name}): {len(items)} 条", file=sys.stderr)

    # Add ids and score
    for item in dy_items + bl_items + cat_items:
        item["id"] = make_id(item["source"], item["title"], item["url"])
        score = rough_score(item)
        item.update(score)

    all_items = dy_items + bl_items + cat_items

    # Sort by composite desc
    all_items.sort(key=lambda x: x["composite"], reverse=True)

    output = {
        "fetched_at": "2026-05-08",
        "errors": errors,
        "total": len(all_items),
        "items": all_items
    }

    # Output JSON to stdout for consumption
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    sys.stdout.reconfigure(encoding='utf-8')
    print(json_str)

    # Also save to cache
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(json_str)

if __name__ == "__main__":
    main()
