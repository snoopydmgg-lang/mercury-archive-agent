import pandas as pd
import sys

# 读取 Excel
df = pd.read_excel('00_InBox_收件箱/作品列表.xlsx')

# 打印列名
print("列名:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print(f"\n总行数: {len(df)}")
print(f"\n前10行数据:")

# 打印前10行，每行单独处理
for idx in range(min(10, len(df))):
    row = df.iloc[idx]
    print(f"\n--- 第 {idx+1} 行 ---")
    for col in df.columns:
        value = row[col]
        if pd.notna(value):
            print(f"{col}: {value}")
