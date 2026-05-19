#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户使用习惯与额度卡成本分析（精细版）
基于：
1. MiniMax账单（2026-03-12 至 2026-04-10，27天）
   - 总Token: 14.73亿（含缓存）
   - 实际输入: ~7.84亿 | 输出: ~560万
   - 上下文复用率: 47%
   - 请求次数: 793次/月
2. 闲鱼灰产单价：
   - Opus: 25-30万token/刀，7次请求/刀
   - Sonnet: 50万token/刀，20次请求/刀
3. CodeSOME平台定价
4. 当前方案：MiniMax Starter CNY29/月（按请求次数计费）
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def analyze_usage_pattern():
    print("=" * 70)
    print("用户使用习惯与额度卡成本分析（精细版）")
    print("=" * 70)

    # ============ 基础数据 ============
    total_days = 27
    total_requests = 793
    total_tokens_27d = 1_473_114_296   # 14.73亿token（含缓存）
    input_tokens_actual = 784_000_000  # ~7.84亿实际输入
    output_tokens_actual = 5_600_000    # ~560万输出
    cache_hit_rate = 0.47              # 47%
    current_cost = 49                  # CNY/月（MiniMax Coding Plan）
    usd_to_cny = 7.2

    monthly_requests = (total_requests / total_days) * 30  # 881次/月

    # 闲鱼报价
    SONNET_TOKENS_PER_DOLLAR = 500_000   # 50万token/刀
    OPUS_MIN_TOKENS = 250_000            # 25万token/刀
    OPUS_MAX_TOKENS = 300_000            # 30万token/刀
    SONNET_REQUESTS_PER_DOLLAR = 20      # 20次/刀
    OPUS_REQUESTS_PER_DOLLAR = 7        # 7次/刀

    # 闲鱼套餐包
    XIANYU_PACKAGES = [
        {"name": "基础包", "dollars": 20,  "cny": 11.88},
        {"name": "标准包", "dollars": 60,  "cny": 33.0},
        {"name": "进阶包", "dollars": 100, "cny": 52.0},
        {"name": "大客户包", "dollars": 400, "cny": 214.88},
    ]

    # CodeSOME月度套餐
    CODESOME_PLANS = [
        {"name": "30刀/月", "dollars": 30,  "cny": 289},
        {"name": "40刀/月", "dollars": 40,  "cny": 389},
        {"name": "50刀/月", "dollars": 50,  "cny": 459},
        {"name": "60刀/月", "dollars": 60,  "cny": 559},
    ]

    # ============ 第一部分：你的实际使用情况 ============
    print("\n【一】你的实际使用情况（27天账单）")
    print("-" * 50)
    print(f"  总Token（含缓存）: {total_tokens_27d:,} (约{total_tokens_27d/100_000_000:.1f}亿)")
    print(f"  实际输入Token:     {input_tokens_actual:,} (约{input_tokens_actual/100_000_000:.1f}亿)")
    print(f"  实际输出Token:     {output_tokens_actual:,} (约{output_tokens_actual/1_000_000:.1f}百万)")
    print(f"  上下文复用率:     {cache_hit_rate*100:.0f}%（即缓存命中率）")
    print(f"  请求次数（27天）: {total_requests:,} 次")
    print(f"  月估算请求（30天）: {monthly_requests:.0f} 次")
    print(f"  当前方案: CNY {current_cost}/月（MiniMax Coding Plan）")

    # MiniMax计费逻辑说明
    print("\n  MiniMax ¥49/月计费方式: 按请求次数，不按token")
    print("  （1500次/5小时窗口，你月均881次，峰值54次/天，完全够用）")

    # ============ 第二部分：按Token精细计算（付费Token = 输入×0.53 + 输出） ============
    # 缓存命中47%意味着有53%的输入需要真实付费
    paid_input_tokens = int(input_tokens_actual * (1 - cache_hit_rate) * 30 / total_days)
    paid_output_tokens = int(output_tokens_actual * 30 / total_days)
    monthly_paid_tokens = paid_input_tokens + paid_output_tokens

    print(f"\n【二】按实际付费Token精细计算（月均）")
    print("-" * 50)
    print(f"  缓存复用率: {cache_hit_rate*100:.0f}%")
    print(f"  所以实际付费input: {input_tokens_actual:,} × (1-{cache_hit_rate}) = {paid_input_tokens:,}")
    print(f"  输出Token: {paid_output_tokens:,}")
    print(f"  月均付费Token总量: {monthly_paid_tokens:,} (约{monthly_paid_tokens/1_000_000:.1f}百万)")

    # Sonnet
    sonnet_dollars_by_token = monthly_paid_tokens / SONNET_TOKENS_PER_DOLLAR
    opus_dollars_by_token_min = monthly_paid_tokens / OPUS_MAX_TOKENS  # 最优
    opus_dollars_by_token_max = monthly_paid_tokens / OPUS_MIN_TOKENS  # 最劣

    # 闲鱼单价
    xianyu_best = 214.88 / 400  # 大客户包
    xianyu_std = 33.0 / 60      # 标准包

    print(f"\n  按Token计算（{monthly_paid_tokens:,}付费token/月）:")
    print(f"  Sonnet: 需 {sonnet_dollars_by_token:.1f} 刀/月")
    print(f"    → 按大客户包¥{xianyu_best:.3f}/刀: CNY {sonnet_dollars_by_token * xianyu_best:.2f}/月")
    print(f"    → 按标准包¥{xianyu_std:.3f}/刀:   CNY {sonnet_dollars_by_token * xianyu_std:.2f}/月")
    print(f"  Opus:   需 {opus_dollars_by_token_min:.1f}-{opus_dollars_by_token_max:.1f} 刀/月")
    print(f"    → 按大客户包: CNY {opus_dollars_by_token_min * xianyu_best:.2f}-{opus_dollars_by_token_max * xianyu_best:.2f}/月")

    # ============ 第三部分：按请求次数计算（MiniMax实际计费方式） ============
    print(f"\n【三】按请求次数计算（MiniMax实际计费方式）")
    print("-" * 50)
    print(f"  你的月请求: {monthly_requests:.0f} 次")

    sonnet_requests_dollars = monthly_requests / SONNET_REQUESTS_PER_DOLLAR
    opus_requests_dollars = monthly_requests / OPUS_REQUESTS_PER_DOLLAR

    print(f"\n  Sonnet: 需 {sonnet_requests_dollars:.1f} 刀/月 ({monthly_requests:.0f}次 ÷ 20次/刀)")
    print(f"    → 按大客户包: CNY {sonnet_requests_dollars * xianyu_best:.2f}/月")
    print(f"    → 按标准包:   CNY {sonnet_requests_dollars * xianyu_std:.2f}/月")
    print(f"  Opus:   需 {opus_requests_dollars:.1f} 刀/月 ({monthly_requests:.0f}次 ÷ 7次/刀)")
    print(f"    → 按大客户包: CNY {opus_requests_dollars * xianyu_best:.2f}/月")

    # ============ 第四部分：三平台横向对比 ============
    print(f"\n【四】三平台月费对比（月需{monthly_requests:.0f}次请求）")
    print("-" * 50)
    print(f"  {'平台':<20} {'方案':<15} {'月费':<12} {'vs ¥29'}")
    print("-" * 50)

    # MiniMax
    print(f"  {'MiniMax Starter':<20} {'¥29固定':<15} CNY 29      1.0倍（基准）")

    # 闲鱼 Sonnet
    sonnet_xianyu = sonnet_requests_dollars * xianyu_best
    print(f"  {'闲鱼 Sonnet':<20} {'¥0.537/刀':<15} CNY {sonnet_xianyu:.2f}    {sonnet_xianyu/current_cost:.2f}倍")

    # 闲鱼 Opus
    opus_xianyu = opus_requests_dollars * xianyu_best
    print(f"  {'闲鱼 Opus':<20} {'¥0.537/刀':<15} CNY {opus_xianyu:.2f}   {opus_xianyu/current_cost:.2f}倍")

    # CodeSOME（找最接近需求的套餐）
    print(f"\n  CodeSOME 月度套餐（预付费模式）:")
    for plan in CODESOME_PLANS:
        cover = plan["dollars"] / sonnet_requests_dollars * 100
        cost_per_call = plan["cny"] / plan["dollars"]
        print(f"    {plan['name']:<8} CNY {plan['cny']:<6} ({plan['dollars']}刀) | "
              f"覆盖{cover:.0f}%请求 | 单次请求成本: CNY {cost_per_call:.3f}")

    # 找最接近的CodeSOME套餐
    needed_dollars = sonnet_requests_dollars
    for i, plan in enumerate(CODESOME_PLANS):
        if plan["dollars"] >= needed_dollars:
            codesome_plan = plan
            break
    else:
        codesome_plan = CODESOME_PLANS[-1]

    codesome_monthly = codesome_plan["cny"]
    print(f"\n  CodeSOME推荐: {codesome_plan['name']} → CNY {codesome_monthly}/月 "
          f"({codesome_monthly/current_cost:.1f}倍)")

    # ============ 第五部分：结论 ============
    print("\n【五】结论")
    print("-" * 50)

    all_costs = [
        ("MiniMax Starter", 29),
        ("闲鱼Sonnet(大包)", sonnet_xianyu),
        ("闲鱼Opus(大包)", opus_xianyu),
        ("CodeSOME(最小满足)", codesome_monthly),
    ]
    all_costs.sort(key=lambda x: x[1])
    cheapest = all_costs[0]

    print(f"  最便宜: {cheapest[0]} = CNY {cheapest[1]:.2f}/月")
    print(f"  当前¥29方案排名: 第{[i+1 for i,(n,c) in enumerate(all_costs) if 'MiniMax' in n][0]}名")

    print("\n  ⚠️  重要说明:")
    print("  1. MiniMax ¥29/月是订阅制（600次/5小时），不是按token扣费")
    print("  2. 闲鱼/CodeSOME是预付费额度制，按消耗刀数扣费")
    print("  3. 两者计费逻辑不同：订阅 vs 额度")
    print("  4. 闲鱼Sonnet按请求次数算确实比MiniMax便宜，但:")
    print("     - 存在封号/跑路风险")
    print("     - 14.7亿token只是统计量，实际MiniMax按请求收费")
    print("     - 你的881次/月已被¥29全覆盖，闲鱼省¥5意义不大")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_usage_pattern()