"""
为宫崎骏文案生成配音并上传飞书
"""
import sys
import os
import json
import time

# 添加路径
sys.path.insert(0, "E:/1.work/douyin/1.shuixing/06_Python Scripts/01_AI文案")

from copyworkflow.audio_generator import AudioGenerator
from copyworkflow.feishu_client import FeishuClient

def generate_audio_for_script(json_path, output_dir):
    """为单个文案生成配音"""
    # 读取JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    oral_text = script_data.get('oral_text', '')
    if not oral_text:
        print(f"[ERROR] {json_path} 没有口播文案")
        return None

    # 清理语气提示
    import re
    clean_text = re.sub(r'【[^】]+】', '', oral_text)
    clean_text = re.sub(r'\n+', '\n', clean_text).strip()

    # 生成配音文件名
    filename = os.path.basename(json_path).replace('.json', '-配音.wav')
    output_path = os.path.join(output_dir, filename)

    # 生成配音
    generator = AudioGenerator()
    result = generator.generate_audio(clean_text, output_path)

    return result

def upload_to_feishu(json_path, audio_path, record_id):
    """上传文案和配音到飞书"""
    # 读取JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    client = FeishuClient()

    # 上传发布信息（标题、简介、商品短标题）
    publish_info = {
        'publish_title': script_data.get('publish_title', ''),
        'publish_intro': script_data.get('publish_intro', ''),
        'product_short_title': script_data.get('product_short_title', '')
    }

    print(f"\n[INFO] 上传发布信息到飞书...")
    print(f"  - 标题: {publish_info['publish_title'][:50]}...")
    print(f"  - 简介: {publish_info['publish_intro'][:50]}...")
    print(f"  - 商品短标题: {publish_info['product_short_title']}")

    success1 = client.update_publish_info(record_id, publish_info)

    # 上传文案数据（口播、分镜、BGM、音效）
    script_info = {
        'oral_text': script_data.get('oral_text', ''),
        'visual_script': script_data.get('visual_script', []),
        'bgm_suggestion': script_data.get('bgm_suggestion', ''),
        'sfx_suggestion': script_data.get('sfx_suggestion', ''),
        'audio_url': audio_path if audio_path else ''
    }

    print(f"\n[INFO] 上传文案数据到飞书...")
    success2 = client.update_script(record_id, script_info)

    if success1 and success2:
        print(f"[SUCCESS] 文案已成功上传到飞书")
        return True
    else:
        print(f"[ERROR] 上传飞书失败")
        return False

def main():
    # 文案文件路径
    script_dir = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/宫崎骏作品集/02_脚本_逻辑链"
    audio_dir = "E:/1.work/douyin/1.shuixing/01_Projects_制作中/宫崎骏作品集/01_素材_试用装"

    # 今天生成的两条文案
    scripts = [
        {
            'json': os.path.join(script_dir, '0413-235248-1.json'),
            'name': '大师画像型',
            'record_id': None  # 需要用户提供飞书记录ID
        },
        {
            'json': os.path.join(script_dir, '0413-235433-2.json'),
            'name': '故事叙事型',
            'record_id': None  # 需要用户提供飞书记录ID
        }
    ]

    print("=" * 60)
    print("宫崎骏文案配音生成与飞书上传")
    print("=" * 60)

    for i, script in enumerate(scripts, 1):
        print(f"\n处理第 {i} 条文案：{script['name']}")
        print(f"文件：{os.path.basename(script['json'])}")

        # 生成配音
        print(f"\n[STEP 1] 生成配音...")
        audio_path = generate_audio_for_script(script['json'], audio_dir)

        if audio_path:
            print(f"[SUCCESS] 配音已保存：{audio_path}")
        else:
            print(f"[ERROR] 配音生成失败")
            continue

        # 询问是否上传飞书
        print(f"\n[STEP 2] 上传到飞书")
        print("提示：需要提供飞书记录ID才能上传")
        print("如果暂时不上传，可以跳过此步骤")

        time.sleep(1)

    print("\n" + "=" * 60)
    print("全部完成！")
    print("=" * 60)
    print(f"\n生成的文件：")
    print(f"  - 文案1: {scripts[0]['json']}")
    print(f"  - 文案2: {scripts[1]['json']}")
    print(f"  - 配音保存在: {audio_dir}")
    print(f"\n如需上传飞书，请提供记录ID后手动调用 upload_to_feishu() 函数")

if __name__ == "__main__":
    main()
