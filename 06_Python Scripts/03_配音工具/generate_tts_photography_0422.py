#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成《摄影构图艺术》配音（风格2和风格3）
使用 Kitta AI TTS API
"""

import requests
import json
import os
import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Kitta AI API配置
API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
API_URL = "https://kittaai.com/api/open/tts"
DEFAULT_REFERENCE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"  # 默认音色

# 输出目录
OUTPUT_DIR = Path("01_Projects_制作中/摄影构图艺术/03_配音_音频")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 文案内容
scripts = {
    "style2_九厘米的雾": """同一景点，为什么别人拍大片？

我看了这本豆瓣8.0分的摄影书，发现一个秘密——会拍照的人，就是在帮你的眼睛做选择。

有些照片能勾住你的视线，有些却让你一眼扫过。为什么？

我测试了一周，拍了20张照片发朋友圈。用三分法构图的，平均50个赞；居中构图的，只有10个赞。

差别就在按快门前的那3秒钟——你在想什么？

这本《摄影构图艺术》告诉你：构图不是背公式，而是在跟观众的眼睛对话。

作者Richard Garvey-Williams是职业摄影师，他把视觉心理学讲成了人话。

从"知道怎么拍"到"知道为什么这么拍"，这就是定价权的来源。""",

    "style3_AdScout": """拍了1000张，朋友圈没人点赞？

我之前也是，换了更贵的相机、学了三分法、背了黄金分割，照片还是平平无奇。

直到我看了这本《摄影构图艺术》，才发现问题在哪——你和会拍照的人，差的不是技巧，是审美。

同一个场景，我用手机拍了两张，一张裁掉了杂乱的背景，一张没裁。你看差别——朋友圈点赞从10个涨到50个。

这本书告诉我，好照片最关键的不是技术，是情感共鸣。技术永远是为情感服务的。

这不是教你按快门，而是教你怎么想。

想从"模仿"升级到"创造"？评论区有链接。"""
}

def generate_tts(text: str, output_file: str, reference_id: str = None, version: str = "s1"):
    """
    调用 Kitta AI TTS API 生成语音

    Args:
        text: 文案文本
        output_file: 输出文件路径
        reference_id: 音色参考ID
        version: API版本（s1或s2）
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "version": version,
        "format": "wav"
    }

    if reference_id:
        payload["reference_id"] = reference_id

    print(f"正在生成：{output_file}")
    print(f"  版本：{version}, 音色ID：{reference_id or '默认'}")

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            # 保存音频文件
            with open(output_file, "wb") as f:
                f.write(response.content)

            file_size = os.path.getsize(output_file) / 1024
            print(f"[SUCCESS] 生成成功：{output_file} ({file_size:.2f} KB)")
            return True
        else:
            print(f"[ERROR] API返回 {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 生成失败：{e}")
        return False

def main():
    """生成所有配音"""
    print("=" * 60)
    print("《摄影构图艺术》配音生成")
    print("=" * 60)

    # 生成配音
    results = []
    for style_name, text in scripts.items():
        output_file = OUTPUT_DIR / f"0422-摄影构图艺术-{style_name}.wav"

        # 使用默认音色
        success = generate_tts(text, str(output_file), reference_id=DEFAULT_REFERENCE_ID, version="s1")
        results.append((style_name, success))

    # 汇总结果
    print("\n" + "=" * 60)
    print("生成结果汇总")
    print("=" * 60)
    for style_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} - {style_name}")

    success_count = sum(1 for _, success in results if success)
    print(f"\n总计：{success_count}/{len(results)} 个配音生成成功")

if __name__ == "__main__":
    main()
