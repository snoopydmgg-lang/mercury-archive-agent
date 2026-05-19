#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从项目文件中提取用户高频领域词汇，生成微软拼音可导入的自定义词库。
输出: 00_InBox_收件箱/user_vocab_ms_pinyin.txt (UTF-16LE, 微软拼音导入格式)
"""

import io
import os
import re
import sys
from pathlib import Path
from collections import Counter

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INBOX = PROJECT_ROOT / "00_InBox_收件箱"

# 扫描目标: 文案、脚本、Wiki、CLAUDE.md
SCAN_DIRS = [
    PROJECT_ROOT / "Wiki知识库",
    PROJECT_ROOT / "06_Python Scripts",
    PROJECT_ROOT,
]

SKIP_PATTERNS = [
    r'\.db$', r'\.mp[34]$', r'\.wav$', r'\.png$', r'\.jpg$', r'\.gif$',
    r'\.zip$', r'\.json$', r'\.log$', r'\.pyc$', r'__pycache__', r'node_modules',
    r'\.git', r'\.obsidian', r'graphify', r'\.html$', r'\.css$', r'\.js$',
    r'BGM音乐库', r'venv', r'raw/', r'assets/', r'\.exe$', r'\.pdf$',
    r'token_metrics\.db', r'\.svg$', r'\.ttf$', r'\.woff',
]


def should_skip(path_str):
    for pat in SKIP_PATTERNS:
        if re.search(pat, path_str):
            return True
    return False


def extract_chinese_phrases(text, min_len=2, max_len=8):
    """从文本中提取中文短语 (2-8字)。"""
    # 只保留中文字符
    cleaned = re.sub(r'[^一-鿿]', '', text)
    phrases = []
    for length in range(min_len, min(max_len + 1, len(cleaned) + 1)):
        for i in range(len(cleaned) - length + 1):
            chunk = cleaned[i:i + length]
            # 过滤纯数字/标点残留
            if re.match(r'^[一-鿿]+$', chunk):
                phrases.append(chunk)
    return phrases


def is_common_word(word):
    """过滤过于通用的词 (停用词表 + 碎片检测)。"""
    common = {
        '我们', '他们', '你们', '自己', '什么', '怎么', '为什么', '可以',
        '这个', '那个', '一个', '不是', '就是', '还是', '因为', '所以',
        '但是', '如果', '虽然', '不过', '而且', '然后', '已经', '没有',
        '知道', '觉得', '应该', '需要', '可能', '一定', '一些', '全部',
        '东西', '事情', '时候', '问题', '地方', '方法', '这里', '那里',
        '现在', '今天', '明天', '昨天', '以后', '以前', '看到', '听到',
        '一下', '一种', '很多', '非常', '比较', '太棒了', '大家好',
        '我也是', '也不能', '是否', '如何', '进行', '通过', '使用',
        '包括', '关于', '相关', '所有', '其他', '以上', '以后',
        '例如', '主要', '不同', '基本', '一般', '已经', '这些',
        '这是', '作为', '方面', '对于', '为了', '其中', '以及',
    }
    if word in common:
        return True
    # 过滤助词/代词开头的碎片
    if word[0] in '的了是我这在有他你一不就和人也来要到们以可上下前' and len(word) <= 3:
        return True
    # 过滤疑问词碎片
    if word in ('为什', '为什不', '么是', '么样', '么做', '样才', '样能'):
        return True
    # 纯数字
    if re.match(r'^\d+$', word):
        return True
    return False


def collect_files():
    """收集所有需要扫描的文本文件。"""
    files = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for root, dirs, filenames in os.walk(scan_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]
            for fn in filenames:
                fp = os.path.join(root, fn)
                if should_skip(fp):
                    continue
                # 只读文本类文件
                ext = os.path.splitext(fn)[1].lower()
                if ext in ('.md', '.py', '.txt', '.csv', '.json', '.ini', '.yml', '.yaml',
                           '.bat', '.ps1', '.xml', '.html', '.js', '.ts', ''):
                    files.append(fp)
    return files


def main():
    print("扫描项目文件中...")
    files = collect_files()
    print(f"  找到 {len(files)} 个文本文件")

    all_phrases = []
    processed = 0
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except Exception:
            continue
        all_phrases.extend(extract_chinese_phrases(text))
        processed += 1

    print(f"  处理 {processed} 个文件, 提取 {len(all_phrases)} 个短语片段")

    # 频率统计
    counter = Counter(all_phrases)

    # 过滤: 至少出现3次, 2-6字, 非常见词
    vocab = []
    for phrase, count in counter.most_common(20000):
        if count < 3:
            continue
        if len(phrase) < 2 or len(phrase) > 6:
            continue
        if is_common_word(phrase):
            continue
        vocab.append((phrase, count))

    print(f"  过滤后: {len(vocab)} 个领域词汇\n")

    # 按频率排序，取前2000个
    top_vocab = vocab[:2000]

    # 显示 top 50
    print("Top 50 高频领域词:")
    for i, (phrase, count) in enumerate(top_vocab[:50], 1):
        print(f"  {i:3d}. {phrase} ({count})")

    # ── Claude 常用词补充 ──
    claude_vocab = [
        # 技术栈
        "飞书", "豆包", "多维表格", "云文档", "知识库", "令牌",
        "接口", "回调", "轮询", "熔断", "灰度", "回滚", "压测",
        "大模型", "推理", "微调", "嵌入", "向量", "语义搜索",
        "工作流", "管道", "触发器", "钩子", "看板", "仪表盘",
        "文案生成", "配音", "封面", "选品", "对标", "复盘",
        # 产品名
        "版式之道", "摄影构图", "我等你", "名画里", "星空帝国",
        "水星艺术馆", "余上沅", "九厘米", "飞鸟集",
        # 工具名
        "收件箱", "冷备份", "全局库", "制作中",
        # Claude Code 常用
        "校验", "合规", "幂等", "回填", "降级", "兜底",
        "侧边栏", "终端", "控制台", "调试", "断点",
        "计数器", "缓存", "命中率", "预测", "偏差",
        "口径", "估算", "校准", "因子", "加权",
        "会话", "令牌数", "上下文", "提示词",
        # 商业/运营
        "变现", "转化率", "完播率", "粉丝", "权重",
        "算法推荐", "流量池", "自然流量", "付费流量",
        "挂车", "小黄车", "商品卡", "抖店",
        "短视频", "中视频", "长视频", "图文",
        "选品", "排品", "测品", "爆款", "平销",
        "千川", "随心推", "投放", "素材",
        "直播间", "话术", "憋单", "逼单",
        # 工作习惯
        "复盘", "迭代", "闭环", "复盘", "校准",
        "像素级", "图层工作法", "死命令",
        "站立规则", "收件箱清理",
    ]
    # 去重+保持顺序
    existing = {p for p, _ in top_vocab}
    claude_vocab = [w for w in claude_vocab if w not in existing]

    # 输出为微软拼音导入文件 (UTF-16LE)
    output_path = INBOX / "user_vocab_ms_pinyin.txt"
    with open(output_path, 'w', encoding='utf-16-le') as f:
        f.write('﻿')  # BOM
        for phrase, _ in top_vocab:
            f.write(phrase + '\n')
        for phrase in claude_vocab:
            f.write(phrase + '\n')

    print(f"\n已生成: {output_path}")
    print(f"  项目提取: {len(top_vocab)} 词")
    print(f"  Claude补充: {len(claude_vocab)} 词 (技术/工具/运营)")
    print(f"  合计: {len(top_vocab) + len(claude_vocab)} 词")
    print("\n导入方法:")
    print("  Win+I → 时间和语言 → 语言和区域 → 中文(...) → 语言选项")
    print("  → 微软拼音 → 键盘选项 → 词库和自学习 → 导入 → 选择该文件")


if __name__ == '__main__':
    main()
