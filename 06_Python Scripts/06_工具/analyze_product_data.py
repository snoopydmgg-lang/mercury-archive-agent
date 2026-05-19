#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析商品数据 Excel 文件
"""

import pandas as pd
import sys
import os
from pathlib import Path
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def analyze_excel(file_path):
    """分析单个 Excel 文件"""
    print(f"\n{'='*60}")
    print(f"文件: {Path(file_path).name}")
    print(f"{'='*60}")

    try:
        # 读取 Excel
        df = pd.read_excel(file_path)

        # 基本信息
        print(f"\n总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print(f"\n列名: {list(df.columns)}")

        # 显示前几行数据
        print(f"\n前5行数据:")
        print(df.head().to_string())

        # 如果有数值列，显示统计信息
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"\n数值列统计:")
            print(df[numeric_cols].describe().to_string())

        return df

    except Exception as e:
        print(f"读取失败: {e}")
        return None

def main():
    # 数据文件目录
    data_dir = Path("E:/1.work/douyin/1.shuixing/.playwright-mcp")

    # 查找所有商品数据文件
    product_files = list(data_dir.glob("*商品详情*.xlsx"))

    print(f"找到 {len(product_files)} 个商品数据文件")

    all_data = []
    for file_path in product_files:
        df = analyze_excel(file_path)
        if df is not None:
            # 提取产品名称
            product_name = file_path.stem.split('-')[-1] if '-' in file_path.stem else "未知"
            df['产品名称'] = product_name
            all_data.append(df)

    # 合并所有数据
    if all_data:
        print(f"\n{'='*60}")
        print("汇总分析")
        print(f"{'='*60}")
        combined = pd.concat(all_data, ignore_index=True)
        print(f"\n总计 {len(combined)} 条记录")

        # 按产品分组统计
        if '产品名称' in combined.columns:
            print(f"\n各产品数据量:")
            print(combined['产品名称'].value_counts().to_string())

if __name__ == "__main__":
    main()
