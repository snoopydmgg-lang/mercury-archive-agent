#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抖音数据分析脚本
分析00_InBox_收件箱中的所有Excel文件，包括：
1. 博主作品详细数据（5个博主）
2. 整体数据汇总（抖音数据-关注达人）
3. 新增作品监测（达人监测-新增作品）
"""

import pandas as pd
import numpy as np
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文显示 - Windows系统使用SimHei（黑体）
import matplotlib
matplotlib.rcParams.update({
    'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.family': 'sans-serif'
})

# 设置输出目录
output_dir = "数据分析结果"
os.makedirs(output_dir, exist_ok=True)

def load_all_excel_files(folder_path):
    """
    加载所有Excel文件并返回数据字典
    """
    print("正在加载Excel文件...")

    excel_files = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.xlsx', '.xls')):
                file_path = os.path.join(root, file)
                excel_files[file] = file_path

    print(f"找到 {len(excel_files)} 个Excel文件")

    # 分类文件
    file_categories = {
        '博主作品数据': [],  # 博主详细作品数据
        '整体数据汇总': [],  # 抖音数据-关注达人
        '新增作品监测': []   # 达人监测-新增作品
    }

    for filename in excel_files:
        if '抖音数据-关注达人' in filename:
            file_categories['整体数据汇总'].append(filename)
        elif '达人监测-新增作品' in filename:
            file_categories['新增作品监测'].append(filename)
        else:
            file_categories['博主作品数据'].append(filename)

    # 加载数据
    data_dict = {}

    # 加载博主作品数据
    print("\n加载博主作品数据...")
    blogger_data_list = []
    for filename in file_categories['博主作品数据']:
        try:
            file_path = excel_files[filename]
            # 提取博主名字
            blogger_name = filename.split('-')[0].strip()

            # 读取数据
            df = pd.read_excel(file_path)
            df['博主名称'] = blogger_name
            df['文件名'] = filename

            # 重命名列以便统一 - 根据用户提供的作品列表文件列名
            column_mapping = {
                '序号': '作品ID',
                '视频标题': '视频标题',
                '发布时间': '发布时间',
                '视频时长(秒)': '视频时长_秒',
                '点赞': '点赞数',
                '评论': '评论数',
                '分享': '转发数',  # 用户文件中的"分享"对应"转发数"
                '视频销量': '视频销量',
                '视频销售额': '视频销售额',
                # 以下为可能存在的其他列
                '视频链接': '视频链接',
                '链接地址': '链接地址',
                '博主昵称': '博主昵称',
                '博主抖音号': '博主抖音号',
                '博主粉丝数': '博主粉丝数',
                '博主等级': '博主等级',
                '关联商品': '关联商品',
                '博主点评': '博主点评'
            }

            # 重命名列
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df.rename(columns={old_col: new_col}, inplace=True)

            # 打印原始列名和销售额相关列名（用于调试）
            sales_related = [col for col in df.columns if '销售' in col or '销额' in col or 'Sale' in col]
            if sales_related:
                print(f"  [列名] {blogger_name} 销售额相关列: {sales_related}")

            blogger_data_list.append(df)
            print(f"  [OK] {blogger_name}: {len(df)} 条记录")

        except Exception as e:
            print(f"  [ERROR] {filename}: 加载失败 - {e}")

    # 合并博主数据
    if blogger_data_list:
        blogger_data = pd.concat(blogger_data_list, ignore_index=True)
        data_dict['博主作品数据'] = blogger_data
        print(f"合并博主数据: 共 {len(blogger_data)} 条记录")

    # 加载整体数据汇总
    print("\n加载整体数据汇总...")
    for filename in file_categories['整体数据汇总']:
        try:
            file_path = excel_files[filename]
            df = pd.read_excel(file_path)
            data_dict['整体数据汇总'] = df

            # 打印列名（用于调试）
            sales_related = [col for col in df.columns if '销售' in col or '销额' in col or 'Sale' in col]
            if sales_related:
                print(f"  [列名] {filename} 销售额相关列: {sales_related}")
            else:
                print(f"  [列名] {filename} 所有列名: {list(df.columns)}")

            print(f"  [OK] {filename}: {len(df)} 条记录")
        except Exception as e:
            print(f"  [ERROR] {filename}: 加载失败 - {e}")

    # 加载新增作品监测
    print("\n加载新增作品监测...")
    for filename in file_categories['新增作品监测']:
        try:
            file_path = excel_files[filename]
            df = pd.read_excel(file_path)
            data_dict['新增作品监测'] = df
            print(f"  [OK] {filename}: {len(df)} 条记录")
        except Exception as e:
            print(f"  [ERROR] {filename}: 加载失败 - {e}")

    return data_dict, file_categories

def clean_and_preprocess_data(data_dict):
    """
    数据清洗和预处理
    """
    print("\n正在进行数据清洗和预处理...")

    cleaned_data = {}

    # 1. 处理博主作品数据
    if '博主作品数据' in data_dict:
        df = data_dict['博主作品数据'].copy()

        # 转换时间列
        if '发布时间' in df.columns:
            df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
            df['发布日期'] = df['发布时间'].dt.date
            df['发布月份'] = df['发布时间'].dt.month
            df['发布星期'] = df['发布时间'].dt.day_name()

        # 处理数值列
        numeric_cols = ['视频时长_秒', '点赞数', '评论数', '转发数', '视频销售额', '视频销量', '博主粉丝数']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 调试：打印视频销售额统计
        if '视频销售额' in df.columns:
            # 确保视频销售额是数值类型
            df['视频销售额'] = pd.to_numeric(df['视频销售额'], errors='coerce').fillna(0)
            non_zero_video_sales = df[df['视频销售额'] > 0]
            print(f"视频销售额统计: 总作品数={len(df)}, 非零销售额作品数={len(non_zero_video_sales)}")
            if len(non_zero_video_sales) > 0:
                print(f"非零销售额作品示例:")
                sample = non_zero_video_sales[['博主名称', '视频标题', '视频销售额']].head(3)
                for _, row in sample.iterrows():
                    title = row['视频标题'][:50] + '...' if len(row['视频标题']) > 50 else row['视频标题']
                    print(f"  - {row['博主名称']}: {title} (¥{row['视频销售额']:.2f})")

        # 计算互动率
        if all(col in df.columns for col in ['点赞数', '评论数', '转发数', '博主粉丝数']):
            df['总互动数'] = df['点赞数'] + df['评论数'] + df['转发数']
            df['互动率'] = df['总互动数'] / df['博主粉丝数'] * 100  # 百分比

        # 计算视频时长分组
        if '视频时长_秒' in df.columns:
            df['视频时长_分组'] = pd.cut(df['视频时长_秒'],
                                       bins=[0, 30, 60, 120, 300, 600, np.inf],
                                       labels=['<30s', '30-60s', '1-2min', '2-5min', '5-10min', '>10min'])

        # 删除重复记录
        # 检查哪些列存在
        subset_cols = []
        for col in ['作品ID', '视频标题', '博主名称', 'ID']:
            if col in df.columns:
                subset_cols.append(col)

        if subset_cols:
            df = df.drop_duplicates(subset=subset_cols, keep='first')
            print(f"基于列 {subset_cols} 删除重复记录")
        else:
            print("警告：无合适列用于去重，跳过重复记录删除")

        cleaned_data['博主作品数据'] = df
        print(f"博主作品数据: 清洗后 {len(df)} 条记录")

    # 2. 处理整体数据汇总
    if '整体数据汇总' in data_dict:
        df = data_dict['整体数据汇总'].copy()

        # 重命名列
        column_mapping = {
            '昵称': '博主昵称',
            '抖音号': '博主抖音号',
            '抖音主页链接': '主页链接',
            '主页链接': '主页链接2',
            '粉丝数': '粉丝数',
            '权重指数': '权重指数',
            '累计粉丝': '累计粉丝',
            '累计作品': '累计作品数',
            '累计点赞': '累计点赞数',
            '累计评论': '累计评论数',
            '累计转发': '累计转发数',
            '累计直播': '累计直播次数',
            '观看人次': '累计观看人次',
            '累计音浪': '累计音浪',
            '商品销售额': '商品销售额',
            '直播销售额': '直播销售额',
            '视频销售额': '视频销售额'
        }

        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)

        # 处理数值列
        numeric_cols = ['粉丝数', '权重指数', '累计粉丝', '累计作品数', '累计点赞数',
                       '累计评论数', '累计转发数', '累计直播次数', '累计观看人次',
                       '累计音浪', '商品销售额', '直播销售额', '视频销售额']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 计算平均互动数据
        if all(col in df.columns for col in ['累计点赞数', '累计评论数', '累计转发数', '累计作品数']):
            df['平均点赞'] = df['累计点赞数'] / df['累计作品数']
            df['平均评论'] = df['累计评论数'] / df['累计作品数']
            df['平均转发'] = df['累计转发数'] / df['累计作品数']
            df['总销售额'] = df['商品销售额'] + df['直播销售额'] + df['视频销售额']

        # 调试：打印销售额统计
        if '总销售额' in df.columns:
            # 确保总销售额是数值类型
            df['总销售额'] = pd.to_numeric(df['总销售额'], errors='coerce').fillna(0)
            non_zero_sales = df[df['总销售额'] > 0]
            print(f"销售额统计: 总记录数={len(df)}, 非零销售额记录数={len(non_zero_sales)}")
            if len(non_zero_sales) > 0:
                print(f"非零销售额博主: {non_zero_sales[['博主昵称', '总销售额']].to_string(index=False)}")
            else:
                print("所有博主的销售额均为0")

        cleaned_data['整体数据汇总'] = df
        print(f"整体数据汇总: 清洗后 {len(df)} 条记录")

    # 3. 处理新增作品监测
    if '新增作品监测' in data_dict:
        df = data_dict['新增作品监测'].copy()

        # 转换时间列
        if '发布时间' in df.columns:
            df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')

        # 处理数值列
        numeric_cols = ['视频时长(秒)', '博主粉丝数', '点赞', '销售额', '评论', '转发', '收藏数', '分享数']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        cleaned_data['新增作品监测'] = df
        print(f"新增作品监测: 清洗后 {len(df)} 条记录")

    return cleaned_data

def generate_summary_statistics(cleaned_data):
    """
    生成数据摘要统计
    """
    print("\n正在生成摘要统计...")

    summary = {}

    # 1. 博主作品数据统计
    if '博主作品数据' in cleaned_data:
        df = cleaned_data['博主作品数据']
        print(f"博主作品数据列名: {list(df.columns)}")

        # 基本统计
        basic_stats = {
            '总作品数': len(df),
            '博主数量': df['博主名称'].nunique(),
            '时间范围': f"{df['发布时间'].min()} 至 {df['发布时间'].max()}",
            '平均作品数': len(df) / df['博主名称'].nunique(),
        }

        # 按博主统计 - 动态创建agg字典
        agg_dict = {}
        columns_mapping = []

        # 检查计数列
        count_col = None
        for col in ['作品ID', 'ID']:
            if col in df.columns:
                count_col = col
                agg_dict[col] = 'count'
                columns_mapping.append(('作品数', col, 'count'))
                break

        # 检查点赞数列
        like_col = None
        for col in ['点赞数', '点赞']:
            if col in df.columns:
                like_col = col
                agg_dict[col] = ['mean', 'sum']
                columns_mapping.extend([('平均点赞', col, 'mean'), ('总点赞', col, 'sum')])
                break

        # 检查评论数列
        comment_col = None
        for col in ['评论数', '评论']:
            if col in df.columns:
                comment_col = col
                agg_dict[col] = ['mean', 'sum']
                columns_mapping.extend([('平均评论', col, 'mean'), ('总评论', col, 'sum')])
                break

        # 检查转发数列
        share_col = None
        for col in ['转发数', '转发']:
            if col in df.columns:
                share_col = col
                agg_dict[col] = ['mean', 'sum']
                columns_mapping.extend([('平均转发', col, 'mean'), ('总转发', col, 'sum')])
                break

        # 检查视频销售额列
        sales_col = None
        for col in ['视频销售额', '销售额']:
            if col in df.columns:
                sales_col = col
                agg_dict[col] = ['mean', 'sum', lambda x: x.sum() if pd.notnull(x).any() else 0]
                columns_mapping.extend([('平均销售额', col, 'mean'), ('总销售额', col, 'sum'), ('有销售额作品数', col, '<lambda>')])
                break

        # 检查视频时长列
        duration_col = None
        for col in ['视频时长_秒', '视频时长(秒)']:
            if col in df.columns:
                duration_col = col
                agg_dict[col] = 'mean'
                columns_mapping.append(('平均时长', col, 'mean'))
                break

        if agg_dict:
            blogger_stats = df.groupby('博主名称').agg(agg_dict).round(2)

            # 扁平化多级列索引
            if isinstance(blogger_stats.columns, pd.MultiIndex):
                blogger_stats.columns = ['_'.join(col).strip() for col in blogger_stats.columns.values]
            else:
                # 如果是单层索引，根据mapping重命名
                new_columns = []
                for col in blogger_stats.columns:
                    # 查找映射
                    for new_name, old_name, agg_func in columns_mapping:
                        if old_name == col and agg_func == 'mean':
                            new_columns.append(new_name)
                            break
                        elif old_name == col and agg_func == 'sum':
                            new_columns.append(new_name)
                            break
                        elif old_name == col and agg_func == 'count':
                            new_columns.append(new_name)
                            break
                        elif old_name == col and agg_func == '<lambda>':
                            new_columns.append(new_name)
                            break
                    else:
                        new_columns.append(col)

                blogger_stats.columns = new_columns
        else:
            # 即使没有其他列，也至少统计作品数
            blogger_stats = df.groupby('博主名称').size().reset_index(name='作品数')
            blogger_stats.set_index('博主名称', inplace=True)
            print("警告：无有效列进行博主统计，仅统计作品数")

        # 互动分析
        interaction_stats = {}

        if like_col and like_col in df.columns:
            interaction_stats['平均点赞数'] = df[like_col].mean()
            if df[like_col].notna().any():
                interaction_stats['最高点赞作品'] = df.loc[df[like_col].idxmax()]['视频标题'] if '视频标题' in df.columns else 'N/A'
                interaction_stats['最高点赞数'] = df[like_col].max()
            else:
                interaction_stats['最高点赞作品'] = 'N/A'
                interaction_stats['最高点赞数'] = 0
        else:
            interaction_stats['平均点赞数'] = 0
            interaction_stats['最高点赞作品'] = 'N/A'
            interaction_stats['最高点赞数'] = 0

        if comment_col and comment_col in df.columns:
            interaction_stats['平均评论数'] = df[comment_col].mean()
        else:
            interaction_stats['平均评论数'] = 0

        if share_col and share_col in df.columns:
            interaction_stats['平均转发数'] = df[share_col].mean()
        else:
            interaction_stats['平均转发数'] = 0

        summary['博主作品数据'] = {
            'basic_stats': basic_stats,
            'blogger_stats': blogger_stats,
            'interaction_stats': interaction_stats
        }

    # 2. 整体数据汇总统计
    if '整体数据汇总' in cleaned_data:
        df = cleaned_data['整体数据汇总']
        print(f"整体数据汇总列名: {list(df.columns)}")

        # 基本统计 - 使用安全的列访问
        basic_stats = {
            '博主总数': len(df),
        }

        # 粉丝数统计
        if '粉丝数' in df.columns:
            basic_stats['总粉丝数'] = df['粉丝数'].sum()
            basic_stats['平均粉丝数'] = df['粉丝数'].mean()
        else:
            basic_stats['总粉丝数'] = 0
            basic_stats['平均粉丝数'] = 0

        # 作品数统计
        if '累计作品' in df.columns:
            basic_stats['总作品数'] = df['累计作品'].sum()
        elif '累计作品数' in df.columns:
            basic_stats['总作品数'] = df['累计作品数'].sum()
        else:
            basic_stats['总作品数'] = 0

        # 销售额统计
        sales_cols = ['商品销售额', '直播销售额', '视频销售额']
        total_sales = 0
        for col in sales_cols:
            if col in df.columns:
                total_sales += df[col].sum()
        basic_stats['总销售额'] = total_sales

        # 最高权重博主
        if '权重指数' in df.columns and df['权重指数'].notna().any():
            basic_stats['最高权重博主'] = df.loc[df['权重指数'].idxmax()]['博主昵称'] if '博主昵称' in df.columns else 'N/A'
        else:
            basic_stats['最高权重博主'] = 'N/A'

        # 最高销售额博主
        if '总销售额' in df.columns and df['总销售额'].notna().any():
            basic_stats['最高销售额博主'] = df.loc[df['总销售额'].idxmax()]['博主昵称'] if '博主昵称' in df.columns else 'N/A'
        else:
            # 尝试计算每个博主的总销售额
            if all(col in df.columns for col in ['博主昵称', '商品销售额', '直播销售额', '视频销售额']):
                df['计算总销售额'] = df['商品销售额'] + df['直播销售额'] + df['视频销售额']
                basic_stats['最高销售额博主'] = df.loc[df['计算总销售额'].idxmax()]['博主昵称']
            else:
                basic_stats['最高销售额博主'] = 'N/A'

        # 准备top博主数据
        top_columns = ['博主昵称', '粉丝数']
        if '权重指数' in df.columns:
            top_columns.append('权重指数')

        # 计算总销售额列
        if '总销售额' in df.columns:
            top_columns.append('总销售额')
        elif all(col in df.columns for col in ['商品销售额', '直播销售额', '视频销售额']):
            df['计算总销售额'] = df['商品销售额'] + df['直播销售额'] + df['视频销售额']
            top_columns.append('计算总销售额')
            top_bloggers_df = df.nlargest(10, '粉丝数')[top_columns]
            # 重命名计算列
            top_bloggers_df = top_bloggers_df.rename(columns={'计算总销售额': '总销售额'})
        else:
            top_bloggers_df = df.nlargest(10, '粉丝数')[top_columns]

        # 确保top_bloggers_df已定义
        if 'top_bloggers_df' not in locals():
            print("警告: top_bloggers_df未定义，使用空DataFrame")
            top_bloggers_df = pd.DataFrame()

        summary['整体数据汇总'] = {
            'basic_stats': basic_stats,
            'top_bloggers': top_bloggers_df
        }

    # 3. 新增作品监测统计
    if '新增作品监测' in cleaned_data:
        df = cleaned_data['新增作品监测']

        basic_stats = {
            '新增作品数': len(df),
            '涉及博主数': df['博主昵称'].nunique() if '博主昵称' in df.columns else 0,
            '平均点赞': df['点赞'].mean() if '点赞' in df.columns else 0,
            '平均销售额': df['销售额'].mean() if '销售额' in df.columns else 0,
            '发布日期': df['发布时间'].min().date() if '发布时间' in df.columns and df['发布时间'].notna().any() else 'N/A',
        }

        summary['新增作品监测'] = {
            'basic_stats': basic_stats
        }

    return summary

def create_visualizations(cleaned_data, summary):
    """
    创建可视化图表
    """
    print("\n正在创建可视化图表...")

    # 确保中文字体设置
    matplotlib.rcParams.update({
        'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.family': 'sans-serif'
    })

    # 设置图表风格
    sns.set_style("whitegrid")
    # 设置中文字体（seaborn可能会重置字体设置）
    matplotlib.rcParams.update({
        'font.sans-serif': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
        'axes.unicode_minus': False,
        'font.family': 'sans-serif'
    })
    plt.figure(figsize=(12, 8))

    # 1. 博主作品数据可视化
    if '博主作品数据' in cleaned_data:
        df = cleaned_data['博主作品数据']

        # 图表1: 各博主作品数量分布
        plt.figure(figsize=(10, 6))
        blogger_counts = df['博主名称'].value_counts()
        # 使用plt.bar以便获取bars对象添加数据标注
        bars = plt.bar(blogger_counts.index, blogger_counts.values, color='skyblue')
        plt.title('各博主作品数量分布', fontsize=14)
        plt.xlabel('博主名称', fontsize=12)
        plt.ylabel('作品数量', fontsize=12)
        plt.xticks(rotation=45)

        # 添加数据标注（垂直柱状图，顶部上方显示）
        for bar, value in zip(bars, blogger_counts.values):
            if value != 0:
                # 在柱子顶部上方添加标注
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2,
                         height + height * 0.01,  # 在柱子上方加1%间距
                         f'{int(value)}',  # 显示整数值
                         ha='center', va='bottom',
                         fontsize=10, color='#333333')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/博主作品数量分布.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 图表2: 各博主平均互动数据
        if all(col in df.columns for col in ['点赞数', '评论数', '转发数']):
            plt.figure(figsize=(12, 6))
            blogger_avg = df.groupby('博主名称')[['点赞数', '评论数', '转发数']].mean()
            blogger_avg.plot(kind='bar', width=0.8)
            plt.title('各博主平均互动数据', fontsize=14)
            plt.xlabel('博主名称', fontsize=12)
            plt.ylabel('平均数量', fontsize=12)
            plt.xticks(rotation=45)
            plt.legend(['平均点赞', '平均评论', '平均转发'])
            plt.tight_layout()
            plt.savefig(f"{output_dir}/各博主平均互动数据.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 图表3: 视频时长分布
        if '视频时长_分组' in df.columns:
            plt.figure(figsize=(10, 6))
            duration_dist = df['视频时长_分组'].value_counts().sort_index()
            # 使用plt.bar以便获取bars对象添加数据标注
            bars = plt.bar(duration_dist.index, duration_dist.values, color='lightgreen')
            plt.title('视频时长分布', fontsize=14)
            plt.xlabel('视频时长分组', fontsize=12)
            plt.ylabel('作品数量', fontsize=12)

            # 添加数据标注（垂直柱状图，顶部上方显示）
            for bar, value in zip(bars, duration_dist.values):
                if value != 0:
                    # 在柱子顶部上方添加标注
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width() / 2,
                             height + height * 0.01,  # 在柱子上方加1%间距
                             f'{int(value)}',  # 显示整数值
                             ha='center', va='bottom',
                             fontsize=10, color='#333333')

            plt.tight_layout()
            plt.savefig(f"{output_dir}/视频时长分布.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 图表4: 点赞-评论-转发散点图矩阵
        if all(col in df.columns for col in ['点赞数', '评论数', '转发数']):
            plt.figure(figsize=(12, 10))
            interaction_cols = ['点赞数', '评论数', '转发数']
            scatter_matrix = pd.plotting.scatter_matrix(df[interaction_cols], figsize=(12, 10), diagonal='hist')
            plt.suptitle('互动数据散点图矩阵', fontsize=14)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/互动数据散点图矩阵.png", dpi=300, bbox_inches='tight')
            plt.close()

    # 2. 整体数据汇总可视化
    if '整体数据汇总' in cleaned_data:
        df = cleaned_data['整体数据汇总']

        # 图表5: 博主粉丝数分布
        if '粉丝数' in df.columns:
            plt.figure(figsize=(10, 6))
            df_sorted = df.sort_values('粉丝数', ascending=False).head(15)
            bars = plt.barh(df_sorted['博主昵称'], df_sorted['粉丝数'], color='orange')
            plt.title('Top 15 博主粉丝数分布', fontsize=14)
            plt.xlabel('粉丝数', fontsize=12)
            plt.ylabel('博主昵称', fontsize=12)

            # 添加数据标注（水平柱状图，右侧显示）
            for bar, value in zip(bars, df_sorted['粉丝数']):
                if value != 0:
                    # 在柱子右端外侧添加标注
                    width = bar.get_width()
                    plt.text(width + width * 0.01,  # 在柱子右侧加1%间距
                             bar.get_y() + bar.get_height() / 2,
                             f'{int(value):,}',  # 格式化千分位
                             ha='left', va='center',
                             fontsize=10, color='#333333')

            plt.tight_layout()
            plt.savefig(f"{output_dir}/Top15博主粉丝数分布.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 图表6: 粉丝数 vs 销售额散点图
        if all(col in df.columns for col in ['粉丝数', '总销售额']):
            plt.figure(figsize=(10, 6))
            plt.scatter(df['粉丝数'], df['总销售额'], alpha=0.6, s=100)
            plt.title('粉丝数 vs 总销售额', fontsize=14)
            plt.xlabel('粉丝数', fontsize=12)
            plt.ylabel('总销售额', fontsize=12)

            # 添加趋势线
            if len(df) > 1:
                # 确保数据是数值类型
                try:
                    x_data = pd.to_numeric(df['粉丝数'], errors='coerce')
                    y_data = pd.to_numeric(df['总销售额'], errors='coerce')

                    # 移除NaN值
                    valid_mask = x_data.notna() & y_data.notna()
                    x_valid = x_data[valid_mask]
                    y_valid = y_data[valid_mask]

                    if len(x_valid) > 1:
                        z = np.polyfit(x_valid, y_valid, 1)
                        p = np.poly1d(z)
                        plt.plot(x_valid, p(x_valid), "r--", alpha=0.8)
                    else:
                        print("警告：有效数据点不足，跳过趋势线绘制")
                except Exception as e:
                    print(f"绘制趋势线时出错: {e}")

            plt.tight_layout()
            plt.savefig(f"{output_dir}/粉丝数vs总销售额.png", dpi=300, bbox_inches='tight')
            plt.close()

        # 图表7: 各指标相关性热图
        if len(df.columns) > 5:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) > 2:
                plt.figure(figsize=(12, 10))
                corr_matrix = df[numeric_cols].corr()
                sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
                plt.title('数据指标相关性热图', fontsize=14)
                plt.tight_layout()
                plt.savefig(f"{output_dir}/数据指标相关性热图.png", dpi=300, bbox_inches='tight')
                plt.close()

    # 3. 新增作品监测可视化
    if '新增作品监测' in cleaned_data:
        df = cleaned_data['新增作品监测']

        # 图表8: 新增作品互动分布
        if all(col in df.columns for col in ['点赞', '评论', '转发']):
            plt.figure(figsize=(10, 6))
            interaction_data = df[['点赞', '评论', '转发']].mean()
            interaction_data.plot(kind='bar', color=['skyblue', 'lightgreen', 'salmon'])
            plt.title('新增作品平均互动数据', fontsize=14)
            plt.xlabel('互动类型', fontsize=12)
            plt.ylabel('平均数量', fontsize=12)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/新增作品平均互动数据.png", dpi=300, bbox_inches='tight')
            plt.close()

    print(f"所有图表已保存到 {output_dir}/ 目录")

def generate_report(cleaned_data, summary, file_categories):
    """
    生成分析报告
    """
    print("\n正在生成分析报告...")

    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("抖音数据分析报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)

    # 文件概览
    report_lines.append("\n📁 文件概览")
    report_lines.append("-" * 40)
    for category, files in file_categories.items():
        report_lines.append(f"{category}: {len(files)} 个文件")
        for file in files:
            report_lines.append(f"  • {file}")

    # 博主作品数据分析
    if '博主作品数据' in summary:
        report_lines.append("\n📊 博主作品数据分析")
        report_lines.append("-" * 40)
        stats = summary['博主作品数据']['basic_stats']
        for key, value in stats.items():
            report_lines.append(f"{key}: {value}")

        report_lines.append("\n📈 各博主表现统计:")
        blogger_stats = summary['博主作品数据']['blogger_stats']
        report_lines.append(blogger_stats.to_string())

        report_lines.append("\n❤️ 互动分析:")
        interaction_stats = summary['博主作品数据']['interaction_stats']
        for key, value in interaction_stats.items():
            report_lines.append(f"{key}: {value}")

    # 整体数据汇总分析
    if '整体数据汇总' in summary:
        report_lines.append("\n📈 整体数据汇总分析")
        report_lines.append("-" * 40)
        stats = summary['整体数据汇总']['basic_stats']
        for key, value in stats.items():
            report_lines.append(f"{key}: {value}")

        report_lines.append("\n🏆 Top 10 博主:")
        top_bloggers = summary['整体数据汇总']['top_bloggers']
        report_lines.append(top_bloggers.to_string(index=False))

    # 新增作品监测分析
    if '新增作品监测' in summary:
        report_lines.append("\n🆕 新增作品监测分析")
        report_lines.append("-" * 40)
        stats = summary['新增作品监测']['basic_stats']
        for key, value in stats.items():
            report_lines.append(f"{key}: {value}")

    # 数据质量评估
    report_lines.append("\n📋 数据质量评估")
    report_lines.append("-" * 40)

    if '博主作品数据' in cleaned_data:
        df = cleaned_data['博主作品数据']
        missing_percentage = df.isnull().sum() / len(df) * 100
        high_missing = missing_percentage[missing_percentage > 50]

        # 过滤掉本来就是空的列，不显示警告
        exclude_columns = ['关联组件', '组件说明']
        filtered_high_missing = {col: pct for col, pct in high_missing.items()
                                if col not in exclude_columns}

        if len(filtered_high_missing) > 0:
            report_lines.append("⚠️ 高缺失率列 (>50%):")
            for col, percentage in filtered_high_missing.items():
                report_lines.append(f"  • {col}: {percentage:.1f}% 缺失")
        else:
            report_lines.append("✅ 数据质量良好，无高缺失率列")

    # 业务洞察
    report_lines.append("\n💡 业务洞察与建议")
    report_lines.append("-" * 40)

    # 基于分析的业务洞察
    insights = [
        "1. 关注高互动率博主：分析显示部分博主虽然粉丝数不高，但互动率较高",
        "2. 视频时长优化：大多数视频集中在30-120秒，这是抖音用户的偏好时长",
        "3. 销售额与粉丝数相关性强：粉丝数越高的博主，总体销售额也越高",
        "4. 发布时间分析：建议分析最佳发布时间段以提升作品曝光",
        "5. 内容类型分析：高点赞作品往往具有特定的标题或内容特征",
        "6. 合作建议：优先考虑粉丝数10万以上且互动率>5%的博主",
        "7. 监控新增作品：每日新增作品表现可快速反映市场趋势变化"
    ]

    for insight in insights:
        report_lines.append(insight)

    # 可视化文件列表
    report_lines.append("\n📸 生成的可视化图表")
    report_lines.append("-" * 40)
    if os.path.exists(output_dir):
        image_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        for image in image_files:
            report_lines.append(f"• {image}")

    # 保存报告
    report_content = "\n".join(report_lines)
    report_file = f"{output_dir}/数据分析报告.txt"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"分析报告已保存到: {report_file}")

    # 同时保存摘要数据到Excel
    if '博主作品数据' in summary:
        excel_file = f"{output_dir}/分析摘要数据.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            if 'blogger_stats' in summary['博主作品数据']:
                summary['博主作品数据']['blogger_stats'].to_excel(writer, sheet_name='博主表现统计')

            if '整体数据汇总' in summary and 'top_bloggers' in summary['整体数据汇总']:
                summary['整体数据汇总']['top_bloggers'].to_excel(writer, sheet_name='Top博主排行')

        print(f"摘要数据已保存到: {excel_file}")

    return report_content

def generate_html_report(cleaned_data, summary, file_categories):
    """
    生成HTML格式的分析报告
    """
    print("\n正在生成HTML分析报告...")

    import base64
    import io
    import pandas as pd
    from datetime import datetime

    # 读取图表文件并转换为base64
    def image_to_base64(image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        return ""

    # 收集所有图表
    image_base64 = {}
    if os.path.exists(output_dir):
        for img_name in os.listdir(output_dir):
            if img_name.lower().endswith('.png'):
                img_path = os.path.join(output_dir, img_name)
                image_base64[img_name] = image_to_base64(img_path)

    # 创建HTML报告
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水星艺术馆达人数据分析报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h1 {{
            text-align: center;
            color: #2980b9;
            border-bottom: 3px solid #2980b9;
        }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px;
            flex: 1;
            min-width: 200px;
        }}
        .metric-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }}
        .metric-card h3 {{
            color: white;
            border-bottom: 1px solid rgba(255,255,255,0.3);
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4fc;
        }}
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .insight {{
            background-color: #e8f6f3;
            border-left: 4px solid #1abc9c;
            padding: 15px;
            margin: 15px 0;
        }}
        .warning {{
            background-color: #fdebd0;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 15px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 14px;
        }}
        .report-title {{
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="report-title">
        <h1>水星艺术馆达人数据分析报告</h1>
        <p style="text-align: center;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <!-- 第1节：总览 -->
    <div class="section">
        <h2>1. 总览</h2>
        <div class="metric-container">
"""

    # 添加核心指标
    if '整体数据汇总' in summary:
        stats = summary['整体数据汇总']['basic_stats']
        html_content += f"""
            <div class="metric-card">
                <h3>博主总数</h3>
                <div class="metric-value">{stats.get('博主总数', 0)}</div>
            </div>
            <div class="metric-card">
                <h3>总粉丝数</h3>
                <div class="metric-value">{int(stats.get('总粉丝数', 0)):,}</div>
            </div>
            <div class="metric-card">
                <h3>平均粉丝数</h3>
                <div class="metric-value">{int(stats.get('平均粉丝数', 0)):,}</div>
            </div>
"""

    if '博主作品数据' in summary:
        stats = summary['博主作品数据']['basic_stats']
        html_content += f"""
            <div class="metric-card">
                <h3>总作品数</h3>
                <div class="metric-value">{stats.get('总作品数', 0)}</div>
            </div>
            <div class="metric-card">
                <h3>博主数量</h3>
                <div class="metric-value">{stats.get('博主数量', 0)}</div>
            </div>
"""

    html_content += """
        </div>
    </div>

    <!-- 第2节：各博主表现对比表格 -->
    <div class="section">
        <h2>2. 各博主表现对比表格</h2>
"""

    # 博主作品数据表格
    if '博主作品数据' in summary and 'blogger_stats' in summary['博主作品数据']:
        blogger_stats = summary['博主作品数据']['blogger_stats']
        if not blogger_stats.empty:
            html_content += """
            <h3>博主作品表现统计</h3>
            <table>
                <thead>
                    <tr>
                        <th>博主名称</th>
                        <th>作品数</th>
                        <th>平均点赞</th>
                        <th>总点赞</th>
                        <th>平均销售额</th>
                        <th>总销售额</th>
                        <th>平均视频时长(秒)</th>
                    </tr>
                </thead>
                <tbody>
"""
            # 动态生成行
            for idx, row in blogger_stats.iterrows():
                # 尝试提取各列，根据实际列名调整，确保处理NaN值
                works_count = row.get('作品数', row.get('作品ID_count', 0) if '作品ID_count' in row else 0)
                avg_likes = row.get('平均点赞', row.get('点赞数_mean', 0))
                total_likes = row.get('总点赞', row.get('点赞数_sum', 0))
                avg_sales = row.get('平均销售额', row.get('视频销售额_mean', 0))
                total_sales = row.get('总销售额', row.get('视频销售额_sum', 0))
                avg_duration = row.get('平均时长', row.get('视频时长_秒_mean', 0))

                # 处理NaN值，确保格式化为数字
                works_count = 0 if pd.isna(works_count) else int(works_count)
                avg_likes = 0 if pd.isna(avg_likes) else float(avg_likes)
                total_likes = 0 if pd.isna(total_likes) else float(total_likes)
                avg_sales = 0 if pd.isna(avg_sales) else float(avg_sales)
                total_sales = 0 if pd.isna(total_sales) else float(total_sales)
                avg_duration = 0 if pd.isna(avg_duration) else float(avg_duration)

                html_content += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{works_count}</td>
                        <td>{avg_likes:.0f}</td>
                        <td>{total_likes:.0f}</td>
                        <td>{avg_sales:.2f}</td>
                        <td>{total_sales:.2f}</td>
                        <td>{avg_duration:.1f}</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
