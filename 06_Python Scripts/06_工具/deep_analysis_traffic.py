#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频流量深度分析
对比爆款与低迷作品，找出关键差异
"""

import pandas as pd
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def analyze_traffic_decline():
    """分析流量低迷原因"""
    base_path = "E:/1.work/douyin/1.shuixing/00_InBox_收件箱"

    # 读取数据
    df_works = pd.read_excel(os.path.join(base_path, "作品列表.xlsx"))
    df_sales = pd.read_excel(os.path.join(base_path, "短视频下载明细.xlsx"))

    # 转换发布时间
    df_works['发布时间'] = pd.to_datetime(df_works['发布时间'])
    df_works['日期'] = df_works['发布时间'].dt.strftime('%Y%m%d').astype(int)

    # 合并销售数据
    df_merged = df_works.merge(df_sales, left_on='日期', right_on='日期', how='left')
    df_merged['成交金额'] = df_merged['成交金额'].fillna(0)

    print("=" * 100)
    print("【流量低迷诊断报告】")
    print("=" * 100)

    # 1. 识别爆款视频
    print("\n\n## 一、爆款视频识别")
    print("-" * 100)

    爆款阈值 = df_works['播放量'].quantile(0.9)  # 前10%为爆款
    df_works['是否爆款'] = df_works['播放量'] >= 爆款阈值

    爆款视频 = df_works[df_works['是否爆款'] == True].sort_values('播放量', ascending=False)
    普通视频 = df_works[df_works['是否爆款'] == False]

    print(f"\n爆款阈值: {爆款阈值:.0f} 播放量")
    print(f"爆款视频数量: {len(爆款视频)}")
    print(f"普通视频数量: {len(普通视频)}")

    print("\n【爆款视频列表】")
    for idx, row in 爆款视频.iterrows():
        print(f"\n{row['发布时间'].strftime('%m月%d日')} | 播放 {row['播放量']:,} | 完播率 {row['完播率']:.2%}")
        print(f"标题: {row['作品名称'][:80]}...")
        print(f"数据: 点赞{row['点赞量']} 收藏{row['收藏量']} 粉丝+{row['粉丝增量']}")

    # 2. 对比核心指标
    print("\n\n## 二、爆款 vs 普通视频 - 核心指标对比")
    print("-" * 100)

    对比指标 = ['播放量', '完播率', '5s完播率', '2s跳出率', '平均播放时长', '点赞量', '收藏量', '粉丝增量']

    print(f"\n{'指标':<15} {'爆款均值':>12} {'普通均值':>12} {'差距倍数':>10} {'结论':>15}")
    print("-" * 100)

    关键差异 = []

    for 指标 in 对比指标:
        爆款均值 = 爆款视频[指标].mean()
        普通均值 = 普通视频[指标].mean()

        if 普通均值 > 0:
            差距倍数 = 爆款均值 / 普通均值
        else:
            差距倍数 = float('inf') if 爆款均值 > 0 else 1

        if 指标 in ['完播率', '5s完播率', '2s跳出率']:
            结论 = "✓ 正常" if abs(差距倍数 - 1) < 0.5 else "✗ 显著差异"
        else:
            结论 = "✓ 正常" if 差距倍数 < 3 else "✗ 显著差异"

        print(f"{指标:<15} {爆款均值:>12.2f} {普通均值:>12.2f} {差距倍数:>10.2f}x {结论:>15}")

        if "✗" in 结论:
            关键差异.append({
                '指标': 指标,
                '爆款': 爆款均值,
                '普通': 普通均值,
                '差距': 差距倍数
            })

    # 3. 时间序列分析
    print("\n\n## 三、时间序列分析 - 流量趋势")
    print("-" * 100)

    df_works_sorted = df_works.sort_values('发布时间')

    print(f"\n{'日期':<12} {'播放量':>10} {'完播率':>10} {'5s完播':>10} {'跳出率':>10} {'标题':<50}")
    print("-" * 100)

    for idx, row in df_works_sorted.head(15).iterrows():
        print(f"{row['发布时间'].strftime('%m-%d %H:%M'):<12} "
              f"{row['播放量']:>10,} "
              f"{row['完播率']:>9.1%} "
              f"{row['5s完播率']:>9.1%} "
              f"{row['2s跳出率']:>9.1%} "
              f"{row['作品名称'][:50]}")

    # 4. 内容特征分析
    print("\n\n## 四、内容特征分析")
    print("-" * 100)

    # 提取关键词
    def extract_keywords(title):
        keywords = []
        if '版式' in title or '设计' in title:
            keywords.append('版式设计')
        if '宫崎骏' in title or '吉卜力' in title:
            keywords.append('宫崎骏')
        if '飞鸟集' in title or '泰戈尔' in title:
            keywords.append('飞鸟集')
        if '摄影' in title or '构图' in title:
            keywords.append('摄影')
        if '留白' in title:
            keywords.append('留白')
        return keywords[0] if keywords else '其他'

    df_works['内容类型'] = df_works['作品名称'].apply(extract_keywords)

    类型统计 = df_works.groupby('内容类型').agg({
        '播放量': ['count', 'mean', 'max'],
        '完播率': 'mean',
        '点赞量': 'mean',
        '收藏量': 'mean'
    }).round(2)

    print("\n【内容类型表现】")
    print(类型统计)

    # 5. 成交转化分析
    print("\n\n## 五、成交转化分析")
    print("-" * 100)

    有成交视频 = df_merged[df_merged['成交金额'] > 0]

    print(f"\n总视频数: {len(df_works)}")
    print(f"有成交视频数: {len(有成交视频)}")
    print(f"成交转化率: {len(有成交视频)/len(df_works):.1%}")

    if len(有成交视频) > 0:
        print("\n【成交视频详情】")
        for idx, row in 有成交视频.iterrows():
            print(f"\n{row['发布时间'].strftime('%m月%d日')} | 播放 {row['播放量']:,} | 成交 ¥{row['成交金额']:.0f}")
            print(f"GPM: ¥{row['千次观看成交金额']:.2f}")
            print(f"标题: {row['作品名称'][:80]}...")

    # 6. 诊断结论
    print("\n\n" + "=" * 100)
    print("【诊断结论】")
    print("=" * 100)

    print("\n### 关键问题识别:")

    问题清单 = []

    # 问题1: 完播率
    if 普通视频['完播率'].mean() < 0.02:
        问题清单.append({
            '问题': '完播率过低',
            '数据': f"普通视频完播率仅 {普通视频['完播率'].mean():.2%}，远低于行业基准 3-5%",
            '影响': '算法判定内容质量差，限制推流',
            '优先级': 'P0 - 致命'
        })

    # 问题2: 5s完播率
    if 普通视频['5s完播率'].mean() < 0.25:
        问题清单.append({
            '问题': '5秒完播率不足',
            '数据': f"普通视频5s完播率 {普通视频['5s完播率'].mean():.2%}，低于健康线 30%",
            '影响': '开头吸引力不足，用户快速划走',
            '优先级': 'P0 - 致命'
        })

    # 问题3: 2s跳出率
    if 普通视频['2s跳出率'].mean() > 0.5:
        问题清单.append({
            '问题': '2秒跳出率过高',
            '数据': f"普通视频2s跳出率 {普通视频['2s跳出率'].mean():.2%}",
            '影响': '封面/标题与内容不匹配，或开头无吸引力',
            '优先级': 'P0 - 致命'
        })

    # 问题4: 播放量差距
    if 关键差异:
        for diff in 关键差异:
            if diff['指标'] == '播放量' and diff['差距'] > 50:
                问题清单.append({
                    '问题': '播放量断崖式下跌',
                    '数据': f"爆款播放量是普通视频的 {diff['差距']:.0f} 倍",
                    '影响': '内容未进入推荐池，或被算法降权',
                    '优先级': 'P0 - 致命'
                })

    # 问题5: 互动率
    点赞率_爆款 = (爆款视频['点赞量'] / 爆款视频['播放量']).mean()
    点赞率_普通 = (普通视频[普通视频['播放量'] > 0]['点赞量'] / 普通视频[普通视频['播放量'] > 0]['播放量']).mean()

    if 点赞率_普通 < 点赞率_爆款 * 0.5:
        问题清单.append({
            '问题': '互动率低',
            '数据': f"普通视频点赞率 {点赞率_普通:.3%} vs 爆款 {点赞率_爆款:.3%}",
            '影响': '内容共鸣不足，无法激发用户互动',
            '优先级': 'P1 - 重要'
        })

    for i, 问题 in enumerate(问题清单, 1):
        print(f"\n{i}. 【{问题['优先级']}】{问题['问题']}")
        print(f"   数据: {问题['数据']}")
        print(f"   影响: {问题['影响']}")

    return df_works, df_merged, 问题清单

if __name__ == "__main__":
    analyze_traffic_decline()
