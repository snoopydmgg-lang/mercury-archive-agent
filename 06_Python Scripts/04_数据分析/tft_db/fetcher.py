"""
TFT Data Fetcher - 从 Riot API 抓取 NA 高分段数据并存入 SQLite
用法:
  python fetcher.py challenger     # 抓取 Challenger 全量玩家
  python fetcher.py matches 100    # 为数据库中的玩家抓取最近对局（每个玩家最多10场）
  python fetcher.py fill 50        # 一次性：抓50个玩家 + 他们的对局
"""
import requests
import json
import time
import sys
import os
from datetime import datetime, timezone

# 添加当前目录到 path
sys.path.insert(0, os.path.dirname(__file__))
from db_schema import get_conn, init_db

API_KEY = "RGAPI-203223b9-8beb-4182-bb4e-98272d8fb836"
HEADERS = {"X-Riot-Token": API_KEY}
PLATFORM = "na1"
ROUTING = "americas"
BASE_PLATFORM = f"https://{PLATFORM}.api.riotgames.com"
BASE_ROUTING = f"https://{ROUTING}.api.riotgames.com"

# 速率限制：开发 Key 每秒20请求，保守一点用每秒10
REQUEST_DELAY = 0.15  # 秒

def api_get(url, retries=3):
    """带重试和限流的 API 请求"""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return resp.json()
            elif resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 10))
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif resp.status_code == 401:
                print("  API Key 过期! 请重新获取: https://developer.riotgames.com/")
                return None
            else:
                print(f"  HTTP {resp.status_code}: {url}")
                time.sleep(1)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(2)
    return None

def fetch_challengers():
    """抓取 NA Challenger 全量玩家"""
    init_db()
    conn = get_conn()
    url = f"{BASE_PLATFORM}/tft/league/v1/challenger"
    data = api_get(url)
    if not data:
        print("Challenger API 失败")
        return

    entries = data.get("entries", [])
    now = datetime.now(timezone.utc).isoformat()

    for e in entries:
        conn.execute("""
            INSERT OR REPLACE INTO players (puuid, tier, rank, league_points, wins, losses, hot_streak, veteran, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["puuid"], "CHALLENGER", "I",
            e.get("leaguePoints", 0), e.get("wins", 0), e.get("losses", 0),
            1 if e.get("hotStreak") else 0,
            1 if e.get("veteran") else 0,
            now
        ))

    conn.commit()
    conn.close()
    print(f"Challenger 玩家入库: {len(entries)} 名")

def fetch_grandmaster():
    """抓取 Grandmaster 玩家"""
    init_db()
    conn = get_conn()
    url = f"{BASE_PLATFORM}/tft/league/v1/grandmaster"
    data = api_get(url)
    if not data:
        print("Grandmaster API 失败")
        return

    entries = data.get("entries", [])
    now = datetime.now(timezone.utc).isoformat()

    for e in entries:
        conn.execute("""
            INSERT OR REPLACE INTO players (puuid, tier, rank, league_points, wins, losses, hot_streak, veteran, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e["puuid"], "GRANDMASTER", "I",
            e.get("leaguePoints", 0), e.get("wins", 0), e.get("losses", 0),
            1 if e.get("hotStreak") else 0,
            1 if e.get("veteran") else 0,
            now
        ))

    conn.commit()
    conn.close()
    print(f"Grandmaster 玩家入库: {len(entries)} 名")

def fetch_matches_for_players(limit=50):
    """为数据库中的玩家抓取对局"""
    conn = get_conn()

    # 优先抓没有对局记录的玩家
    players = conn.execute("""
        SELECT p.puuid FROM players p
        WHERE NOT EXISTS (SELECT 1 FROM participants pp WHERE pp.puuid = p.puuid)
        ORDER BY p.league_points DESC
        LIMIT ?
    """, (limit,)).fetchall()

    if not players:
        # 都有对局了，抓最近更新的
        players = conn.execute("""
            SELECT p.puuid FROM players p
            ORDER BY p.last_updated DESC
            LIMIT ?
        """, (limit,)).fetchall()

    total_new_matches = 0
    for i, row in enumerate(players):
        puuid = row["puuid"]
        print(f"[{i+1}/{len(players)}] 抓取玩家 {puuid[:20]}... 的对局")

        # 获取最近对局 ID
        url = f"{BASE_ROUTING}/tft/match/v1/matches/by-puuid/{puuid}/ids?count=10"
        match_ids = api_get(url)
        if not match_ids:
            continue

        # 过滤已有的
        existing = set()
        for mid in match_ids:
            r = conn.execute("SELECT 1 FROM matches WHERE match_id = ?", (mid,)).fetchone()
            if r:
                existing.add(mid)

        new_ids = [m for m in match_ids if m not in existing]
        if not new_ids:
            continue

        for mid in new_ids:
            detail = api_get(f"{BASE_ROUTING}/tft/match/v1/matches/{mid}")
            if not detail:
                continue

            save_match(conn, detail)
            total_new_matches += 1

        conn.commit()

    conn.close()
    print(f"新增对局: {total_new_matches} 场")