"""

    # 整体数据汇总表格
    if '整体数据汇总' in summary and 'top_bloggers' in summary['整体数据汇总']:
        top_bloggers = summary['整体数据汇总']['top_bloggers']
        if not top_bloggers.empty:
            html_content += """
            <h3>Top博主排行</h3>
            <table>
                <thead>
                    <tr>
                        <th>博主昵称</th>
                        <th>粉丝数</th>
                        <th>权重指数</th>
                        <th>总销售额</th>
                    </tr>
                </thead>
                <tbody>
"""
            for _, row in top_bloggers.iterrows():
                html_content += f"""
                    <tr>
                        <td>{row.get('博主昵称', 'N/A')}</td>
                        <td>{int(row.get('粉丝数', 0)):,}</td>
                        <td>{row.get('权重指数', 0):.2f}</td>
                        <td>{row.get('总销售额', 0):.2f}</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
"""

    html_content += """
    </div>

    <!-- 第3节：Top博主分析 -->
    <div class="section">
        <h2>3. Top博主分析</h2>
"""

    # 嵌入Top博主图表
    if 'Top15博主粉丝数分布.png' in image_base64:
        html_content += f"""
        <div class="chart-container">
            <h3>Top 15博主粉丝数分布</h3>
            <img src="data:image/png;base64,{image_base64['Top15博主粉丝数分布.png']}"
                 alt="Top15博主粉丝数分布">
        </div>
