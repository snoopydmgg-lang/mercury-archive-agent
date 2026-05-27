"""
TFT API Probe v2 - 修正 Summoner 端点，完整测试数据链路
"""
import requests
import json
import time

API_KEY = "RGAPI-203223b9-8beb-4182-bb4e-98272d8fb836"
HEADERS = {"X-Riot-Token": API_KEY}

# 已确认可用的区域
REGIONS = [
    ("kr", "asia", "韩国"),
    ("na1", "americas", "北美"),
    ("euw1", "europe", "欧洲"),
]

def test_tft_full_pipeline(platform, routing, label):
    """完整测试: Challenger -> Summoner(TFT) -> Match IDs -> Match Detail"""
    print(f"\n{'='*50}")
    print(f"测试区域: {label} ({platform})")
    print(f"{'='*50}")

    # 1. 拿 Challenger 列表
    url = f"https://{platform}.api.riotgames.com/tft/league/v1/challenger"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        print(f"  Challenger 失败: HTTP {resp.status_code}")
        return
    entries = resp.json().get("entries", [])
    print(f"  [1] Challenger: {len(entries)} 名玩家")

    # 按 LP 排序取前3
    top3 = sorted(entries, key=lambda x: x.get("leaguePoints", 0), reverse=True)[:3]
    for i, e in enumerate(top3):
        print(f"      #{i+1} {e.get('summonerId', 'N/A')[:20]}... LP={e.get('leaguePoints', 0)}")

    # 2. 用 summonerId 拿 TFT Summoner 信息（获取 PUUID）
    summoner_id = top3[0]["summonerId"]
    # TFT 用的是同一个 Summoner 端点，但路径是 /tft/
    # 试试两种路径
    paths_to_try = [
        f"https://{platform}.api.riotgames.com/tft/summoner/v1/summoners/{summoner_id}",
        f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}",
    ]

    puuid = None
    for path_url in paths_to_try:
        resp = requests.get(path_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            puuid = resp.json().get("puuid")
            print(f"  [2] Summoner PUUID: {puuid[:30]}...")
            break
        else:
            short_path = path_url.split("/")[-2]
            print(f"  [2] {short_path} -> HTTP {resp.status_code}")

    if not puuid:
        # 尝试用 TFT League entry 里的 puuid 字段
        print("  [2] 尝试从 league entries 直接获取 PUUID...")
        # 有些版本的 league API 直接返回 puuid
        for e in entries:
            if "puuid" in e:
                puuid = e["puuid"]
                print(f"  [2] 从 entries 拿到 PUUID: {puuid[:30]}...")
                break
        if not puuid:
            print("  [2] 所有路径均无法获取 PUUID，尝试用 summoner name 查...")
            # 试一个知名玩家
            test_names = ["hide on bush", "Faker", "Dopa"]
            for name in test_names:
                name_url = f"https://{platform}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{name}"
                resp = requests.get(name_url, headers=HEADERS, timeout=10)
                if resp.status_code == 200:
                    puuid = resp.json().get("puuid")
                    print(f"  [2] 用名字 '{name}' 查到 PUUID: {puuid[:30]}...")
                    break
                time.sleep(0.3)

    if not puuid:
        print("  [!] 无法获取 PUUID，跳过后续测试")
        return

    # 3. 用 PUUID 拿最近对局 ID
    match_url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=5"
    resp = requests.get(match_url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        print(f"  [3] Match IDs 失败: HTTP {resp.status_code}")
        return
    match_ids = resp.json()
    print(f"  [3] 最近 {len(match_ids)} 场对局: {match_ids[:3]}...")

    # 4. 拉第一场对局详情
    if match_ids:
        detail_url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/{match_ids[0]}"
        resp = requests.get(detail_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"  [4] Match Detail 失败: HTTP {resp.status_code}")
            return
        detail = resp.json()
        info = detail.get("info", {})
        participants = info.get("participants", [])
        print(f"  [4] 对局详情: {len(participants)} 名玩家, 版本={info.get('game_version', 'N/A')[:30]}")

        # 展示第一名的阵容
        if participants:
            winner = min(participants, key=lambda x: x.get("placement", 8))
            traits = [t for t in winner.get("traits", []) if t.get("tier_current", 0) > 0]
            units = winner.get("units", [])
            print(f"      第一名阵容:")
            print(f"        羁绊: {', '.join([t.get('name','') for t in traits])}")
            print(f"        英雄: {', '.join([u.get('character_id','').replace('TFT_Set','') for u in units])}")

    print(f"\n  结论: {label} 区域完整链路 OK!")

def main():
    print("TFT API 完整链路探测 v2")
    print(f"API Key: {API_KEY[:20]}...")

    for platform, routing, label in REGIONS:
        test_tft_full_pipeline(platform, routing, label)
        time.sleep(1)

    print("\n" + "="*50)
    print("国服情况说明:")
    print("  Riot API 不覆盖中国大陆服务器 (cn1)")
    print("  国服数据需要通过其他途径获取:")
    print("    1. 网页爬虫 (lol.qq.com / 云顶之弈官网)")
    print("    2. 第三方 API (如果有的话)")
    print("    3. 先用韩服数据做分析框架，后续接国服数据源")
    print("="*50)

if __name__ == "__main__":
    main()
