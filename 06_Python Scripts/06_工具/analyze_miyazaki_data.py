#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析宫崎骏视频数据
"""

import pandas as pd
import sys
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 读取作品列表
df1 = pd.read_excel("E:/1.work/douyin/1.shuixing/00_InBox_收件箱/作品列表.xlsx")
df2 = pd.read_excel("E:/1.work/douyin/1.shuixing/00_InBox_收件箱/[20260319-20260417]_全部视频_全部视频.xlsx")

print("="*60)
print("作品列表中的宫崎骏视频")
print("="*60)

# 筛选宫崎骏相关视频
miyazaki_df1 = df1[df1['作品名称'].str.contains('宫崎骏', na=False)]
print(f"\n找到 {len(miyazaki_df1)} 条记录\n")
if len(miyazaki_df1) > 0:
    print(miyazaki_df1[['作品名称', '发布时间', '播放量', '完播率', '5s完播率', '点赞量', '收藏量']].to_string())

print("\n" + "="*60)
print("全部视频中的宫崎骏视频")
print("="*60)

miyazaki_df2 = df2[df2['作品标题'].str.contains('宫崎骏', na=False)]
print(f"\n找到 {len(miyazaki_df2)} 条记录\n")
if len(miyazaki_df2) > 0:
    print(miyazaki_df2[['作品标题', '发布时间', '观看次数', '直接成交金额', '成交订单数']].to_string())

# 统计数据
if len(miyazaki_df2) > 0:
    print("\n" + "="*60)
    print("宫崎骏视频统计")
    print("="*60)
    print(f"\n总视频数: {len(miyazaki_df2)}")

    # 转换观看次数为数字（处理可能的字符串）
    try:
        # 尝试转换为数字
        watch_counts = pd.to_numeric(miyazaki_df2['观看次数'], errors='coerce')
        valid_counts = watch_counts.dropna()
        if len(valid_counts) > 0:
            print(f"平均观看次数: {valid_counts.mean():.0f}")
            print(f"最高观看次数: {valid_counts.max():.0f}")
            print(f"最低观看次数: {valid_counts.min():.0f}")
    except Exception as e:
        print(f"观看次数统计失败: {e}")

    print(f"总成交金额: {miyazaki_df2['直接成交金额'].sum()}")
    print(f"总成交订单数: {miyazaki_df2['成交订单数'].sum()}")

    # 显示每条视频的详细数据
    print("\n" + "="*60)
    print("各视频详细数据")
    print("="*60)
    for idx, row in miyazaki_df2.iterrows():
        print(f"\n标题: {row['作品标题'][:50]}...")
        print(f"发布时间: {row['发布时间']}")
        print(f"观看次数: {row['观看次数']}")
        print(f"成交: {row['直接成交金额']} ({row['成交订单数']}单)")