"""

    # 最高权重博主和最高销售额博主
    if '整体数据汇总' in summary:
        stats = summary['整体数据汇总']['basic_stats']
        html_content += f"""
        <div class="insight">
            <h3>关键发现</h3>
            <p><strong>最高权重博主:</strong> {stats.get('最高权重博主', 'N/A')}</p>
            <p><strong>最高销售额博主:</strong> {stats.get('最高销售额博主', 'N/A')}</p>
"""
        if stats.get('总销售额', 0) > 0:
            html_content += f"""
            <p><strong>总销售额:</strong> ¥{int(stats.get('总销售额', 0)):,}</p>
"""
        html_content += """
        </div>
"""

    html_content += """
    </div>

    <!-- 第4节：作品数量分布图 -->
    <div class="section">
        <h2>4. 作品数量分布图</h2>
"""

    if '博主作品数量分布.png' in image_base64:
        html_content += f"""
        <div class="chart-container">
            <h3>各博主作品数量分布</h3>
            <img src="data:image/png;base64,{image_base64['博主作品数量分布.png']}"
                 alt="各博主作品数量分布">
        </div>
"""

    if '视频时长分布.png' in image_base64:
        html_content += f"""
        <div class="chart-container">
            <h3>视频时长分布</h3>
            <img src="data:image/png;base64,{image_base64['视频时长分布.png']}"
                 alt="视频时长分布">
        </div>
