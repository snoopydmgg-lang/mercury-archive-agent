# -*- coding: utf-8 -*-
"""名画里的秘密 — YouTube 影视镜头素材下载
从收件箱表格提取搜索关键词，用 yt-dlp + deno + cookies 搜索并下载短片片段
"""
import subprocess, os, sys, io, re, time, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TABLE_FILE = "00_InBox_收件箱/目录画作与影视作品.md"
OUTPUT_DIR = "01_Projects_制作中/名画里的秘密/04_素材_影视镜头"
LOG_FILE = os.path.join(OUTPUT_DIR, "download_log.json")
COOKIE_FILE = "06_Python Scripts/06_工具/youtube_cookies.txt"

YT_DLP = "C:/Users/Administrator/AppData/Local/Programs/Python/Python310/Scripts/yt-dlp.exe"
DENO_DIR = "C:/Users/Administrator/AppData/Local/Microsoft/WinGet/Packages/DenoLand.Deno_Microsoft.Winget.Source_8wekyb3d8bbwe"

# Parse table
with open(TABLE_FILE, "r", encoding="utf-8") as f:
    content = f.read()

rows = []
for line in content.split("\n"):
    line = line.strip()
    if not line.startswith("|") or "---" in line or "目录画作" in line or "页码" in line:
        continue
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 7:
        continue
    painting = parts[1].strip("*")
    movie = parts[3].strip("*")
    keywords = parts[6].strip()
    if keywords and keywords != "搜索关键词":
        rows.append({"painting": painting, "movie": movie, "keywords": keywords})

print(f"Parsed {len(rows)} entries")

# Deduplicate by movie
seen = set()
unique = []
for r in rows:
    if r["movie"].lower() not in seen:
        seen.add(r["movie"].lower())
        unique.append(r)
    else:
        for u in unique:
            if u["movie"].lower() == r["movie"].lower():
                if r["keywords"] not in u["keywords"]:
                    u["keywords"] += " " + r["keywords"]
                break

print(f"Deduped to {len(unique)} movies")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load log
log = {}
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)

# Build env with deno in PATH
env = os.environ.copy()
env["PATH"] = DENO_DIR + os.pathsep + env.get("PATH", "")
env["HTTP_PROXY"] = "http://127.0.0.1:7892"
env["HTTPS_PROXY"] = "http://127.0.0.1:7892"

results = []

for i, item in enumerate(unique):
    movie = item["movie"]
    keywords = item["keywords"]
    painting = item["painting"]

    # Safe ASCII filename prefix
    safe_movie = re.sub(r'[\\/*?:"<>|]', '', movie)
    safe_movie = safe_movie.replace(" ", "_").replace("《", "").replace("》", "")
    # Use index to avoid path issues
    out_template = os.path.join(OUTPUT_DIR, f"{i+1:02d}_{safe_movie}_%(id)s.%(ext)s")

    if movie in log:
        print(f"[{i+1}/{len(unique)}] {movie} - cached, skip")
        results.append({"movie": movie, "painting": painting, "status": "cached", "path": log[movie]})
        continue

    print(f"[{i+1}/{len(unique)}] {movie}: {keywords[:60]}")

    cmd = [
        YT_DLP,
        f"ytsearch1:{keywords}",
        "--cookies", COOKIE_FILE,
        "--format", "best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best",
        "--match-filter", "duration < 600",
        "--max-downloads", "1",
        "--no-playlist",
        "--output", out_template,
        "--print", "after_move:filepath",
        "--no-warnings",
        "--socket-timeout", "30",
        "--retries", "3",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                                cwd="E:/1.work/douyin/1.shuixing", env=env)
        stdout_lines = result.stdout.strip().split("\n")
        stderr = result.stderr.strip()

        # Find downloaded file
        downloaded_path = None
        for line in stdout_lines:
            line = line.strip()
            if line and os.path.exists(line):
                downloaded_path = line
                break

        if downloaded_path:
            log[movie] = downloaded_path
            size_mb = os.path.getsize(downloaded_path) / (1024 * 1024)
            print(f"  OK ({size_mb:.1f} MB)")
            results.append({"movie": movie, "painting": painting, "status": "downloaded", "path": downloaded_path})
        else:
            # Try to find by index prefix
            prefix = f"{i+1:02d}_{safe_movie}"
            dl_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(prefix) and f.endswith('.mp4')]
            if dl_files:
                path = os.path.join(OUTPUT_DIR, dl_files[0])
                log[movie] = path
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"  Recovered ({size_mb:.1f} MB)")
                results.append({"movie": movie, "painting": painting, "status": "recovered", "path": path})
            else:
                # Check stderr for clues
                err_short = stderr.split("\n")[-1][:200] if stderr else "no output"
                print(f"  FAIL: {err_short}")
                results.append({"movie": movie, "painting": painting, "status": "failed", "error": err_short})

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT")
        results.append({"movie": movie, "painting": painting, "status": "timeout"})
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({"movie": movie, "painting": painting, "status": "error", "error": str(e)})

    # Rate limit
    if i < len(unique) - 1:
        time.sleep(2)

# Save log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

# Summary
ok = sum(1 for r in results if r["status"] in ("downloaded", "cached", "recovered"))
fail = sum(1 for r in results if r["status"] in ("failed", "timeout", "error"))
print(f"\n===== Download Complete =====")
print(f"Success: {ok}/{len(unique)}")
print(f"Failed: {fail}/{len(unique)}")

if fail > 0:
    print("\nFailed:")
    for r in results:
        if r["status"] in ("failed", "timeout", "error"):
            print(f"  - {r['movie']}: {r.get('error', r['status'])}")
