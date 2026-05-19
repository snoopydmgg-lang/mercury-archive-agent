import pandas as pd
from datetime import datetime

# 读取 Excel
df = pd.read_excel('00_InBox_收件箱/作品列表.xlsx')

# 重命名列（根据位置）
df.columns = ['作品标题', '发布时间', '时长', '作品状态', '播放量', '完播率', '5s完播率', '平均完播率', '2s跳出率', '平均播放时长', '点赞数', '分享数', '评论数', '收藏数', '主页访问', '涨粉数']

# 转换发布时间
df['发布时间'] = pd.to_datetime(df['发布时间'])

# 筛选上周数据（4月19日-4月25日）
start_date = datetime(2026, 4, 19)
end_date = datetime(2026, 4, 26)
last_week = df[(df['发布时间'] >= start_date) & (df['发布时间'] < end_date)]

print("=" * 80)
print("上周发布作品统计（2026-04-19 ~ 2026-04-25）")
print("=" * 80)
print(f"\n上周发布数量: {len(last_week)} 条")

if len(last_week) > 0:
    print("\n上周发布作品列表:")
    print("-" * 80)
    for idx, row in last_week.iterrows():
        print(f"\n【作品 {idx+1}】")
        print(f"标题: {row['作品标题'][:50]}...")
        print(f"发布时间: {row['发布时间']}")
        print(f"播放量: {row['播放量']}")
        print(f"点赞: {row['点赞数']} | 收藏: {row['收藏数']} | 评论: {row['评论数']} | 分享: {row['分享数']}")
        print(f"涨粉: {row['涨粉数']}")
        print(f"完播率: {row['完播率']*100:.2f}% | 2s跳出率: {row['2s跳出率']*100:.2f}%")

    # 统计数据
    print("\n" + "=" * 80)
    print("上周数据汇总")
    print("=" * 80)
    print(f"总播放量: {last_week['播放量'].sum():,}")
    print(f"总点赞数: {last_week['点赞数'].sum()}")
    print(f"总收藏数: {last_week['收藏数'].sum()}")
    print(f"总分享数: {last_week['分享数'].sum()}")
    print(f"总涨粉数: {last_week['涨粉数'].sum()}")
    print(f"平均完播率: {last_week['完播率'].mean()*100:.2f}%")
    print(f"平均2s跳出率: {last_week['2s跳出率'].mean()*100:.2f}%")

# 全部作品统计
print("\n" + "=" * 80)
print("全部作品统计（共 {} 条）".format(len(df)))
print("=" * 80)
print(f"总播放量: {df['播放量'].sum():,}")
print(f"播放量中位数: {df['播放量'].median()}")
print(f"最高播放量: {df['播放量'].max():,}")

# 保存到 CSV
output_file = '00_InBox_收件箱/作品列表_清洗版.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n已保存清洗版数据到: {output_file}")
