"""
停顿标签清洗器 - 严格校验与熔断
"""
import re
import sys
import io
from typing import List, Tuple

# 修复 Windows 控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def clean_pause_tags(text: str) -> str:
    """
    清洗停顿标签 <#x#>

    Args:
        text: 原始文本

    Returns:
        清洗后文本
    """
    # Step 1: 提取所有停顿标签及其位置
    pattern = r'<#([\d.]+)#>'
    matches = list(re.finditer(pattern, text))

    if not matches:
        return text

    # Step 2: 构建替换映射
    replacements = []
    i = 0

    while i < len(matches):
        match = matches[i]
        start, end = match.span()
        value = float(match.group(1))

        # Step 2A: 检测连续停顿标签
        consecutive_values = [value]
        j = i + 1

        while j < len(matches):
            next_match = matches[j]
            # 检查是否连续（中间只有空白字符）
            between = text[end:next_match.start()]
            if between.strip() == '':
                consecutive_values.append(float(next_match.group(1)))
                end = next_match.end()
                j += 1
            else:
                break

        # 合并连续停顿（相加并截断）
        merged_value = min(sum(consecutive_values), 98.99)

        # Step 2B: 边界与精度修正
        merged_value = round(merged_value, 2)

        if merged_value < 0.01:
            # 修正为最小值
            merged_value = 0.01
        elif merged_value > 98.99:
            # 截断为最大值
            merged_value = 98.99

        replacements.append((matches[i].start(), end, f'<#{merged_value}#>'))

        i = j

    # Step 3: 执行替换（从后往前，避免索引偏移）
    result = text
    for start, end, replacement in reversed(replacements):
        result = result[:start] + replacement + result[end:]

    # Step 4: 位置校验 - 移除首尾标签
    # 移除开头的停顿标签
    result = re.sub(r'^\s*<#[\d.]+#>\s*', '', result)

    # 移除结尾的停顿标签
    result = re.sub(r'\s*<#[\d.]+#>\s*$', '', result)

    # 移除孤立的停顿标签（前后都是空白或标点）
    result = re.sub(r'(?<=\s)<#[\d.]+#>(?=\s)', ' ', result)
    result = re.sub(r'(?<=^)<#[\d.]+#>(?=\s)', '', result)
    result = re.sub(r'(?<=\s)<#[\d.]+#>(?=$)', '', result)

    # 规范化空格
    result = re.sub(r'\s+', ' ', result).strip()

    return result


# ==================== 测试用例 ====================

def test_clean_pause_tags():
    """极端边界测试"""

    # Test 1: 边界溢出
    assert clean_pause_tags("你好<#0.001#>世界") == "你好<#0.01#>世界"  # < 0.01 修正
    assert clean_pause_tags("你好<#0.01#>世界") == "你好<#0.01#>世界"  # 最小值
    assert clean_pause_tags("你好<#98.99#>世界") == "你好<#98.99#>世界"  # 最大值
    assert clean_pause_tags("你好<#100#>世界") == "你好<#98.99#>世界"  # > 98.99 截断
    assert clean_pause_tags("你好<#999.99#>世界") == "你好<#98.99#>世界"  # 极端溢出

    # Test 2: 精度修正
    assert clean_pause_tags("你好<#1.234#>世界") == "你好<#1.23#>世界"  # 三位小数截断
    assert clean_pause_tags("你好<#1.999#>世界") == "你好<#2.0#>世界"  # 四舍五入
    assert clean_pause_tags("你好<#0.005#>世界") == "你好<#0.01#>世界"  # 小于0.01修正

    # Test 3: 连续标签合并
    assert clean_pause_tags("你好<#1#><#2#>世界") == "你好<#3.0#>世界"  # 相加
    assert clean_pause_tags("你好<#50#><#50#>世界") == "你好<#98.99#>世界"  # 相加后截断
    assert clean_pause_tags("你好<#1#><#2#><#3#>世界") == "你好<#6.0#>世界"  # 三连
    assert clean_pause_tags("你好<#0.5#> <#0.5#>世界") == "你好<#1.0#>世界"  # 中间有空格

    # Test 4: 首尾标签移除
    assert clean_pause_tags("<#1#>你好世界") == "你好世界"  # 开头
    assert clean_pause_tags("你好世界<#1#>") == "你好世界"  # 结尾
    assert clean_pause_tags("<#1#>你好世界<#2#>") == "你好世界"  # 首尾都有
    assert clean_pause_tags("  <#1#>  你好世界  <#2#>  ") == "你好世界"  # 带空格

    # Test 5: 孤立标签
    assert clean_pause_tags("你好 <#1#> 世界") == "你好 世界"  # 前后都是空格

    # Test 6: 复杂组合
    assert clean_pause_tags("<#1#>你好<#0.5#><#0.5#>世界<#2#>") == "你好<#1.0#>世界"
    assert clean_pause_tags("A<#100#><#100#>B<#0.001#>C") == "A<#98.99#>B<#0.01#>C"

    # Test 7: 无标签
    assert clean_pause_tags("你好世界") == "你好世界"
    assert clean_pause_tags("") == ""

    # Test 8: 纯标签
    assert clean_pause_tags("<#1#>") == ""
    assert clean_pause_tags("<#1#><#2#><#3#>") == ""

    print("✅ 所有测试通过")


if __name__ == "__main__":
    test_clean_pause_tags()

    # 实际案例测试
    print("\n" + "="*60)
    print("实际案例测试")
    print("="*60)

    test_cases = [
        "你好<#0.5#>世界",
        "<#1#>开头有标签",
        "结尾有标签<#1#>",
        "连续<#1#><#2#><#3#>标签",
        "溢出<#999#>测试",
        "精度<#1.23456#>测试",
        "你好<#0.001#>世界",
    ]

    for text in test_cases:
        result = clean_pause_tags(text)
        print(f"输入: {text}")
        print(f"输出: {result}")
        print()