def save_match(conn, detail):
    """将一场对局的完整数据存入数据库"""
    info = detail.get("info", {})
    metadata = detail.get("metadata", {})
    match_id = metadata.get("match_id", "")

    # 存对局元数据
    conn.execute("""
        INSERT OR IGNORE INTO matches (match_id, game_version, game_datetime, game_length, tft_set_number, tft_game_type, queue_id, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match_id,
        info.get("game_version", ""),
        info.get("game_datetime", ""),
        info.get("game_length", 0),
        info.get("tft_set_number", 0),
        info.get("tft_game_type", ""),
        info.get("queue_id", 0),
        datetime.now(timezone.utc).isoformat()
    ))

    # 存每个参与者
    for p in info.get("participants", []):
        puuid = p.get("puuid", "")
        # 自动补入未知玩家（对局中的非高分段玩家）
        conn.execute("""
            INSERT OR IGNORE INTO players (puuid, tier, rank, league_points, wins, losses, last_updated)
            VALUES (?, 'UNKNOWN', '', 0, 0, 0, ?)
        """, (puuid, datetime.now(timezone.utc).isoformat()))
        conn.execute("""
            INSERT OR IGNORE INTO participants (match_id, puuid, placement, augments, companion, gold_left, last_round, level, players_eliminated, time_eliminated, total_damage_to_players)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id, puuid,
            p.get("placement", 0),
            json.dumps(p.get("augments", []), ensure_ascii=False),
            json.dumps(p.get("companion", {}), ensure_ascii=False),
            p.get("gold_left", 0),
            p.get("last_round", 0),
            p.get("level", 0),
            p.get("players_eliminated", 0),
            p.get("time_eliminated", 0),
            p.get("total_damage_to_players", 0),
        ))

        # 存英雄单位
        for idx, u in enumerate(p.get("units", [])):
            conn.execute("""
                INSERT OR IGNORE INTO units (match_id, puuid, unit_index, character_id, item_names, rarity, tier)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, puuid, idx,
                u.get("character_id", ""),
                json.dumps(u.get("itemNames", []), ensure_ascii=False),
                u.get("rarity", 0),
                u.get("tier", 0),
            ))

        # 存羁绊
        for t in p.get("traits", []):
            conn.execute("""
                INSERT OR IGNORE INTO traits (match_id, puuid, trait_name, num_units, style, tier_current, tier_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, puuid,
                t.get("name", ""),
                t.get("num_units", 0),
                t.get("style", 0),
                t.get("tier_current", 0),
                t.get("tier_total", 0),
            ))

def show_stats():
    """显示数据库统计"""
    conn = get_conn()
    players = conn.execute("SELECT COUNT(*) as c FROM players").fetchone()["c"]
    matches = conn.execute("SELECT COUNT(*) as c FROM matches").fetchone()["c"]
    participants = conn.execute("SELECT COUNT(*) as c FROM participants").fetchone()["c"]

    print(f"\n数据库统计:")
    print(f"  玩家: {players}")
    print(f"  对局: {matches}")
    print(f"  参与记录: {participants}")

    if matches > 0:
        # 最近对局时间
        latest = conn.execute("SELECT game_version FROM matches ORDER BY fetched_at DESC LIMIT 1").fetchone()
        print(f"  最新版本: {latest['game_version'][:40]}")

        # Top 1 英雄
        top_units = conn.execute("""
            SELECT u.character_id, COUNT(*) as cnt, AVG(p.placement) as avg_place
            FROM units u
            JOIN participants p ON u.match_id = p.match_id AND u.puuid = p.puuid
            WHERE p.placement = 1
            GROUP BY u.character_id
            ORDER BY cnt DESC
            LIMIT 10
        """).fetchall()
        if top_units:
            print(f"\n  Top 1 最高频英雄:")
            for u in top_units:
                name = u["character_id"].replace("TFT14_", "").replace("TFT17_", "")
                print(f"    {name}: {u['cnt']}次, 平均排名 {u['avg_place']:.1f}")

    conn.close()

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python fetcher.py challenger     # 抓 Challenger 玩家")
        print("  python fetcher.py grandmaster    # 抓 Grandmaster 玩家")
        print("  python fetcher.py matches [N]    # 抓 N 个玩家的对局")
        print("  python fetcher.py fill [N]       # 一步到位：抓玩家+对局")
        print("  python fetcher.py stats          # 查看数据库统计")
        return

    cmd = sys.argv[1]

    if cmd == "challenger":
        fetch_challengers()
    elif cmd == "grandmaster":
        fetch_grandmaster()
    elif cmd == "matches":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        fetch_matches_for_players(limit)
    elif cmd == "fill":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print("Step 1: 抓取 Challenger 玩家...")
        fetch_challengers()
        print("Step 2: 抓取 Grandmaster 玩家...")
        fetch_grandmaster()
        print(f"Step 3: 抓取前 {limit} 个玩家的对局...")
        fetch_matches_for_players(limit)
        print("\nStep 4: 统计...")
        show_stats()
    elif cmd == "stats":
        show_stats()
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
