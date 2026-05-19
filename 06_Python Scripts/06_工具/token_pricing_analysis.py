#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
额度卡定价合理性分析
用户提供：
- Opus: 1刀 ≈ 25万-30万 token
- Sonnet: 1刀 ≈ 50万 token

对比 Anthropic 官方定价（2025-08）：
- Opus: 输入 $15/百万 token, 输出 $75/百万 token
- Sonnet: 输入 $3/百万 token, 输出 $15/百万 token
- Haiku: 输入 $0.25/百万 token, 输出 $1.25/百万 token
"""

def calculate_cost_per_million(tokens_per_dollar):
    """计算每百万 token 需要多少刀"""
    if tokens_per_dollar == 0:
        return float('inf')
    return 1_000_000 / tokens_per_dollar

def main():
    print("=" * 60)
    print("额度卡定价合理性分析")
    print("=" * 60)

    # 用户定价数据
    user_pricing = {
        "Opus": {"tokens_per_dollar": [250_000, 300_000], "desc": "25万-30万 token/刀"},
        "Sonnet": {"tokens_per_dollar": [500_000], "desc": "50万 token/刀"},
    }

    # Anthropic 官方定价（美元/百万token）
    official_pricing = {
        "Opus": {"input": 15.0, "output": 75.0},
        "Sonnet": {"input": 3.0, "output": 15.0},
        "Haiku": {"input": 0.25, "output": 1.25},
    }

    print("\n1. 用户定价分析（1刀能买多少token）:")
    print("-" * 40)
    for model, data in user_pricing.items():
        tokens_list = data["tokens_per_dollar"]
        desc = data["desc"]
        for tokens in tokens_list:
            cost_per_million = calculate_cost_per_million(tokens)
            print(f"  {model}: {desc}")
            print(f"    → 每百万token成本: ${cost_per_million:.2f}")

    print("\n2. Anthropic 官方定价（美元/百万token）:")
    print("-" * 40)
    for model, prices in official_pricing.items():
        print(f"  {model}:")
        print(f"    输入: ${prices['input']:.2f}/百万token")
        print(f"    输出: ${prices['output']:.2f}/百万token")
        avg = (prices['input'] * 4 + prices['output'] * 1) / 5  # 假设输入:输出=4:1
        print(f"    估算平均（4:1）: ${avg:.2f}/百万token")

    print("\n3. 对比分析:")
    print("-" * 40)

    # 用户定价范围
    opus_user_min = calculate_cost_per_million(300_000)  # 30万/刀 = 更便宜
    opus_user_max = calculate_cost_per_million(250_000)  # 25万/刀 = 更贵
    sonnet_user = calculate_cost_per_million(500_000)

    # 官方平均估算（输入:输出=4:1）
    opus_official_avg = (15 * 4 + 75 * 1) / 5  # $39/百万token
    sonnet_official_avg = (3 * 4 + 15 * 1) / 5  # $7.8/百万token

    print(f"  Opus:")
    print(f"    用户: ${opus_user_min:.2f} - ${opus_user_max:.2f}/百万token")
    print(f"    官方平均: ${opus_official_avg:.2f}/百万token")
    discount_min = (opus_official_avg - opus_user_min) / opus_official_avg * 100
    discount_max = (opus_official_avg - opus_user_max) / opus_official_avg * 100
    print(f"    折扣: {discount_min:.1f}% - {discount_max:.1f}%")

    print(f"\n  Sonnet:")
    print(f"    用户: ${sonnet_user:.2f}/百万token")
    print(f"    官方平均: ${sonnet_official_avg:.2f}/百万token")
    discount = (sonnet_official_avg - sonnet_user) / sonnet_official_avg * 100
    print(f"    折扣: {discount:.1f}%")

    print("\n4. 合理性评估:")
    print("-" * 40)
    print("[+] 优点:")
    print("  - 按token消耗扣费，透明公平")
    print("  - 不同模型差异化定价，反映能力差异")
    print("  - 预付卡模式便于用户预算控制")
    print("  - 后台明细可查，增强信任")
    print("\n[!] 注意事项:")
    print("  - 用户需理解token概念（非字数）")
    print("  - 定价显著低于官方，需确保成本覆盖")
    print("  - 可能依赖批量采购折扣或补贴策略")
    print("  - 需准确统计输入/输出token")
    print("\n[图表] 商业建议:")
    print("  - 明确说明是否区分输入/输出token")
    print("  - 考虑提供使用量预测工具")
    print("  - 可设置套餐阶梯（如10刀、50刀、100刀）")
    print("  - 定期调价以匹配官方价格变动")

    print("\n5. 示例计算（1刀能做什么）:")
    print("-" * 40)
    # 估算典型对话的token消耗
    print("  典型对话（1000字中文 ≈ 2000 token）:")
    for model, data in user_pricing.items():
        tokens_list = data["tokens_per_dollar"]
        tokens = tokens_list[0]  # 取第一个值
        conversations = tokens / 2000
        print(f"  {model}: 1刀 ≈ {conversations:.0f} 次对话")

    print("\n" + "=" * 60)
    print("结论: 定价模式合理，但需确保商业可持续性")
    print("=" * 60)

if __name__ == "__main__":
    main()