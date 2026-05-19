#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
博主数据分析：关注博主的最新动态和爆款作品
"""

import pandas as pd
import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 文件路径
INBOX_DIR = Path("00_InBox_收件箱")
BLOGGER_FILE = INBOX_DIR / "抖音数据-关注达人-全部达人列表 (1).xlsx"
WORKS_FILE = INBOX_DIR / "作品列表.xlsx"

def load_data():
    """加载数据"""
    print("=" * 60)
    print("加载数据中...")
    print("=" * 60)

    bloggers = pd.read_excel(BLOGGER_FILE)
    works = pd.read_excel(WORKS_FILE)

    print(f"✓ 博主数据: {len(bloggers)} 条")
    print(f"✓ 作品数据: {len(works)} 条")
    print()

    return bloggers, works

def analyze_active_bloggers(bloggers):
    """分析活跃博主（最近有新作品的）"""
    print("=" * 60)
    print("1. 活跃博主分析（最近有新作品）")
    print("=" * 60)

    # 筛选最近有新作品的博主
    active = bloggers[bloggers['新增作品'] > 0].copy()

    if len(active) == 0:
        print("⚠ 没有博主最近发布新作品")
        return

    # 按新增作品数排序
    active = active.sort_values('新增作品', ascending=False)

    print(f"\n共 {len(active)} 个博主最近有新作品：\n")

    for idx, row in active.iterrows():
        print(f"【{row['昵称']}】")
        print(f"  粉丝数: {row['粉丝数']:,}")
        print(f"  新增作品: {row['新增作品']} 个")
        print(f"  新增点赞: {row['新增点赞']}")
        print(f"  新增粉丝: {row['新增粉丝']}")
        print(f"  权重指数: {row['权重指数']}")
        print(f"  抖音主页: {row['抖音主页']}")
        print()

def analyze_low_fan_explosions(bloggers):
    """分析低粉爆款（粉丝少但数据好的博主）"""
    print("=" * 60)
    print("2. 低粉爆款分析（粉丝<5万 但数据好）")
    print("=" * 60)

    # 筛选低粉博主（粉丝数 < 50000）
    low_fan = bloggers[bloggers['粉丝数'] < 50000].copy()

    # 筛选有活跃数据的（新增作品 > 0 或 新增点赞 > 0）
    active_low_fan = low_fan[
        (low_fan['新增作品'] > 0) |
        (low_fan['新增点赞'] > 0) |
        (low_fan['新增粉丝'] > 0)
    ].copy()

    if len(active_low_fan) == 0:
        print("⚠ 没有符合条件的低粉爆款博主")
        return

    # 按权重指数排序
    active_low_fan = active_low_fan.sort_values('权重指数', ascending=False)

    print(f"\n共 {len(active_low_fan)} 个低粉博主有活跃数据：\n")

    for idx, row in active_low_fan.iterrows():
        print(f"【{row['昵称']}】⭐ 潜力博主")
        print(f"  粉丝数: {row['粉丝数']:,} (低粉)")
        print(f"  权重指数: {row['权重指数']} (活跃度)")
        print(f"  新增作品: {row['新增作品']} 个")
        print(f"  新增点赞: {row['新增点赞']}")
        print(f"  新增粉丝: {row['新增粉丝']}")
        print(f"  抖音主页: {row['抖音主页']}")
        print()

def analyze_sales_bloggers(bloggers):
    """分析有销售数据的博主"""
    print("=" * 60)
    print("3. 带货博主分析（有销售额）")
    print("=" * 60)

    # 筛选有销售额的博主（总销售额不为0且不为空）
    sales = bloggers[
        (bloggers['总销售额'].notna()) &
        (bloggers['总销售额'] != 0) &
        (bloggers['总销售额'] != '0')
    ].copy()

    if len(sales) == 0:
        print("⚠ 没有博主有销售数据")
        return

    # 按权重指数排序
    sales = sales.sort_values('权重指数', ascending=False)

    print(f"\n共 {len(sales)} 个博主有销售数据：\n")

    for idx, row in sales.iterrows():
        print(f"【{row['昵称']}】")
        print(f"  粉丝数: {row['粉丝数']:,}")
        print(f"  总销售额: {row['总销售额']}")
        print(f"  直播销售额: {row['直播销售额']}")
        print(f"  视频销售额: {row['视频销售额']}")
        print(f"  权重指数: {row['权重指数']}")
        print(f"  抖音主页: {row['抖音主页']}")
        print()

def generate_selection_insights(bloggers):
    """生成选品参考建议"""
    print("=" * 60)
    print("4. 选品参考建议")
    print("=" * 60)

    # 低粉高活跃博主
    low_fan_active = bloggers[
        (bloggers['粉丝数'] < 50000) &
        (bloggers['权重指数'] > 200) &
        ((bloggers['新增作品'] > 0) | (bloggers['新增点赞'] > 0))
    ].copy()

    if len(low_fan_active) > 0:
        print("\n✓ 重点关注（低粉高活跃）：")
        for idx, row in low_fan_active.iterrows():
            print(f"  - {row['昵称']} (粉丝 {row['粉丝数']:,}, 权重 {row['权重指数']})")
            print(f"    → 去他主页看最近发了什么作品")

    # 有销售数据的博主
    sales = bloggers[
        (bloggers['总销售额'].notna()) &
        (bloggers['总销售额'] != 0) &
        (bloggers['总销售额'] != '0')
    ].copy()

    if len(sales) > 0:
        print("\n✓ 带货参考（有销售数据）：")
        for idx, row in sales.iterrows():
            print(f"  - {row['昵称']} (销售额 {row['总销售额']})")
            print(f"    → 看他在卖什么品类")

    print("\n" + "=" * 60)
    print("建议操作：")
    print("=" * 60)
    print("1. 打开上述博主的抖音主页")
    print("2. 查看他们最近发布的作品")
    print("3. 分析爆款作品的选品逻辑")
    print("4. 记录可复制的选品方向")
    print()

def main():
    """主函数"""
    # 加载数据
    bloggers, works = load_data()

    # 分析活跃博主
    analyze_active_bloggers(bloggers)

    # 分析低粉爆款
    analyze_low_fan_explosions(bloggers)

    # 分析带货博主
    analyze_sales_bloggers(bloggers)

    # 生成选品建议
    generate_selection_insights(bloggers)

if __name__ == "__main__":
    main()
