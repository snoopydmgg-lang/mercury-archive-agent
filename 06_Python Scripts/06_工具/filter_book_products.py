"""
图书类目选品筛选工具
基于灰豚榜单数据，筛选适合水星艺术馆的商品
"""

import pandas as pd
import re

def parse_range(range_str):
    """解析销量/销售额区间，返回中位数"""
    if pd.isna(range_str) or range_str == 0:
        return 0

    range_str = str(range_str)

    # 处理 "1w-2.5w" 这种格式
    if 'w' in range_str or 'k' in range_str:
        parts = range_str.replace('w', '').replace('k', '').split('-')
        if len(parts) == 2:
            try:
                low = float(parts[0])
                high = float(parts[1])
                multiplier = 10000 if 'w' in range_str else 1000
                return (low + high) / 2 * multiplier
            except:
                return 0

    # 处理纯数字
    try:
        return float(range_str)
    except:
        return 0

def calculate_video_ratio(row):
    """计算短视频出单占比"""
    total_sales = parse_range(row['商品销量'])
    video_sales = parse_range(row['视频销量'])

    if total_sales == 0:
        return 0

    return (video_sales / total_sales) * 100

def calculate_price(row):
    """根据销量和销售额估算客单价"""
    sales = parse_range(row['商品销量'])
    revenue = parse_range(row['商品销售额'])

    if sales == 0:
        return 0

    return revenue / sales

def is_target_category(category, title):
    """判断是否为目标类目：文学/历史/哲学/艺术"""

    # 排除类目（儿童读物、教辅、医学养生）
    exclude_keywords = [
        '儿童', '童书', '绘本', '幼儿', '少儿', '亲子', '早教',
        '教辅', '教材', '考试', '中考', '高考', '小学', '中学', '试卷', '练习',
        '医学', '养生', '中医', '本草', '偏方', '药方', '健康'
    ]

    # 目标类目（文学、历史、哲学、艺术）
    target_keywords = [
        # 文学
        '文学', '小说', '诗歌', '散文', '戏剧', '名著', '经典',
        # 历史
        '历史', '史记', '通鉴', '古代', '近代', '世界史', '中国史',
        # 哲学
        '哲学', '思想', '逻辑', '伦理', '美学', '认知',
        # 艺术
        '艺术', '设计', '摄影', '美术', '绘画', '书法',
        '版式', '构图', '色彩', '视觉', '平面', '创意',
        '插画', '漫画', '动画', '建筑', '工艺', '手工',
        '音乐', '电影', '戏剧', '舞蹈'
    ]

    text = str(category) + str(title)

    # 先排除
    if any(keyword in text for keyword in exclude_keywords):
        return False

    # 再匹配目标
    return any(keyword in text for keyword in target_keywords)

def filter_products(file_path, output_path=None):
    """筛选商品"""

    # 读取数据
    print("正在读取数据...")
    df = pd.read_excel(file_path)
    print(f"总商品数: {len(df)}")

    # 计算衍生指标
    print("\n正在计算指标...")
    df['视频出单占比'] = df.apply(calculate_video_ratio, axis=1)
    df['估算客单价'] = df.apply(calculate_price, axis=1)
    df['商品销量_数值'] = df['商品销量'].apply(parse_range)
    df['是否目标类目'] = df.apply(lambda row: is_target_category(row['类目'], row['商品名称']), axis=1)

    # 筛选条件
    print("\n应用筛选条件...")
    filtered = df[
        (df['视频出单占比'] >= 60) &  # 短视频出单占比 ≥ 60%
        (df['商品销量_数值'] >= 500) &  # 销量 ≥ 500单
        (df['商品销量_数值'] <= 50000) &  # 销量 ≤ 5w单（避免红海）
        (df['估算客单价'] >= 50) &  # 客单价 ≥ 50元
        (df['估算客单价'] <= 300) &  # 客单价 ≤ 300元
        (df['是否目标类目'] == True)  # 文学/历史/哲学/艺术
    ].copy()

    print(f"筛选后商品数: {len(filtered)}")

    if len(filtered) == 0:
        print("\n[WARNING] 没有符合条件的商品，尝试放宽条件...")

        # 放宽条件：只要目标类目 + 视频出单占比高
        filtered = df[
            (df['视频出单占比'] >= 50) &
            (df['是否目标类目'] == True)
        ].copy()

        print(f"放宽后商品数: {len(filtered)}")

    # 按视频销量排序
    filtered = filtered.sort_values('商品销量_数值', ascending=False)

    # 选择关键列
    output_columns = [
        '排行', '商品名称', '类目', '估算客单价', '商品销量', '商品销售额',
        '视频销量', '视频出单占比', '关联视频', '关联达人',
        '店铺名称', '品牌', '好评率', '商品链接'
    ]

    result = filtered[output_columns]

    # 保存结果
    if output_path:
        result.to_excel(output_path, index=False)
        print(f"\n[OK] 结果已保存到: {output_path}")

    # 打印前10个
    print("\n" + "="*80)
    print("TOP 10 候选商品:")
    print("="*80)

    for idx, row in result.head(10).iterrows():
        print(f"\n[{int(row['排行'])}] {row['商品名称']}")
        print(f"  类目: {row['类目']}")
        print(f"  估算客单价: {row['估算客单价']:.0f}元")
        print(f"  销量: {row['商品销量']} | 销售额: {row['商品销售额']}")
        print(f"  视频销量: {row['视频销量']} | 视频占比: {row['视频出单占比']:.1f}%")
        print(f"  关联视频: {row['关联视频']} | 关联达人: {row['关联达人']}")
        print(f"  店铺: {row['店铺名称']} | 品牌: {row['品牌']}")
        print(f"  好评率: {row['好评率']}")
        print(f"  链接: {row['商品链接']}")

    return result

if __name__ == "__main__":
    input_file = "00_InBox_收件箱/抖音商品榜-2026年04月-undefined.xlsx"
    output_file = "00_InBox_收件箱/筛选结果_文史哲艺术类图书.xlsx"

    result = filter_products(input_file, output_file)

    print("\n" + "="*80)
    print(f"[OK] 筛选完成！共找到 {len(result)} 个候选商品")
    print("="*80)
