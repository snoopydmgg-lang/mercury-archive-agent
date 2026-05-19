#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek 官方账单校准工具
用法:
  python deepseek_calibrate.py <amount.csv> <cost.csv>
  python deepseek_calibrate.py                          # 默认读收件箱最新 CSV

读取 DeepSeek 平台导出的 amount/cost CSV，输出官方计费汇总，
并与 token_tracker 的 transcript 估算做对比。
"""

import sys
import csv
import io
import os
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict

INBOX = Path(__file__).resolve().parent.parent.parent / "00_InBox_收件箱"

# Windows 终端编码
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ANSI_RED = '\033[91m'
ANSI_YELLOW = '\033[93m'
ANSI_GREEN = '\033[92m'
ANSI_CYAN = '\033[96m'
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_DIM = '\033[2m'


def parse_amount_csv(path):
    """解析 amount CSV, 返回 {date: {model: {type: {'tokens': N, 'cost': N}}}}"""
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'tokens': 0, 'cost': 0.0})))
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row['utc_date']
            model = row['model']
            typ = row['type']
            price = float(row['price']) if row['price'] else 0
            amount = int(row['amount']) if row['amount'] else 0
            data[d][model][typ]['tokens'] += amount
            data[d][model][typ]['cost'] += price * amount
    return data


def parse_cost_csv(path):
    """解析 cost CSV, 返回 {date: {model: cost}}"""
    data = defaultdict(lambda: defaultdict(float))
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row['utc_date']
            model = row['model']
            cost = float(row['cost'])
            data[d][model] += cost
    return data


def format_money(n):
    return f"¥{n:.2f}"


def format_tokens(n):
    if n >= 1_000_000:
        return f'{n/1_000_000:.2f}M'
    elif n >= 1_000:
        return f'{n/1_000:.1f}K'
    return str(n)


def find_latest_csvs():
    """在收件箱中找最新的 amount 和 cost CSV"""
    amounts = sorted(INBOX.glob("amount-*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    costs = sorted(INBOX.glob("cost-*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return (amounts[0] if amounts else None), (costs[0] if costs else None)


def main():
    amount_path, cost_path = None, None

    if len(sys.argv) >= 3:
        amount_path = Path(sys.argv[1])
        cost_path = Path(sys.argv[2])
    else:
        amount_path, cost_path = find_latest_csvs()

    if not amount_path or not amount_path.exists():
        print(f"{ANSI_RED}未找到 amount CSV 文件{ANSI_RESET}")
        print("用法: python deepseek_calibrate.py <amount.csv> <cost.csv>")
        print("或将 CSV 放入 00_InBox_收件箱/ 后直接运行")
        return

    if not cost_path or not cost_path.exists():
        print(f"{ANSI_RED}未找到 cost CSV 文件{ANSI_RESET}")
        return

    amount_data = parse_amount_csv(amount_path)
    cost_data = parse_cost_csv(cost_path)

    # 仅统计 deepseek-v4-pro (ccswitch 是主力 API key)
    PRO_MODEL = 'deepseek-v4-pro'

    # ── 按日汇总 ──
    print(f"\n{ANSI_BOLD}{ANSI_CYAN}╭{'─' * 78}╮{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_BOLD}DeepSeek 官方账单校准 · {PRO_MODEL}{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} 数据源: {amount_path.name}")
    print(f"{ANSI_CYAN}├{'─' * 78}┤{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} {'日期':<12} {'输出':>8} {'输入(未命中)':>12} {'输入(命中)':>14} {'请求':>6} {'费用':>10}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} {'─' * 12} {'─' * 8} {'─' * 12} {'─' * 14} {'─' * 6} {'─' * 10}")

    total_output = 0
    total_miss = 0
    total_hit = 0
    total_requests = 0
    total_cost = 0.0
    days_count = 0

    for d in sorted(amount_data.keys()):
        if PRO_MODEL not in amount_data[d]:
            continue
        m = amount_data[d][PRO_MODEL]
        out_tok = m['output_tokens']['tokens']
        miss_tok = m['input_cache_miss_tokens']['tokens']
        hit_tok = m['input_cache_hit_tokens']['tokens']
        req = m['request_count']['tokens']  # actually count, not tokens

        # 用 cost CSV 的精确费用
        day_cost = cost_data.get(d, {}).get(PRO_MODEL, 0.0)

        total_output += out_tok
        total_miss += miss_tok
        total_hit += hit_tok
        total_requests += req
        total_cost += day_cost
        days_count += 1

        print(f"{ANSI_CYAN}│{ANSI_RESET} {d:<12} {format_tokens(out_tok):>8} {format_tokens(miss_tok):>12} {format_tokens(hit_tok):>14} {req:>6} {ANSI_BOLD}{format_money(day_cost):>10}{ANSI_RESET}")

    # ── 总计 ──
    print(f"{ANSI_CYAN}│{ANSI_RESET} {'─' * 12} {'─' * 8} {'─' * 12} {'─' * 14} {'─' * 6} {'─' * 10}")
    all_tokens = total_output + total_miss + total_hit
    cache_rate = (total_hit / (total_miss + total_hit) * 100 if (total_miss + total_hit) > 0 else 0)
    today = date.today()
    daily_avg = total_cost / days_count if days_count > 0 else 0

    print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_BOLD}{'合计':<12} {format_tokens(total_output):>8} {format_tokens(total_miss):>12} {format_tokens(total_hit):>14} {total_requests:>6} {format_money(total_cost):>10}{ANSI_RESET}")
    print(f"{ANSI_CYAN}├{'─' * 78}┤{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} 总 Token: {format_tokens(all_tokens):>10}  |  Cache 命中率: {cache_rate:.1f}%  |  日均: {format_money(daily_avg)}  |  累计: {ANSI_BOLD}{format_money(total_cost)}{ANSI_RESET}")

    # ── 与 tracker 估算对比 ──
    print(f"{ANSI_CYAN}├{'─' * 78}┤{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_BOLD}vs. token_tracker 估算对比{ANSI_RESET}")
    print(f"{ANSI_CYAN}│{ANSI_RESET} {'':12} {'官方账单':>20} {'tracker 估算':>20} {'偏差':>20}")

    # 尝试导入 tracker 的数据做对比
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from token_tracker import collect_all_usage, calculate_cost
        cache = collect_all_usage()
        this_month = today.strftime('%Y-%m')

        tracker_in = tracker_out = tracker_cr = tracker_cc = 0
        tracker_sessions = 0
        for m_key, m_data in cache['monthly'].items():
            if m_key == this_month:
                tracker_in += m_data['input']
                tracker_out += m_data['output']
                tracker_cr += m_data.get('cache_read', 0)
                tracker_cc += m_data.get('cache_creation', 0)
                tracker_sessions += m_data['sessions']

        t_cost = calculate_cost(tracker_in, tracker_out, tracker_cr, tracker_cc)
        t_total = tracker_in + tracker_out + tracker_cr + tracker_cc
        t_input_like = tracker_in + tracker_cc + tracker_cr
        t_cache_rate = (tracker_cr / t_input_like * 100 if t_input_like > 0 else 0)

        # 对比
        def diff_pct(estimate, official):
            if official == 0:
                return 'N/A'
            return f"{(estimate - official) / official * 100:+.1f}%"

        print(f"{ANSI_CYAN}│{ANSI_RESET} {'输入(未命中)':<12} {format_tokens(total_miss):>20} {format_tokens(tracker_in + tracker_cc):>20} {diff_pct(tracker_in + tracker_cc, total_miss):>20}")
        print(f"{ANSI_CYAN}│{ANSI_RESET} {'输入(命中)':<12} {format_tokens(total_hit):>20} {format_tokens(tracker_cr):>20} {diff_pct(tracker_cr, total_hit):>20}")
        print(f"{ANSI_CYAN}│{ANSI_RESET} {'输出':<12} {format_tokens(total_output):>20} {format_tokens(tracker_out):>20} {diff_pct(tracker_out, total_output):>20}")
        print(f"{ANSI_CYAN}│{ANSI_RESET} {'费用总计':<12} {format_money(total_cost):>20} {format_money(t_cost['total']):>20} {diff_pct(t_cost['total'], total_cost):>20}")
        print(f"{ANSI_CYAN}│{ANSI_RESET} {'Cache 命中率':<12} {cache_rate:.1f}% {'':>17} {t_cache_rate:.1f}% {'':>17}")

        # 校准因子
        if total_cost > 0:
            factor = t_cost['total'] / total_cost
            print(f"{ANSI_CYAN}├{'─' * 78}┤{ANSI_RESET}")
            print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_BOLD}校准因子: {factor:.2f}x{ANSI_RESET} (tracker 估算 / 官方账单)")
            if factor > 2:
                print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_YELLOW}tracker 高估 {factor:.1f}x, 主要原因: transcript token 计数口径与 DeepSeek 计费不一致{ANSI_RESET}")
            elif factor < 0.5:
                print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_YELLOW}tracker 低估, 可能有未统计的 API key 消耗{ANSI_RESET}")
            else:
                print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_GREEN}偏差在可接受范围内{ANSI_RESET}")

    except Exception as e:
        print(f"{ANSI_CYAN}│{ANSI_RESET} {ANSI_DIM}(无法加载 tracker 数据做对比: {e}){ANSI_RESET}")

    print(f"{ANSI_CYAN}╰{'─' * 78}╯{ANSI_RESET}\n")


if __name__ == '__main__':
    main()