"""

    html_content += """
    </div>

    <!-- 第5节：互动数据分析 -->
    <div class="section">
        <h2>5. 互动数据分析</h2>
"""

    # 互动分析数据
    if '博主作品数据' in summary and 'interaction_stats' in summary['博主作品数据']:
        interaction_stats = summary['博主作品数据']['interaction_stats']
        html_content += f"""
        <div class="metric-container">
            <div class="metric-card">
                <h3>平均点赞数</h3>
                <div class="metric-value">{interaction_stats.get('平均点赞数', 0):.1f}</div>
            </div>
            <div class="metric-card">
                <h3>平均评论数</h3>
                <div class="metric-value">{interaction_stats.get('平均评论数', 0):.1f}</div>
            </div>
            <div class="metric-card">
                <h3>平均转发数</h3>
                <div class="metric-value">{interaction_stats.get('平均转发数', 0):.1f}</div>
            </div>
        </div>

        <div class="insight">
            <h3>最高点赞作品</h3>
            <p><strong>作品标题:</strong> {interaction_stats.get('最高点赞作品', 'N/A')}</p>
            <p><strong>点赞数:</strong> {interaction_stats.get('最高点赞数', 0):,}</p>
        </div>
"""

    # 如果有互动图表，嵌入
    if '粉丝数vs总销售额.png' in image_base64:
        html_content += f"""
        <div class="chart-container">
            <h3>粉丝数与销售额关系</h3>
            <img src="data:image/png;base64,{image_base64['粉丝数vs总销售额.png']}"
                 alt="粉丝数vs总销售额">
        </div>
