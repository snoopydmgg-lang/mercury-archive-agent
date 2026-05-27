"""
TFT Query Tool - 为 Claude Code 提供数据查询接口
用法:
  python query.py meta              # 当前版本 meta 阵容分析
  python query.py top_units         # Top 1 最高频英雄
  python query.py comp <英雄名>     # 查某套阵容的详细数据
  python query.py augments          # 海克斯强化胜率
  python query.py items <英雄名>    # 某英雄最常见装备
  python query.py recent [N]        # 最近 N 场对局摘要
  python query.py search <关键词>   # 模糊搜索英雄/羁绊
"""
import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from db_schema import get_conn

def meta_analysis():
    """分析当前 meta：哪些阵容平均排名最好"""
    conn = get_conn()

    # 按羁绊组合分析（取有激活羁绊的对局）
    print("=" * 60)
    print("META 阵容分析（按核心羁绊分组）")
    print("=" * 60)

    # 找出最常见的核心羁绊组合（只看前3个激活羁绊）
    results = conn.execute("""
        WITH player_traits AS (
            SELECT
                t.match_id,
                t.puuid,
                p.placement,
                GROUP_CONCAT(t.trait_name, '|') as all_traits
            FROM traits t
            JOIN participants p ON t.match_id = p.match_id AND t.puuid = p.puuid
            WHERE t.tier_current > 0
            GROUP BY t.match_id, t.puuid
        )
        SELECT
            COUNT(*) as games,
            AVG(placement) as avg_placement,
            SUM(CASE WHEN placement = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN placement <= 3 THEN 1 ELSE 0 END) as top3_count,
            ROUND(AVG(placement), 2) as avg_place
        FROM player_traits
        GROUP BY all_traits
        HAVING games >= 3
        ORDER BY avg_place ASC
        LIMIT 20
    """).fetchall()

    if not results:
        print("  数据不足，请先运行 fetcher.py fill 抓取数据")
        conn.close()
        return

    print(f"\n{'阵容':<50} {'场次':>5} {'均排名':>6} {'吃鸡':>4} {'前3':>4}")
    print("-" * 75)

    # 也展示每个组合的英雄
    for r in results:
        # 找这个组合的典型英雄
        # 简化：只显示关键数据
        print(f"  场次={r['games']:>4}  均排名={r['avg_place']:.2f}  吃鸡={r['wins']}  前3={r['top3_count']}")

    # 更实用的分析：按英雄组合
    print("\n" + "=" * 60)
    print("TOP 1 英雄出场统计（吃鸡阵容中的英雄）")
    print("=" * 60)

    top1_units = conn.execute("""
        SELECT
            u.character_id,
            COUNT(*) as win_count,
            AVG(p.placement) as avg_place_in_game
        FROM units u
        JOIN participants p ON u.match_id = p.match_id AND u.puuid = p.puuid
        WHERE p.placement = 1
        GROUP BY u.character_id
        HAVING win_count >= 2
        ORDER BY win_count DESC
        LIMIT 20
    """).fetchall()

    if top1_units:
        print(f"\n{'英雄':<30} {'吃鸡次数':>8} {'出场均排名':>10}")
        print("-" * 52)
        for u in top1_units:
            name = u["character_id"].replace("TFT17_", "").replace("TFT14_", "")
            print(f"  {name:<28} {u['win_count']:>6} {u['avg_place_in_game']:>10.2f}")

    # 羁绊分析
    print("\n" + "=" * 60)
    print("羁绊胜率统计")
    print("=" * 60)

    trait_stats = conn.execute("""
        SELECT
            t.trait_name,
            COUNT(*) as games,
            AVG(p.placement) as avg_place,
            SUM(CASE WHEN p.placement = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN p.placement <= 3 THEN 1 ELSE 0 END) as top3
        FROM traits t
        JOIN participants p ON t.match_id = p.match_id AND t.puuid = p.puuid
        WHERE t.tier_current > 0
        GROUP BY t.trait_name
        HAVING games >= 5
        ORDER BY avg_place ASC
        LIMIT 20
    """).fetchall()

    if trait_stats:
        print(f"\n{'羁绊':<30} {'场次':>5} {'均排名':>6} {'吃鸡率':>7} {'前3率':>7}")
        print("-" * 60)
        for t in trait_stats:
            name = t["trait_name"].replace("TFT17_", "").replace("TFT14_", "")
            win_rate = t["wins"] / t["games"] * 100
            top3_rate = t["top3"] / t["games"] * 100
            print(f"  {name:<28} {t['games']:>5} {t['avg_place']:>6.2f} {win_rate:>6.1f}% {top3_rate:>6.1f}%")

    conn.close()

