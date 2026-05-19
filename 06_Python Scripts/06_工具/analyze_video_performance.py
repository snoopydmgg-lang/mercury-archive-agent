#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音视频流量分析工具
读取作品列表和下载明细，分析流量低迷原因
"""

import pandas as pd
import sys
import os

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

def read_excel_files():
    """读取Excel文件"""
    base_path = "E:/1.work/douyin/1.shuixing/00_InBox_收件箱"

    # 读取作品列表
    works_file = os.path.join(base_path, "作品列表.xlsx")
    download_file = os.path.join(base_path, "短视频下载明细.xlsx")

    print("=" * 80)
    print("【作品列表数据】")
    print("=" * 80)

    try:
        df_works = pd.read_excel(works_file)
        print(f"\n总记录数: {len(df_works)}")
        print(f"\n列名: {list(df_works.columns)}")
        print("\n前10行数据:")
        print(df_works.head(10).to_string())

        print("\n\n数据统计:")
        print(df_works.describe())

    except Exception as e:
        print(f"读取作品列表失败: {e}")
        df_works = None

    print("\n\n" + "=" * 80)
    print("【短视频下载明细数据】")
    print("=" * 80)

    try:
        df_download = pd.read_excel(download_file)
        print(f"\n总记录数: {len(df_download)}")
        print(f"\n列名: {list(df_download.columns)}")
        print("\n前10行数据:")
        print(df_download.head(10).to_string())

        print("\n\n数据统计:")
        print(df_download.describe())

    except Exception as e:
        print(f"读取下载明细失败: {e}")
        df_download = None

    return df_works, df_download

if __name__ == "__main__":
    read_excel_files()
