#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import sys

def analyze_excel_files(folder_path):
    """
    分析指定文件夹中的所有Excel文件
    """
    # 获取所有Excel文件
    excel_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(root, file))

    print(f"找到 {len(excel_files)} 个Excel文件:")
    for f in excel_files:
        print(f"  - {os.path.basename(f)}")
    print()

    results = []

    for file_path in excel_files:
        try:
            print(f"正在分析: {os.path.basename(file_path)}")
            print("-" * 50)

            # 读取Excel文件的所有工作表名
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names

            print(f"工作表数量: {len(sheet_names)}")

            file_info = {
                'file_name': os.path.basename(file_path),
                'file_path': file_path,
                'sheets': []
            }

            for sheet_name in sheet_names:
                print(f"\n  工作表: '{sheet_name}'")

                # 读取工作表数据
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)  # 只读取表头
                    columns = list(df.columns)
                    print(f"    列数: {len(columns)}")
                    print(f"    列名: {columns}")

                    # 获取总行数（包含表头）
                    df_full = pd.read_excel(file_path, sheet_name=sheet_name)
                    total_rows = len(df_full)
                    print(f"    数据行数: {total_rows - 1} (不含表头)")

                    # 检查是否有缺失值
                    missing_counts = df_full.isnull().sum()
                    missing_cols = missing_counts[missing_counts > 0]
                    if len(missing_cols) > 0:
                        print(f"    警告: 以下列存在缺失值:")
                        for col, count in missing_cols.items():
                            print(f"      - {col}: {count} 个缺失值")

                    sheet_info = {
                        'sheet_name': sheet_name,
                        'columns': columns,
                        'total_rows': total_rows,
                        'data_rows': total_rows - 1,
                        'missing_cols': missing_cols.to_dict() if len(missing_cols) > 0 else {}
                    }

                    file_info['sheets'].append(sheet_info)

                except Exception as e:
                    print(f"    读取工作表时出错: {e}")
                    sheet_info = {
                        'sheet_name': sheet_name,
                        'error': str(e)
                    }
                    file_info['sheets'].append(sheet_info)

            results.append(file_info)
            print("\n")

        except Exception as e:
            print(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
            print("\n")

    # 输出汇总信息
    print("=" * 80)
    print("数据结构汇总")
    print("=" * 80)

    for file_info in results:
        print(f"\n文件: {file_info['file_name']}")
        print(f"路径: {file_info['file_path']}")

        for sheet_info in file_info['sheets']:
            print(f"  工作表: {sheet_info['sheet_name']}")
            if 'error' in sheet_info:
                print(f"    错误: {sheet_info['error']}")
            else:
                print(f"    数据行数: {sheet_info['data_rows']}")
                print(f"    列数: {len(sheet_info['columns'])}")
                print(f"    列名: {sheet_info['columns']}")
                if sheet_info['missing_cols']:
                    print(f"    缺失值列: {sheet_info['missing_cols']}")
        print()

if __name__ == "__main__":
    folder_path = r"E:\1.工作有关\抖音带货\1.水星艺术馆\00_InBox_收件箱"

    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        sys.exit(1)

    analyze_excel_files(folder_path)