def top_units():
    """所有英雄的出场和胜率统计"""
    conn = get_conn()

    results = conn.execute("""
        SELECT
            u.character_id,
            COUNT(DISTINCT u.match_id) as games,
            AVG(p.placement) as avg_place,
            SUM(CASE WHEN p.placement = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN p.placement <= 3 THEN 1 ELSE 0 END) as top3,
            AVG(u.tier) as avg_star
        FROM units u
        JOIN participants p ON u.match_id = p.match_id AND u.puuid = p.puuid
        GROUP BY u.character_id
        HAVING games >= 3
        ORDER BY avg_place ASC
    """).fetchall()

    print(f"{'英雄':<25} {'场次':>5} {'均排名':>6} {'吃鸡率':>7} {'前3率':>7} {'均星级':>6}")
    print("-" * 62)
    for r in results:
        name = r["character_id"].replace("TFT17_", "").replace("TFT14_", "")
        win_rate = r["wins"] / r["games"] * 100
        top3_rate = r["top3"] / r["games"] * 100
        print(f"  {name:<23} {r['games']:>5} {r['avg_place']:>6.2f} {win_rate:>6.1f}% {top3_rate:>6.1f}% {r['avg_star']:>5.2f}")

    conn.close()

def comp_analysis(hero_keyword):
    """分析某套阵容的详细数据"""
    conn = get_conn()

    # 找包含该英雄的所有对局
    matches_with_hero = conn.execute("""
        SELECT DISTINCT match_id, puuid
        FROM units
        WHERE character_id LIKE ?
    """, (f"%{hero_keyword}%",)).fetchall()

    if not matches_with_hero:
        print(f"未找到包含 '{hero_keyword}' 的对局")
        conn.close()
        return

    match_puuids = [(m["match_id"], m["puuid"]) for m in matches_with_hero]

    print(f"包含 {hero_keyword} 的对局: {len(match_puuids)} 场")
    print("=" * 60)

    # 这些对局中该英雄的平均排名
    placements = []
    for mid, puid in match_puuids:
        p = conn.execute("SELECT placement FROM participants WHERE match_id = ? AND puuid = ?", (mid, puid)).fetchone()
        if p:
            placements.append(p["placement"])

    if placements:
        avg = sum(placements) / len(placements)
        wins = sum(1 for p in placements if p == 1)
        top3 = sum(1 for p in placements if p <= 3)
        print(f"  平均排名: {avg:.2f}")
        print(f"  吃鸡率: {wins/len(placements)*100:.1f}%")
        print(f"  前3率: {top3/len(placements)*100:.1f}%")

    # 该英雄最常见的装备
    print(f"\n{hero_keyword} 最常见装备:")
    item_counts = {}
    for mid, puid in match_puuids:
        u = conn.execute("SELECT item_names FROM units WHERE match_id = ? AND puuid = ? AND character_id LIKE ?",
                        (mid, puid, f"%{hero_keyword}%")).fetchone()
        if u:
            items = json.loads(u["item_names"])
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1

    for item, count in sorted(item_counts.items(), key=lambda x: -x[1])[:10]:
        name = item.replace("TFT_Item_", "").replace("TFT17_Item_", "")
        print(f"    {name}: {count}次")

    # 该英雄最常见的队友
    print(f"\n{hero_keyword} 最常见队友:")
    teammate_counts = {}
    for mid, puid in match_puuids:
        units = conn.execute("SELECT character_id FROM units WHERE match_id = ? AND puuid = ?", (mid, puid)).fetchall()
        for u in units:
            name = u["character_id"]
            if hero_keyword.lower() not in name.lower():
                teammate_counts[name] = teammate_counts.get(name, 0) + 1

    for char, count in sorted(teammate_counts.items(), key=lambda x: -x[1])[:10]:
        name = char.replace("TFT17_", "").replace("TFT14_", "")
        print(f"    {name}: {count}次")

    conn.close()

