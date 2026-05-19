"""
摄影构图艺术 - 配音生成脚本
为三套文案生成配音
"""
import sys
import os
import re

# 添加路径
sys.path.insert(0, "E:/1.work/douyin/1.shuixing/06_Python Scripts/01_AI文案")

from copyworkflow.audio_generator import AudioGenerator

# 项目路径
PROJECT_DIR = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\摄影构图艺术"
AUDIO_DIR = os.path.join(PROJECT_DIR, "01_素材_试用装")
SCRIPT_FILE = os.path.join(PROJECT_DIR, "02_脚本_逻辑链", "0416-摄影构图艺术-三套文案.md")

# 确保音频目录存在
os.makedirs(AUDIO_DIR, exist_ok=True)

def extract_oral_text(content, section_name):
    """从 MD 文件中提取指定章节的口播文案"""
    # 找到章节开始位置
    section_start = content.find(f"## {section_name}")
    if section_start == -1:
        return None

    # 找到口播文案开始位置
    oral_start = content.find("## 口播文案", section_start)
    if oral_start == -1:
        return None

    # 找到口播文案结束位置（下一个 --- 或 ## ）
    oral_end = content.find("---", oral_start)
    if oral_end == -1:
        oral_end = content.find("## 画面脚本", oral_start)

    if oral_end == -1:
        return None

    # 提取文本
    oral_text = content[oral_start + len("## 口播文案"):oral_end].strip()

    # 清理文本：移除 Markdown 格式
    oral_text = re.sub(r'\*\*', '', oral_text)  # 移除加粗
    oral_text = re.sub(r'\【[^】]+】', '', oral_text)  # 移除语气提示
    oral_text = re.sub(r'\n+', '\n', oral_text)  # 合并多余换行

    return oral_text.strip()

def main():
    print("=" * 60)
    print("  摄影构图艺术 - 配音生成")
    print("=" * 60)
    print()

    # 读取文案文件
    print(f"[INFO] 读取文案文件: {SCRIPT_FILE}")
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 三套文案配置
    scripts = [
        {
            "name": "余上沅的奇妙屋",
            "section": "余上沅的奇妙屋",
            "output": "0416-摄影构图艺术-余上沅-配音.wav"
        },
        {
            "name": "九厘米的雾",
            "section": "九厘米的雾",
            "output": "0416-摄影构图艺术-九厘米-配音.wav"
        },
        {
            "name": "Ad Scout",
            "section": "Ad Scout",
            "output": "0416-摄影构图艺术-AdScout-配音.wav"
        }
    ]

    generator = AudioGenerator()
    success_count = 0

    for i, script in enumerate(scripts, 1):
        print(f"\n{'=' * 60}")
        print(f"[{i}/3] {script['name']}")
        print(f"{'=' * 60}")

        # 提取口播文案
        print(f"[STEP 1] 提取口播文案...")
        oral_text = extract_oral_text(content, script['section'])

        if not oral_text:
            print(f"[ERROR] 无法提取口播文案")
            continue

        print(f"[INFO] 文案长度: {len(oral_text)} 字符")
        print(f"[INFO] 预览: {oral_text[:100]}...")

        # 生成配音
        print(f"\n[STEP 2] 生成配音...")
        output_path = os.path.join(AUDIO_DIR, script['output'])

        result = generator.generate_audio(oral_text, output_path)

        if result:
            print(f"[SUCCESS] 配音已保存: {output_path}")
            success_count += 1
        else:
            print(f"[ERROR] 配音生成失败")

    print(f"\n{'=' * 60}")
    print(f"完成: {success_count}/3 成功")
    print(f"{'=' * 60}")
    print(f"\n配音文件保存在: {AUDIO_DIR}")

if __name__ == "__main__":
    main()
