"""
版式之道 - 三套文案配音生成（修复版）
修复问题：删除所有逾期注释和调试信息
"""
import requests
import re
import os
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Kitta AI API配置
API_TOKEN = "93a023b1b6baae2e6b5876705d666ffe4deee67a343fb3cf55a354ef9b24d2c6"
REFERENCE_ID = "bc9fced8-266a-47fd-b86f-0eb0c9b71d68"
url = "https://kittaai.com/api/open/tts"

# 输出目录
output_dir = r'E:\1.work\douyin\1.shuixing\01_Projects_制作中\版式之道\03_配音_音频'
os.makedirs(output_dir, exist_ok=True)

# 三套文案（DBS优化版）
scripts = {
    "风格1-余上沅": """一张海报，留白占了九成——你觉得没设计完，大师说这是最难的部分。

18位日本设计大师，古平正义、平野甲贺、服部一成……把版式逻辑拆成了77种可复用的策略，锁进这本《版式之道》。

留白空间感——日本设计师的留白比例高达60%到70%，那些"空"的地方，恰恰是按秒计费的。

网格系统——不是创意决定你的报价，是网格系统。6大创意风格，77种版式策略，每一种都是可以复刻的方法论。

CRAP原则——对比、重复、对齐、亲密性，四把钥匙，打开视觉层级的秘密。

212页，70余个经典设计案例，留白哲学、几何交错感、复古意向感、秩序明镜感。

平面设计最大的谎言是：越满越用心。

这本书告诉你的是——版式，从来都是方法论，不是灵感集。

《版式之道》，善本图书出品，18位大师亲自指导。""",

    "风格2-九厘米": """平面设计最大的谎言：越满越用心。

日本设计师的留白比例，往往高达六七成。你以为没设计完，他们说——这是报价最高的部分。

留白是按秒计费的。网格系统决定设计报价，从来不是创意。

《版式之道》，18位日本设计大师亲自指导，6大创意风格，77种版式策略，70余个经典案例，212页精印内容。

留白空间感、高级反差感、几何交错感、手绘活泼感、复古意向感、秩序明镜感——六种风格，每一种都是一套完整的设计语言。

古平正义、平野甲贺、服部一成……18位大师，把网格系统、视觉层级、版心率、CRAP原则，拆成带坐标的解剖报告，放进这212页里。

野路子和科班平面设计师的差距，从来不在技术、设备，在于有没有掌握版式之道。

善本图书出品，豆瓣高分收录。

你的下一张作品，值得一套真正的方法论。""",

    "风格3-AdScout": """为什么你做的海报总像路边摊上的牛皮癣？

字塞满了、颜色堆满了、元素全上了——客户还是说"不够专业"。

平面设计最大的谎言，就是越满越用心。

日本顶级设计师留白比例高达六七成，报价比堆满的高三倍。

版式，从来不是为了好看——是为了定价。

《版式之道》，18位日本设计大师亲自指导，6大创意风格，77种版式策略，70余个经典案例，212页精印。

留白空间感、高级反差感、几何交错感——每一种风格背后都有可复用的底层逻辑。

网格系统、视觉层级、CRAP原则，这些才是科班设计师和野路子之间真正的墙。

留白是按秒计费的。

网格系统决定设计报价，不是创意。

善本图书出品，豆瓣高分收录。

你缺的不是软件技巧，是版式之道。"""
}

def clean_text_for_tts(text):
    """清理文本，移除所有不适合TTS的内容"""
    # 移除所有注释标记
    text = re.sub(r'#.*', '', text)
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # 移除markdown标记
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'__', '', text)
    text = re.sub(r'~~', '', text)

    # 移除特殊符号（保留基本标点）
    text = re.sub(r'[【】『』「」《》〈〉]', '', text)

    # 统一标点
    text = text.replace('——', '，')
    text = text.replace('…', '。')

    # 移除多余空白
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()

    return text

def tts_kitta(text, output_path):
    """调用Kitta AI生成配音"""
    # 清理文本
    clean_text = clean_text_for_tts(text)

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "reference_id": REFERENCE_ID,
        "text": clean_text,
        "version": "s1",
        "format": "wav"
    }

    print(f'正在生成配音...')
    response = requests.post(url, headers=headers, json=payload, timeout=180)

    if response.status_code == 200:
        try:
            result = response.json()
            audio_url = result.get('audio_url') or result.get('url')
            if audio_url:
                audio_resp = requests.get(audio_url, timeout=60)
                if audio_resp.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(audio_resp.content)
                    print(f'✅ 已保存: {output_path}')
                    return True
        except:
            pass

        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f'✅ 已保存: {output_path}')
        return True
    else:
        print(f'❌ API返回错误 {response.status_code}')
        return False

def main():
    timestamp = datetime.now().strftime("%Y%m%d")

    print("=" * 60)
    print("版式之道 - 三套文案配音生成")
    print("=" * 60)

    for style_name, text in scripts.items():
        print(f"\n生成 {style_name}...")
        output_path = os.path.join(output_dir, f'{timestamp}-版式之道-配音-{style_name}.wav')

        result = tts_kitta(text, output_path)

        if result:
            size = os.path.getsize(output_path)
            print(f'文件大小: {size/1024/1024:.1f} MB')

        print("-" * 60)

    print("\n✅ 全部完成！")

if __name__ == "__main__":
    main()