def augment_stats():
    """海克斯强化胜率统计"""
    conn = get_conn()

    results = conn.execute("""
        SELECT
            p.augments,
            p.placement
        FROM participants p
        WHERE p.augments != '[]' AND p.augments IS NOT NULL
    """).fetchall()

    if not results:
        print("无海克斯数据")
        conn.close()
        return

    augment_stats = {}
    for r in results:
        augments = json.loads(r["augments"])
        for aug in augments:
            if aug not in augment_stats:
                augment_stats[aug] = {"placements": [], "wins": 0, "top3": 0}
            augment_stats[aug]["placements"].append(r["placement"])
            if r["placement"] == 1:
                augment_stats[aug]["wins"] += 1
            if r["placement"] <= 3:
                augment_stats[aug]["top3"] += 1

    print(f"{'海克斯强化':<40} {'场次':>5} {'均排名':>6} {'吃鸡率':>7}")
    print("-" * 62)
    sorted_augs = sorted(augment_stats.items(), key=lambda x: sum(x[1]["placements"])/len(x[1]["placements"]))
    for aug, stats in sorted_augs[:30]:
        games = len(stats["placements"])
        avg = sum(stats["placements"]) / games
        win_rate = stats["wins"] / games * 100
        name = aug.replace("TFT17_Augment_", "").replace("TFT7_Augment_", "")
        print(f"  {name:<38} {games:>5} {avg:>6.2f} {win_rate:>6.1f}%")

    conn.close()

def search(keyword):
    """模糊搜索英雄和羁绊"""
    conn = get_conn()

    print(f"搜索: {keyword}")
    print("-" * 40)

    # 英雄
    units = conn.execute("""
        SELECT character_id, COUNT(*) as cnt, AVG(p.placement) as avg_p
        FROM units u
        JOIN participants p ON u.match_id = p.match_id AND u.puuid = p.puuid
        WHERE character_id LIKE ?
        GROUP BY character_id
    """, (f"%{keyword}%",)).fetchall()

    if units:
        print("英雄:")
        for u in units:
            name = u["character_id"].replace("TFT17_", "").replace("TFT14_", "")
            print(f"  {name}: {u['cnt']}次出场, 均排名 {u['avg_p']:.2f}")

    # 羁绊
    traits = conn.execute("""
        SELECT trait_name, COUNT(*) as cnt, AVG(p.placement) as avg_p
        FROM traits t
        JOIN participants p ON t.match_id = p.match_id AND t.puuid = p.puuid
        WHERE trait_name LIKE ? AND t.tier_current > 0
        GROUP BY trait_name
    """, (f"%{keyword}%",)).fetchall()

    if traits:
        print("羁绊:")
        for t in traits:
            name = t["trait_name"].replace("TFT17_", "").replace("TFT14_", "")
            print(f"  {name}: {t['cnt']}次激活, 均排名 {t['avg_p']:.2f}")

    conn.close()

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python query.py meta              # Meta 阵容分析")
        print("  python query.py top_units         # 英雄出场统计")
        print("  python query.py comp <英雄名>     # 阵容详情")
        print("  python query.py augments          # 海克斯胜率")
        print("  python query.py search <关键词>   # 模糊搜索")
        return

    cmd = sys.argv[1]

    if cmd == "meta":
        meta_analysis()
    elif cmd == "top_units":
        top_units()
    elif cmd == "comp":
        if len(sys.argv) < 3:
            print("用法: python query.py comp <英雄名>")
            return
        comp_analysis(sys.argv[2])
    elif cmd == "augments":
        augment_stats()
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("用法: python query.py search <关键词>")
            return
        search(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
