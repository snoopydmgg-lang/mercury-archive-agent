# -*- coding: utf-8 -*-
"""
飞鸟集 3条文案配音
使用 Kitta AI TTS API
"""
import sys
import io
import os
import requests
import re
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
REFERENCE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"
OUTPUT_DIR = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/飞鸟集/01_素材_试用装/配音"

# 3条飞鸟集文案
SCRIPTS = {
    "1_Ad_Scout": {
        "name": "Ad Scout风格",
        "text": """你以为《飞鸟集》只是心灵鸡汤？错了——亚洲首位诺奖得主、1913年获奖、影响全球100年。

更狠的是什么？1922年，郑振铎用白话散文诗翻译它——打破文言主流，开创白话翻译先河。叶芝说过一句话：每天读一句泰戈尔的诗，可以让我忘却世间的一切痛苦。这不是鸡汤，这是认知密度。

440克巴掌本、三面天空蓝刷边、布面精装、护封镶嵌金银两色线——每本书的线条轨迹都不同，寓意鸟儿飞行轨迹。还有独家限量羽毛编码，一书一码，你手里这本全世界独一份。

325首短诗，中英双语对照，全新手绘插画。"生如夏花之绚烂，死如秋叶之静美"——四个字说透生命本质。你以为读诗没用？其实诗训练的是你对世界的敏锐度，是思考间隙里的幸福感。

这不是普通诗集，是可以收藏的文学遗产。放在书架是艺术品，翻开是精神避难所。羽毛编码限量发售，错过就是绝版。"""
    },
    "2_余上沅": {
        "name": "余上沅的奇妙屋风格",
        "text": """"生如夏花之绚烂"——郑振铎1922年用白话翻译它，百年后仍是中文世界标杆。

很多人以为这只是心灵鸡汤，但事实是：泰戈尔用"生如夏花之绚烂，死如秋叶之静美"这样的诗句，重新定义了东方哲学在世界文学中的地位。1922年，郑振铎用白话散文诗翻译它，打破文言主流，开创了中国白话诗歌翻译的先河。

这不是一本普通诗集，而是横跨百年的精神档案——325首短诗，每一首都是对生命本质的深刻洞察。叶芝说过："每天读一句泰戈尔的诗，可以让我忘却世间的一切痛苦。"

再看这个版本：巴掌本115×175mm，440克轻盈手感，通体天空蓝布面精装，三面纯蓝刷边。护封用ALL IN烫镭射银工艺，金银丝线随机组合——每本书的轨迹都不同，寓意飞鸟的飞行轨迹。28克和50克薄纸专色印刷，全新手绘四色插画，独家限量羽毛编码，一书一码。

郑振铎经典译本，文学史级别的收藏价值，加上这套精湛的装帧工艺——这是一本可以传世的诗歌宝库。放在书架是艺术品，翻开是精神避难所。"""
    },
    "3_九厘米的雾": {
        "name": "九厘米的雾风格",
        "text": """在地铁上刷短视频的人，永远不会懂"生如夏花"的真正含义。

泰戈尔的《飞鸟集》教的从来不只是优美句子——而是告诉你，如何在破碎的生活里重建意义的能力。他写飞鸟、写落叶、写星辰、写尘埃，万物皆可入诗，万物皆有所指。"世界以痛吻我，而我报之以歌"——这不是鸡汤，这是生存技术。

但诗集和诗集不一样。这本商务印书馆刷边版，440克的巴掌本，三面天空蓝刷边，护封表面镶嵌金银两色线——每本书的轨迹都不同，寓意鸟儿飞行的随机性。不是印刷品，是可以握在手里的精神雕塑。28克薄纸专色印刷，翻页时能感受到纸张的呼吸感。郑振铎1922年的译本，一百年后仍是中文世界的标尺。

羽毛编码限量发售，一本书一个编号。在这个算法统治注意力的时代，一本好诗集是你最后的精神领地。错过就是绝版。"""
    }
}

def clean_for_tts(text):
    """清理文本，移除括号内的语气提示"""
    cleaned = re.sub(r"[\(\[（【].*?[\)\]）】]", "", text)
    cleaned = cleaned.replace("\n", " ").strip()
    # 移除多余的空格
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

def tts_kitta(text, output_path):
    """调用Kitta AI TTS API"""
    clean_text = clean_for_tts(text)
    url = "https://kittaai.com/api/open/tts"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "reference_id": REFERENCE_ID,
        "text": clean_text,
        "version": "s1",
        "format": "wav",
        "cache": False
    }
    print(f"Text length: {len(clean_text)} chars")
    print("Calling Kitta AI TTS API...")

    resp = requests.post(url, json=payload, headers=headers, timeout=180)
    if resp.status_code == 200:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        size = os.path.getsize(output_path)
        print(f"Saved: {output_path} ({size/1024/1024:.1f} MB)")
        return True
    else:
        print(f"TTS failed: {resp.status_code} - {resp.text}")
        return False

if __name__ == "__main__":
    print("=== 飞鸟集 3条文案配音 ===")

    for key, script in SCRIPTS.items():
        print(f"\n{'='*50}")
        print(f"正在生成: {script['name']}")
        print(f"{'='*50}")

        # 生成文件名
        output_file = os.path.join(OUTPUT_DIR, f"飞鸟集-配音-{script['name']}.wav")

        success = tts_kitta(script['text'], output_file)

        if success:
            print(f"✅ {script['name']} 配音完成")
        else:
            print(f"❌ {script['name']} 配音失败")

        # 间隔3秒，避免API限流
        time.sleep(3)

    print("\n=== 全部完成 ===")
    print(f"输出目录: {OUTPUT_DIR}")