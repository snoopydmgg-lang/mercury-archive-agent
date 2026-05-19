#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《我等你》三套文案配音生成
"""
import sys
import io
import requests
import json
from pathlib import Path

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Kitta AI TTS 配置
API_URL = "https://kittaai.com/api/open/tts"
API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
VOICE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"

# 输出目录（强制规则：必须输出到项目文件夹）
OUTPUT_DIR = Path("E:/1.work/douyin/1.shuixing/01_Projects_制作中/我等你/03_配音_音频")

# 三套文案
scripts = {
    "余上沅": """你有多久没被一本书震撼到失语？

法国绘本天后海贝卡·朵特梅耗时7000小时打造的《我等你》，212页全激光纸雕，每一页都是精密舞台。

纸张厚实，镂空细腻，拿在手里有分量。把书立起来，整个场景瞬间立体展开，小路蜿蜒、房屋错落、花草鲜活，光影穿过纸雕缝隙，画面像活了一样。

故事讲的是两只兔子的约会。明明约好中午十二点见面，他却九点二十分就迫不及待出发。从家里出发，一路紧张又期待。

最打动人的是这句话：约会不是从见面才开始，从约定那一刻，浪漫就已经发生了。全书没有一句"我爱你"，却通篇都是"我爱你"的故事。

小孩看热闹，大人看门道。

不管是自留治愈，还是送给爱人、挚友、家人，都远比普通礼物更有分量。这本书就是一句告白：有人值得你等待，也永远有人在等你。""",

    "九厘米的雾": """这哪是书，明明是艺术品。

法国绘本天后海贝卡的《我等你》，首印14500本，7天售罄，一书难求。

为什么这么火？因为它把一个关于等待的故事，做成了212页可以手动播放的纸上电影。

全激光雕刻，细如发丝的平面细节。即使书上只有一两毫米的叶片，都富有深浅冷暖的层次感。当你把书立起来，光影穿透镂空，每一页都像自带光影的绝美电影画面。

约好中午十二点见面，九点二十分就已经开始等你了。这句话就像一颗糖含在嘴里，甜得让人眼眶发热。

从等待到相遇，每一帧都是情绪。

豆瓣9.8分，法国2019年度创意书大奖。价格不算低，但拿到手就知道有多值。

这不只是一本书，而是一件可以捧在掌心的告白。如果等待真的有结果，那再等一等又何妨？""",

    "AdScout": """男生留下，女孩子把视频转发给男朋友，立马划走。这不是演习。

送TA这本书，就是送上一捧掌心的法式浪漫剧场。

《我等你》耗时7000小时精心打造，212页全激光纸雕，每一页都是精心雕刻的艺术品。

节日不知道送啥？怕撞款？怕没诚意？情人节、纪念日、生日送她再合适不过。比鲜花更持久，比普通礼物更有仪式感。

约好中午十二点见面，九点二十分就已经开始等你了。全书没有一句"我爱你"，却通篇都是"我爱你"的故事。

把书立起来的那一刻，整个场景瞬间立体展开，光影穿过纸雕缝隙，画面像活了一样。

告白、纪念日、节日，礼物首选。封底印有"我等你"，未说出口的心意藏进指尖光影。

适合作为追求、异地恋、和好或惊喜场景的礼物，传递心意。价格不算低，但拿到手就知道有多值，仪式感满满，心意藏不住。"""
}

def generate_tts(text, output_path):
    """调用 Kitta AI TTS API 生成配音"""
    print(f"   📡 正在调用 Kitta AI TTS API...")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "reference_id": VOICE_ID,
        "version": "s1",
        "format": "wav"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"   ✅ 配音生成成功")
            return True
        else:
            print(f"   ❌ API 调用失败")
            print(f"      状态码: {response.status_code}")
            print(f"      响应: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ 发生异常：{e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    print("=" * 60)
    print("  《我等你》三套文案配音生成")
    print("=" * 60)
    print()

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 输出目录：{OUTPUT_DIR}")
    print()

    success_count = 0
    fail_count = 0

    for style, text in scripts.items():
        print(f"🎙️  正在生成：{style} 风格")

        output_path = OUTPUT_DIR / f"配音-{style}.wav"

        if generate_tts(text, output_path):
            file_size = output_path.stat().st_size / 1024 / 1024  # MB
            print(f"   📄 文件大小：{file_size:.2f} MB")
            print(f"   📂 保存路径：{output_path}")
            success_count += 1
        else:
            fail_count += 1

        print()

    print("=" * 60)
    print(f"📊 执行结果：成功 {success_count}/3，失败 {fail_count}/3")

    if success_count == 3:
        print()
        print("✅ 所有配音已生成完成")
        print()
        print("📋 配音文件清单：")
        print(f"   - 风格1（余上沅）：{OUTPUT_DIR}/配音-余上沅.wav")
        print(f"   - 风格2（九厘米的雾）：{OUTPUT_DIR}/配音-九厘米的雾.wav")
        print(f"   - 风格3（AdScout）：{OUTPUT_DIR}/配音-AdScout.wav")

    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 程序异常退出：{e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
