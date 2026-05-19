#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《摄影构图艺术》配音（风格2和风格3）
使用 Kitta AI TTS API + 文本预处理器
"""

import sys
import os
from pathlib import Path

# 添加工具路径
sys.path.insert(0, str(Path(__file__).parent.parent / "06_工具"))

from tts_kitta_refactored import KittaTTS

# 配置
DEFAULT_REFERENCE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"  # 默认音色
OUTPUT_DIR = Path("01_Projects_制作中/摄影构图艺术/03_配音_音频")

# 文案内容（从 MD 文件提取的纯口播文案）
scripts = {
    "style2_九厘米的雾": """
好照片不是拍出来的，是"设计"出来的。这就是职业摄影师和业余爱好者的差距。

差别就在按快门前的3秒钟。

职业摄影师都在用一个方法：把人物放在左侧1/3处，右侧留白。

你以为是公式？其实是在操纵你的眼睛——人的视线会沿着留白的方向移动，这就是照片的"呼吸感"。

我拿这个方法测试了一周，拍了20张照片。点赞率从3%涨到8%。

这本《摄影构图艺术》讲透了一件事——会拍照的人，就是在帮你的眼睛做选择。

豆瓣8.0分，376人推荐。翻开它，你会发现：职业摄影师和业余爱好者的差距，就在这3秒钟。

从"知道怎么拍"到"知道为什么这么拍"，这就是职业摄影师能多收3倍钱的原因。
""",
    "style3_AdScout": """
职业摄影师报价能高3倍，不是因为相机贵，而是因为他们懂一件事。

换了更贵的相机、学了三分法，照片还是平平无奇。

问题不在技巧，在审美。

测试数据显示：用三分法构图的照片，点赞率平均8%；居中构图的照片，只有3%。

会拍照的人，就是在帮你的眼睛做选择。你看这张照片，人物放在左侧，右侧留白，你的视线是不是自然地往右移动？这就是构图的"操纵术"。

豆瓣8.0分，376人推荐。从"模仿"升级到"创造"，拍出自己的风格。

评论区有链接。
"""
}

def main():
    """生成所有配音"""
    print("=" * 60)
    print("《摄影构图艺术》配音生成（使用预处理器）")
    print("=" * 60)

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 初始化 TTS 客户端
    client = KittaTTS(reference_id=DEFAULT_REFERENCE_ID)
    client.set_model("s2_chinese")  # 使用中文模型

    # 生成配音
    results = []
    for style_name, text in scripts.items():
        output_file = OUTPUT_DIR / f"0422-摄影构图艺术-{style_name}.wav"

        print(f"\n正在生成：{style_name}")
        print(f"输出路径：{output_file}")

        success = client.generate(
            text=text.strip(),
            output_path=str(output_file),
            version="s1",
            format="wav",
            strict_mode=False  # 非严格模式，允许警告
        )

        results.append((style_name, success))

    # 汇总结果
    print("\n" + "=" * 60)
    print("生成结果汇总")
    print("=" * 60)
    for style_name, success in results:
        status = "[SUCCESS]" if success else "[FAILED]"
        print(f"{status} - {style_name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n总计：{success_count}/{len(results)} 个配音生成成功")

if __name__ == "__main__":
    main()
