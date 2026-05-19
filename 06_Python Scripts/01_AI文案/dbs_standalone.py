#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBS 独立检定工具
对已生成的文案进行 DBS 五维诊断
"""

import sys
import io
from pathlib import Path
from anthropic import Anthropic

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

CLAUDE_API_KEY = "sk-of-nOFEkAjpTRCMWdrETGUHrfTtnrIFjJlrsadTvfGuCZYMXhiAgIPqSAYtkakODUWs"
CLAUDE_BASE_URL = "https://api.ofox.ai/anthropic"

def read_file(filepath):
    """读取文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def dbs_check(content):
    """DBS 五维检定"""
    client = Anthropic(api_key=CLAUDE_API_KEY, base_url=CLAUDE_BASE_URL)

    prompt = f"""
# 任务
你是 dontbesilent 的内容创作诊断 AI。请对以下短视频文案进行五维诊断。

# 文案内容
{content}

# 诊断维度
1. **文字洁癖检测** - 有无 AI 味、emoji 堆叠、空洞排比句、过度修饰
2. **封面/标题诊断** - 是否自带吸引力、认知劫持效果、能否 3 秒抓住注意力
3. **表达效率检测** - 核心观点是否清晰、有无冗余、信息密度是否合理
4. **认知落差检测** - 相比同行是否有明显差异化、是否提供新视角
5. **情绪共鸣检测** - 是否触达用户痛点、是否有情感张力

# 输出格式
## 诊断结果

| 维度 | 判断 | 说明 |
|------|------|------|
| 文字洁癖 | ✅/⚠️/❌ | 具体问题 |
| 封面/标题 | ✅/⚠️/❌ | 具体问题 |
| 表达效率 | ✅/⚠️/❌ | 具体问题 |
| 认知落差 | ✅/⚠️/❌ | 具体问题 |
| 情绪共鸣 | ✅/⚠️/❌ | 具体问题 |

## 改进建议
[具体的修改建议，如果判断为 ✅ 则说明"无需修改"]

## 一句话总结
[犀利的总结]
"""

    response = client.messages.create(
        model="anthropic/claude-haiku-4.5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.content[0].text

def main():
    if len(sys.argv) < 2:
        print("用法: python dbs_standalone.py <文案文件路径>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"错误：文件不存在 {filepath}")
        sys.exit(1)

    print("=" * 70)
    print("DBS 内容诊断工具")
    print("=" * 70)
    print(f"\n文件: {filepath}")
    print("\n正在读取文案...")

    content = read_file(filepath)

    # 分割三套文案
    sections = content.split("## 余上沅的奇妙屋")
    if len(sections) < 2:
        print("错误：无法识别文案格式")
        sys.exit(1)

    # 提取三种风格
    styles = {
        "余上沅的奇妙屋": content.split("## 余上沅的奇妙屋")[1].split("## 九厘米的雾")[0],
        "九厘米的雾": content.split("## 九厘米的雾")[1].split("## Ad Scout")[0],
        "Ad Scout": content.split("## Ad Scout")[1]
    }

    results = {}

    for style_name, style_content in styles.items():
        print(f"\n{'=' * 70}")
        print(f"检定: {style_name}")
        print("=" * 70)

        result = dbs_check(style_content)
        results[style_name] = result

        print(f"\n{result}")

    # 保存结果
    output_path = filepath.parent / f"{filepath.stem}-DBS检定报告.md"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# DBS 检定报告\n\n")
        f.write(f"文件: {filepath.name}\n\n")
        f.write("---\n\n")

        for style_name, result in results.items():
            f.write(f"## {style_name}\n\n")
            f.write(f"{result}\n\n")
            f.write("---\n\n")

    print(f"\n{'=' * 70}")
    print(f"✓ 检定报告已保存: {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
