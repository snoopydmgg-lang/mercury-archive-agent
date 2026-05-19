"""
CodeSOME 使用数据分析脚本
"""
import pandas as pd
import sys
import os

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_usage(csv_path):
    """分析 CodeSOME 使用数据"""

    # 读取 CSV
    df = pd.read_csv(csv_path)

    # 基础统计
    print('=' * 60)
    print('CodeSOME 使用统计 (2026-04-25 至 2026-05-01)')
    print('=' * 60)
    print(f'\n总调用次数: {len(df)}')
    print(f'时间范围: {df["Time"].min()} 至 {df["Time"].max()}\n')

    # 模型统计
    print('=' * 60)
    print('模型使用分布')
    print('=' * 60)
    print(df['Model'].value_counts())
    print()

    # 成本统计
    print('=' * 60)
    print('成本统计')
    print('=' * 60)
    total_billed = df["Billed Cost"].sum()
    total_original = df["Original Cost"].sum()
    print(f'总成本 (Billed): ${total_billed:.4f} ≈ ¥{total_billed * 7.2:.2f}')
    print(f'原始成本 (Original): ${total_original:.4f} ≈ ¥{total_original * 7.2:.2f}')
    print(f'费率倍数: {total_billed / total_original:.2f}x')
    print(f'平均单次成本: ${df["Billed Cost"].mean():.4f}')
    print(f'最高单次成本: ${df["Billed Cost"].max():.4f}')
    print(f'最低单次成本: ${df["Billed Cost"].min():.4f}')
    print()

    # Token 统计
    print('=' * 60)
    print('Token 消耗统计')
    print('=' * 60)
    total_input = df["Input Tokens"].sum()
    total_output = df["Output Tokens"].sum()
    total_cache_read = df["Cache Read Tokens"].sum()
    total_cache_creation = df["Cache Creation Tokens"].sum()

    print(f'总 Input Tokens: {total_input:,}')
    print(f'总 Output Tokens: {total_output:,}')
    print(f'总 Cache Read Tokens: {total_cache_read:,}')
    print(f'总 Cache Creation Tokens: {total_cache_creation:,}')
    print(f'平均 Input Tokens: {df["Input Tokens"].mean():.0f}')
    print(f'平均 Output Tokens: {df["Output Tokens"].mean():.0f}')
    print(f'缓存命中率: {total_cache_read / (total_input + total_cache_read) * 100:.1f}%')
    print()

    # 按日期统计
    print('=' * 60)
    print('每日消耗统计')
    print('=' * 60)
    df['Date'] = pd.to_datetime(df['Time']).dt.date
    daily = df.groupby('Date').agg({
        'Billed Cost': 'sum',
        'Input Tokens': 'sum',
        'Output Tokens': 'sum'
    })
    daily['Billed Cost (¥)'] = daily['Billed Cost'] * 7.2
    print(daily)
    print()

    # 推理模式统计
    print('=' * 60)
    print('推理模式分布')
    print('=' * 60)
    print(df['Reasoning Effort'].value_counts())
    print()

    # 计费模式统计
    print('=' * 60)
    print('计费模式分布')
    print('=' * 60)
    print(df['Billing Mode'].value_counts())
    billing_cost = df.groupby('Billing Mode')['Billed Cost'].sum()
    print('\n各计费模式总成本:')
    for mode, cost in billing_cost.items():
        print(f'  {mode}: ${cost:.4f} ≈ ¥{cost * 7.2:.2f}')
    print()

    # 时段分析
    print('=' * 60)
    print('时段分析')
    print('=' * 60)
    df['Hour'] = pd.to_datetime(df['Time']).dt.hour
    hourly = df.groupby('Hour').agg({
        'Billed Cost': 'sum',
        'Input Tokens': 'sum'
    }).sort_values('Billed Cost', ascending=False)
    print('消耗最高的5个时段:')
    print(hourly.head(5))
    print()

    # 性能统计
    print('=' * 60)
    print('性能统计')
    print('=' * 60)
    print(f'平均首 Token 时间: {df["First Token (ms)"].mean():.0f} ms')
    print(f'平均总时长: {df["Duration (ms)"].mean():.0f} ms')
    print(f'最快首 Token: {df["First Token (ms)"].min():.0f} ms')
    print(f'最慢首 Token: {df["First Token (ms)"].max():.0f} ms')
    print()

    return df

if __name__ == "__main__":
    csv_path = "E:/1.work/douyin/1.shuixing/00_InBox_收件箱/usage_2026-04-25_to_2026-05-01.csv"
    df = analyze_usage(csv_path)
