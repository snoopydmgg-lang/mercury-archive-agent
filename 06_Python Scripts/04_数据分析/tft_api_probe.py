"""
TFT API Probe - 测试 Riot API Key 和路由
用途：确认 API Key 有效性，探测国服/各区域的可用性
"""
import requests
import json
import sys
import time

API_KEY = "RGAPI-203223b9-8beb-4182-bb4e-98272d8fb836"
HEADERS = {"X-Riot-Token": API_KEY}

# 需要测试的区域路由组合
ROUTING_TESTS = [
    # Platform → 对应的 Regional 路由
    ("na1", "americas", "北美"),
    ("euw1", "europe", "欧洲西"),
    ("kr", "asia", "韩国"),
    ("br1", "americas", "巴西"),
    # 中国大陆可能的路由（尝试多种组合）
    ("cn1", "asia", "国服-asia路由"),
    ("cn1", "americas", "国服-americas路由"),
    ("cn1", "europe", "国服-europe路由"),
    ("cn1", "sea", "国服-sea路由"),
]

def test_endpoint(url, label):
    """测试单个端点，返回 (success, data/error)"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return True, resp.json()
        elif resp.status_code == 401:
            return False, "API Key 无效或已过期"
        elif resp.status_code == 403:
            return False, "Forbidden - 可能 Key 被封或路径不对"
        elif resp.status_code == 404:
            return False, "Not Found - 端点不存在"
        elif resp.status_code == 429:
            return False, "Rate Limited - 被限流了"
        else:
            return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("TFT API 探测脚本")
    print("=" * 60)
    print(f"API Key: {API_KEY[:20]}...")
    print()

    # Step 1: 测试 Challenger 端点（各区域）
    print("【Step 1】测试各区域 Challenger 端点")
    print("-" * 60)
    working_platforms = []
    for platform, routing, label in ROUTING_TESTS:
        url = f"https://{platform}.api.riotgames.com/tft/league/v1/challenger"
        success, data = test_endpoint(url, label)
        status = "OK" if success else "FAIL"
        if success:
            count = len(data.get("entries", []))
            print(f"  [{status}] {label} ({platform}): 成功, {count} 名王者")
        else:
            print(f"  [{status}] {label} ({platform}): {data}")
        if success:
            working_platforms.append((platform, routing, label))
        time.sleep(0.5)  # 防限流

    print()

    # Step 2: 对可用区域测试 Summoner API
    print("【Step 2】对可用区域测试 Summoner API")
    print("-" * 60)
    for platform, routing, label in working_platforms:
        # 用一个已知的高分段玩家名测试
        test_name = "Hide on bush"  # Faker 的 ID
        url = f"https://{platform}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{test_name}"
        success, data = test_endpoint(url, label)
        status = "OK" if success else "FAIL"
        if success:
            puuid = data.get("puuid", "N/A")
            print(f"  [{status}] {label}: PUUID={puuid[:20]}...")
        else:
            print(f"  [{status}] {label}: {data}")
        time.sleep(0.5)

    print()

    # Step 3: 如果有可用区域，测试 Match API
    print("【Step 3】测试 Match API（取 Challenger 池中第一个玩家）")
    print("-" * 60)
    for platform, routing, label in working_platforms:
        # 先拿 Challenger 列表
        url = f"https://{platform}.api.riotgames.com/tft/league/v1/challenger"
        success, data = test_endpoint(url, label)
        if not success:
            continue

        entries = data.get("entries", [])
        if not entries:
            print(f"  [{label}] 无玩家数据")
            continue

        # 取第一个玩家的 summonerId，再查 PUUID
        summoner_id = entries[0].get("summonerId", "")
        summoner_url = f"https://{platform}.api.riotgames.com/tft/summoner/v1/summoners/{summoner_id}"
        s_success, s_data = test_endpoint(summoner_url, label)
        if not s_success:
            print(f"  [{label}] Summoner 查询失败: {s_data}")
            continue

        puuid = s_data.get("puuid", "")
        # 查最近对局
        match_url = f"https://{routing}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=3"
        m_success, m_data = test_endpoint(match_url, label)
        status = "OK" if m_success else "FAIL"
        if m_success:
            print(f"  [{status}] {label}: 最近 {len(m_data)} 场对局 = {m_data}")
        else:
            print(f"  [{status}] {label}: Match API = {m_data}")
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("探测完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
