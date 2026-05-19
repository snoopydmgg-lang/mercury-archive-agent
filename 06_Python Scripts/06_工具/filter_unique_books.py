"""
选品二次筛选：排除烂大街的书
"""

import pandas as pd

def is_overused_book(title, category):
    """判断是否为烂大街的书"""

    # 烂大街的书籍特征
    overused_keywords = [
        # 网红书/畅销书（到处都在卖）
        '刘同', '早上好', '岛上好',  # 刘同新书
        '樊登', '读书卡', 'VIP',  # 樊登读书卡
        '斑马', '百科',  # 斑马百科
        '一句顶一万句', '刘震云',  # 畅销书
        '莫言', '民间故事',  # 诺奖作家畅销书
        '余华', '活着', '许三观',  # 畅销书
        '路遥', '平凡的世界',  # 畅销书
        '茅盾文学奖', '诺奖',  # 获奖标签（烂大街）

        # 教辅类（虽然已排除，但可能有漏网之鱼）
        '中考', '高考', '小学', '中学', '试卷', '练习', '辅导',
        '数学思想', '解题', '押题', '冲刺', '模拟',

        # 儿童读物（虽然已排除，但可能有漏网之鱼）
        '绘本', '幼儿', '少儿', '亲子', '早教', '儿童安全',

        # 鸡汤/成功学/实用工具书
        '反内耗', '养育', '家庭教育', '育儿', '正面管教',
        '高手', '社交', '说话', '沟通', '情商',
        '理财', '赚钱', '投资', '财富',  # 理财类（不符合艺术调性）
        '妙方', '秘方', '偏方',  # 实用工具书

        # 医学养生（虽然已排除，但可能有漏网之鱼）
        '本草', '偏方', '药方', '养生', '健康', '中医',
        '角药', '方子', '配伍',

        # 烂大街的经典（到处都在卖，没有差异化空间）
        '四大名著', '红楼梦', '西游记', '水浒传', '三国演义',
        '论语', '孟子', '大学', '中庸',  # 四书
        '道德经', '老子', '庄子',  # 道家经典
        '孙子兵法', '三十六计',  # 兵法
        '史记', '资治通鉴',  # 史书

        # 新书/限定版（容易过时）
        '2026', '2025', '新书', '首刷', '限定', '签名',

        # 套装/合集（太泛，没有聚焦点）
        '套装', '全集', '合集', '系列', '礼盒',

        # 漫画版经典（降维产品）
        '漫画', '彩绘', '图解', '绘本',
    ]

    text = str(title) + str(category)
    return any(keyword in text for keyword in overused_keywords)

def filter_unique_books(input_file, output_file):
    """筛选出有差异化空间的书"""

    # 读取数据
    print("正在读取数据...")
    df = pd.read_excel(input_file)
    print(f"筛选前: {len(df)} 个商品")

    # 排除烂大街的书
    print("\n正在排除烂大街的书...")
    df['是否烂大街'] = df.apply(lambda row: is_overused_book(row['商品名称'], row['类目']), axis=1)

    filtered = df[df['是否烂大街'] == False].copy()

    print(f"筛选后: {len(filtered)} 个商品")
    print(f"排除了: {len(df) - len(filtered)} 个烂大街的书")

    # 保存结果
    filtered.to_excel(output_file, index=False)
    print(f"\n[OK] 结果已保存到: {output_file}")

    # 打印前20个
    print("\n" + "="*80)
    print("TOP 20 精选商品（排除烂大街）:")
    print("="*80)

    for idx, row in filtered.head(20).iterrows():
        print(f"\n[{int(row['排行'])}] {row['商品名称']}")
        print(f"  类目: {row['类目']}")
        print(f"  客单价: {row['估算客单价']:.0f}元 | 销量: {row['商品销量']}")
        print(f"  视频占比: {row['视频出单占比']:.0f}%")
        print(f"  链接: {row['商品链接']}")

    print("\n" + "="*80)
    print(f"[OK] 筛选完成！共找到 {len(filtered)} 个精选商品")
    print("="*80)

    return filtered

if __name__ == "__main__":
    input_file = "00_InBox_收件箱/筛选结果_文史哲艺术类图书.xlsx"
    output_file = "00_InBox_收件箱/精选结果_差异化图书.xlsx"

    result = filter_unique_books(input_file, output_file)
