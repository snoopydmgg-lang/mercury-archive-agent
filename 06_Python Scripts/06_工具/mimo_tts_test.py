"""MIMO TTS 测试脚本"""
import os
import sys
import base64
import time

# 依赖检查
try:
    from openai import OpenAI
except ImportError:
    print("需要安装 openai: pip install openai")
    sys.exit(1)

MIMO_API_KEY = "tp-cjg92m460j2ax59af6fk3y883baxtfadxsm7xgxq2bucunqn"
# Token Plan 专用端点（中国集群）
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

client = OpenAI(api_key=MIMO_API_KEY, base_url=BASE_URL)


def test_preset_voice():
    """测试预置音色"""
    print("=== 测试1: 预置音色（冰糖）===")
    start = time.time()

    completion = client.chat.completions.create(
        model="mimo-v2.5-tts",
        messages=[
            {
                "role": "user",
                "content": "温柔治愈的语气，像深夜电台主持人，语速稍慢，声音温暖有磁性"
            },
            {
                "role": "assistant",
                "content": "夜深了，你辛苦了。今天也好好努力了呢。不管发生了什么，都请好好休息，明天又是新的一天。"
            }
        ],
        audio={"format": "wav", "voice": "冰糖"}
    )

    audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    out_path = os.path.join(OUTPUT_DIR, "mimo_test_preset_冰糖.wav")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    elapsed = time.time() - start
    print(f"  音色: 冰糖")
    print(f"  文件: {out_path}")
    print(f"  大小: {len(audio_bytes) / 1024:.1f} KB")
    print(f"  耗时: {elapsed:.1f}s")
    return out_path


def test_style_tag():
    """测试风格标签"""
    print("\n=== 测试2: 风格标签（磁性+低沉）===")
    start = time.time()

    completion = client.chat.completions.create(
        model="mimo-v2.5-tts",
        messages=[
            {"role": "user", "content": ""},
            {
                "role": "assistant",
                "content": "(磁性 深沉)夜已经深了，城市还在呼吸。我是今晚陪你的人，欢迎收听午夜电台。"
            }
        ],
        audio={"format": "wav", "voice": "白桦"}
    )

    audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    out_path = os.path.join(OUTPUT_DIR, "mimo_test_style_tag.wav")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    elapsed = time.time() - start
    print(f"  音色: 白桦")
    print(f"  文件: {out_path}")
    print(f"  大小: {len(audio_bytes) / 1024:.1f} KB")
    print(f"  耗时: {elapsed:.1f}s")
    return out_path


def test_voice_design():
    """测试音色设计"""
    print("\n=== 测试3: 音色设计（自定义音色）===")
    start = time.time()

    completion = client.chat.completions.create(
        model="mimo-v2.5-tts-voicedesign",
        messages=[
            {
                "role": "user",
                "content": "一位年迈的老先生，说带北方口音的普通话，语速缓慢而沉稳，嗓音略带沙哑和沧桑感，仿佛一位饱经风霜的老爷爷在讲故事，充满岁月的智慧。"
            },
            {
                "role": "assistant",
                "content": "我这辈子啊，走南闯北六十多年。见过最热闹的集市，也见过最安静的戈壁。到头来才明白一个道理——这人哪，不在走了多远的路，在于记住了多少风景。"
            }
        ],
        audio={"format": "wav"}
    )

    audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    out_path = os.path.join(OUTPUT_DIR, "mimo_test_voice_design.wav")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    elapsed = time.time() - start
    print(f"  音色: 自定义（北方老先生）")
    print(f"  文件: {out_path}")
    print(f"  大小: {len(audio_bytes) / 1024:.1f} KB")
    print(f"  耗时: {elapsed:.1f}s")
    return out_path


def test_director_mode():
    """测试导演模式"""
    print("\n=== 测试4: 导演模式 ===")
    start = time.time()

    director_prompt = """角色：百年门阀岑家的现任大当家。自出生便被过继给祖庙的守门老人抚养，被塑造成一尊完美无瑕、绝情断欲的家族图腾。常年深居简出，对人有着极强的阶级疏离感。

场景：在祠堂的阴影里，看着那个不顾一切冲破保安防线来找她、企图带她私奔的男人。她要用最冷硬的阶级壁垒，绞杀对方，也绞杀自己刚刚萌芽、却足以燎原的感情。

指导：
冰冷、慵懒却极具威压的低音御姐。发声通道非常松弛，没有任何剑拔弩张，却有着让人骨里生寒的压迫感。
语速与顿挫：极慢，每个字都像是在舌尖滚过才吐出来，带着上位者漫不经心的傲慢。"""

    completion = client.chat.completions.create(
        model="mimo-v2.5-tts",
        messages=[
            {"role": "user", "content": director_prompt},
            {
                "role": "assistant",
                "content": "你以为凭你的身份，就能冲撞我的世界？醒醒吧。我们之间隔着的，不只是这几道门，是你永远也跨不过的天堑。"
            }
        ],
        audio={"format": "wav", "voice": "茉莉"}
    )

    audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
    out_path = os.path.join(OUTPUT_DIR, "mimo_test_director_mode.wav")
    with open(out_path, "wb") as f:
        f.write(audio_bytes)

    elapsed = time.time() - start
    print(f"  音色: 茉莉")
    print(f"  文件: {out_path}")
    print(f"  大小: {len(audio_bytes) / 1024:.1f} KB")
    print(f"  耗时: {elapsed:.1f}s")
    return out_path


if __name__ == "__main__":
    print("MIMO TTS 功能测试")
    print("=" * 50)

    results = []
    for test_fn in [test_preset_voice, test_style_tag, test_voice_design, test_director_mode]:
        try:
            path = test_fn()
            results.append((test_fn.__doc__, "OK", path))
        except Exception as e:
            print(f"  错误: {e}")
            results.append((test_fn.__doc__, f"FAIL: {e}", None))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for desc, status, path in results:
        print(f"  {desc.strip()}: {status}")