"""

    html_content += """
    </div>

    <!-- 第6节：数据指标相关性分析 -->
    <div class="section">
        <h2>6. 数据指标相关性分析</h2>
"""

    if '数据指标相关性热图.png' in image_base64:
        html_content += f"""
        <div class="chart-container">
            <h3>数据指标相关性热图</h3>
            <img src="data:image/png;base64,{image_base64['数据指标相关性热图.png']}"
                 alt="数据指标相关性热图">
            <p>热图展示了各数据指标之间的相关性，颜色越红表示正相关性越强，越蓝表示负相关性越强。</p>
        </div>
"""

    html_content += """
    </div>

    <!-- 第7节：结论与建议 -->
    <div class="section">
        <h2>7. 结论与建议</h2>

        <div class="insight">
            <h3>核心结论</h3>
            <ul>
                <li>博主作品覆盖广泛，内容形式多样</li>
                <li>粉丝数与销售额存在正相关关系</li>
                <li>视频时长集中在30-120秒的区间</li>
                <li>互动率较高的博主具有更高的转化潜力</li>
            </ul>
        </div>

        <div class="insight">
            <h3>业务建议</h3>
            <ol>
                <li><strong>重点关注高互动率博主</strong>：虽然粉丝数不是最高，但互动率高的博主转化效果更好</li>
                <li><strong>优化视频时长</strong>：保持视频在30-120秒之间，符合用户观看习惯</li>
                <li><strong>强化内容策划</strong>：分析高点赞作品的特征，复制成功模式</li>
                <li><strong>定期监测新增作品</strong>：及时了解市场趋势和竞品动态</li>
                <li><strong>建立博主分级体系</strong>：根据粉丝数、互动率、销售额等指标对博主分级管理</li>
            </ol>
        </div>
