#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
构建带拼音的词汇中间格式文件。
输入: user_vocab_ms_pinyin.txt (UTF-16LE, 一行一词)
输出: vocab_with_pinyin.csv (UTF-8, word/pinyin/freq/source)
"""

import io
import os
import re
import sys
import csv
from pathlib import Path
from collections import Counter

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INBOX = Path(__file__).resolve().parent.parent.parent / "00_InBox_收件箱"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

OUTPUT_PATH = INBOX / "vocab_with_pinyin.csv"

# ── 用户手动补充词汇 (来自聊天中确认的常用词) ──
USER_MANUAL_WORDS = [
    "ROI", "DAU", "SOP", "OKR", "MVP", "RPE", "COMT",
    "Root Cause", "Bug Fix",
    "试用装理论", "认知反转", "技术悖论", "数据暴力", "逻辑降维",
    "悬念钩子", "渐进超负荷", "胸椎活动度", "肩胛骨稳定性", "上斜方肌",
    "碳水后置", "脑雾", "最小可行性产品", "赛马机制",
    "第一性原理", "边际成本", "系统论", "图层工作法", "番茄钟",
    "熵增", "分形", "进化论", "泛知识", "黑盒验证",
    "降维打击", "向下兼容",
    "AIGC", "LLM", "Prompt", "Agent", "RAG", "Fine-tuning",
    "Transformer", "Token", "Context Window", "Hallucination",
    "Zero-shot", "Few-shot", "Embedding", "Vector Database",
    "LangChain", "GPT", "Claude", "Midjourney", "Stable Diffusion",
    "ComfyUI", "Llama", "Hugging Face", "GPU", "NPU",
    "算力", "涌现能力", "强化学习", "监督学习", "神经网络",
    "扩散模型", "提示词工程", "知识库", "多模态", "大语言模型",
    "微调", "幻觉", "上下文窗口", "向量数据库",
    "适应症", "禁忌症", "不良反应", "药代动力学", "用药依从性",
    "循证医学", "临床试验", "真实世界研究",
    "核心客户", "关键意见领袖", "学术会议", "科室会", "院内会",
    "卫星会", "病例分享", "专家共识", "诊疗指南",
    "医保支付", "带量采购", "国家医保目录",
    "竞品分析", "市场份额", "商业渠道", "纯销数据", "发货流向",
    "药事委员会", "伦理委员会", "处方习惯", "长效制剂",
    "靶向治疗", "联合用药", "一线治疗", "二线治疗",
    "耐药性", "患者随访", "经理协访", "拜访计划",
    "客情维护", "进院提单", "学术推广",
    "赖酱",
]


def load_project_vocab(path):
    """读取 user_vocab_ms_pinyin.txt (UTF-16LE), 返回词条列表。"""
    words = []
    with open(path, 'r', encoding='utf-16-le') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('﻿'):
                words.append(line)
    return words


def compute_word_frequencies(words, project_root, sample_files=200):
    """在项目文件中统计词频 (采样模式加速)。"""
    # 收集文本文件
    text_files = []
    for root, dirs, filenames in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                   ('node_modules', 'venv', '__pycache__', 'raw', 'assets', 'BGM音乐库')]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in ('.md', '.py', '.txt', '.csv', '.json', '.ini', '.yml', '.yaml', '.bat', ''):
                text_files.append(os.path.join(root, fn))
                if len(text_files) >= sample_files:
                    break
        if len(text_files) >= sample_files:
            break

    # 采样统计
    counter = Counter()
    for fp in text_files:
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except:
            continue
        for word in words:
            if word in content:
                counter[word] += content.count(word)

    return counter


def has_chinese(text):
    return any('一' <= c <= '鿿' for c in text)


def generate_pinyin_safe(text):
    """为中文词生成拼音，英文词保留原文。"""
    if not has_chinese(text):
        return text  # 英文/数字原样

    try:
        from pypinyin import lazy_pinyin, Style
        py_list = lazy_pinyin(text, style=Style.TONE)
        return ' '.join(py_list)
    except ImportError:
        return ''


def batch_generate_pinyin(words):
    """批量生成拼音 (pypinyin 每字只查一次)。"""
    from pypinyin import pinyin as py_func, Style

    if not words:
        return {}

    # 分离中英文
    cn_words = [(i, w) for i, w in enumerate(words) if has_chinese(w)]

    if not cn_words:
        return {}

    print(f'  批量生成拼音: {len(cn_words)} 个中文词...')

    # 收集所有唯一汉字
    all_chars = set()
    for _, w in cn_words:
        all_chars.update(c for c in w if '一' <= c <= '鿿')

    unique_chars = list(all_chars)
    print(f'  唯一汉字: {len(unique_chars)} 个')

    # 批量查拼音 (pypinyin v2 API)
    try:
        char_pinyin = py_func(unique_chars, style=Style.TONE)
    except TypeError:
        # 旧版 API
        char_pinyin = [py_func([c], style=Style.TONE)[0] for c in unique_chars]

    char_map = {}
    for char, py_list in zip(unique_chars, char_pinyin):
        char_map[char] = py_list[0] if py_list else char

    # 组装每个词的拼音
    result = {}
    for i, w in cn_words:
        pinyin_parts = [char_map.get(c, c) for c in w if '一' <= c <= '鿿']
        result[i] = ' '.join(pinyin_parts)

    return result


def main():
    vocab_path = INBOX / "user_vocab_ms_pinyin.txt"

    if not vocab_path.exists():
        print(f'词汇文件不存在: {vocab_path}')
        print('请先运行 extract_user_vocab.py 生成')
        return

    # 1. 加载项目词汇
    print('1. 加载词汇...')
    words = load_project_vocab(vocab_path)
    print(f'   项目提取: {len(words)} 词')

    # 2. 追加用户手动词汇 (去重)
    existing = set(words)
    added = [w for w in USER_MANUAL_WORDS if w not in existing]
    words.extend(added)
    print(f'   用户补充: {len(added)} 词 (新增)')
    print(f'   合计: {len(words)} 词')

    # 3. 统计频率
    print('2. 统计词频 (采样)...')
    freq = compute_word_frequencies(words, PROJECT_ROOT, sample_files=200)
    print(f'   采样统计完成, {len(freq)} 词有频率数据')

    # 4. 生成拼音
    print('3. 生成拼音...')
    pinyin_map = batch_generate_pinyin(words)

    # 5. 输出 CSV
    print(f'4. 输出 CSV → {OUTPUT_PATH}')
    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'pinyin', 'frequency', 'source', 'has_chinese'])
        for i, word in enumerate(words):
            py = pinyin_map.get(i, word)  # word itself for English
            fr = freq.get(word, 0)
            # 判断来源
            if word in added:
                src = 'manual'
            else:
                src = 'project'
            writer.writerow([word, py, fr, src, 'Y' if has_chinese(word) else 'N'])

    print(f'   完成! {len(words)} 行')
    print(f'   文件: {OUTPUT_PATH}')

    # 6. 统计摘要
    cn_count = sum(1 for w in words if has_chinese(w))
    en_count = len(words) - cn_count
    has_py = sum(1 for i in pinyin_map)
    print(f'\n摘要:')
    print(f'  中文词: {cn_count} (有拼音: {has_py})')
    print(f'  英文/混合: {en_count}')
    print(f'  高频 Top 10:')
    for word, fr in sorted(freq.items(), key=lambda x: -x[1])[:10]:
        print(f'    {word}: {fr}')


if __name__ == '__main__':
    main()
