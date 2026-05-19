#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析收件箱中的最新作品数据
"""

import pandas as pd
import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def analyze_video_data(file_path):
    """分析视频作品数据"""
    print(f"\n{'='*60}")
    print(f"文件: {Path(file_path).name}")
    print(f"{'='*60}")

    try:
        df = pd.read_excel(file_path)

        print(f"\n总行数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print(f"\n列名: {list(df.columns)}")

        # 显示前10行
        print(f"\n前10行数据:")
        print(df.head(10).to_string())

        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"\n数值列统计:")
            print(df[numeric_cols].describe().to_string())

        # 如果有日期列，显示时间范围
        date_cols = [col for col in df.columns if '时间' in col or '日期' in col or 'time' in col.lower() or 'date' in col.lower()]
        if date_cols:
            print(f"\n时间范围:")
            for col in date_cols:
                try:
                    print(f"{col}: {df[col].min()} ~ {df[col].max()}")
                except:
                    pass

        return df

    except Exception as e:
        print(f"读取失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    inbox_dir = Path("E:/1.work/douyin/1.shuixing/00_InBox_收件箱")

    # 读取所有 Excel 文件
    excel_files = list(inbox_dir.glob("*.xlsx"))

    print(f"找到 {len(excel_files)} 个 Excel 文件")

    for file_path in excel_files:
        if '复盘报告' not in file_path.name:  # 跳过复盘报告
            df = analyze_video_data(file_path)
            if df is not None:
                print(f"\n数据已读取，共 {len(df)} 条记录")

if __name__ == "__main__":
    main()