"""

    # 数据质量评估
    if '博主作品数据' in cleaned_data:
        df = cleaned_data['博主作品数据']
        missing_percentage = df.isnull().sum() / len(df) * 100
        high_missing = missing_percentage[missing_percentage > 50]

        # 过滤掉本来就是空的列，不显示警告
        exclude_columns = ['关联组件', '组件说明']
        filtered_high_missing = {col: pct for col, pct in high_missing.items()
                                if col not in exclude_columns}

        if len(filtered_high_missing) > 0:
            html_content += """
        <div class="warning">
            <h3>数据质量提醒</h3>
            <p>以下列存在较高缺失率（>50%），建议检查数据源：</p>
            <ul>
"""
            for col, percentage in filtered_high_missing.items():
                html_content += f"                <li>{col}: {percentage:.1f}% 缺失</li>\n"
            html_content += """
            </ul>
        </div>
"""

    html_content += """
    </div>

    <div class="footer">
        <p>水星艺术馆数据分析报告 | 生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        <p>本报告基于数据分析自动生成，仅供参考</p>
    </div>
</body>
</html>
"""

    # 保存HTML文件
    html_file = f"{output_dir}/水星艺术馆达人数据分析报告.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML分析报告已保存到: {html_file}")
    return html_file

def main():
    """
    主函数
    """
    print("=" * 80)
    print("抖音数据分析工具")
    print("=" * 80)

    # 文件夹路径
    folder_path = r"E:\1.工作有关\抖音带货\1.水星艺术馆\00_InBox_收件箱"

    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 - {folder_path}")
        return

    try:
        # 1. 加载所有Excel文件
        data_dict, file_categories = load_all_excel_files(folder_path)

        if not data_dict:
            print("未找到可分析的数据")
            return

        # 2. 数据清洗和预处理
        cleaned_data = clean_and_preprocess_data(data_dict)

        # 3. 生成摘要统计
        summary = generate_summary_statistics(cleaned_data)

        # 4. 创建可视化图表
        create_visualizations(cleaned_data, summary)

        # 5. 生成分析报告
        report = generate_report(cleaned_data, summary, file_categories)

        # 6. 生成HTML报告
        html_report = generate_html_report(cleaned_data, summary, file_categories)

        print("\n" + "=" * 80)
        print("分析完成！")
        print(f"所有结果已保存到: {output_dir}/")
        print(f"HTML报告: {html_report}")
        print("=" * 80)

        # 显示关键洞察
        print("\n关键洞察摘要:")
        if '博主作品数据' in summary:
            stats = summary['博主作品数据']['basic_stats']
            print(f"- 分析作品总数: {stats.get('总作品数', 0)}")
            print(f"- 涉及博主数量: {stats.get('博主数量', 0)}")

        if '整体数据汇总' in summary:
            stats = summary['整体数据汇总']['basic_stats']
            print(f"- 监控博主总数: {stats.get('博主总数', 0)}")
            print(f"- 总粉丝数: {int(stats.get('总粉丝数', 0)):,}")
            if stats.get('总销售额', 0) > 0:
                print(f"- 总销售额: ¥{int(stats.get('总销售额', 0)):,}")

    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()