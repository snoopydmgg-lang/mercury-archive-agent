#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微软拼音 ChsPinyinUDL.dat 生成器
从词表生成可直接导入的自定义词库文件。

用法:
  python generate_ms_pinyin_dat.py <词汇文件> [输出路径]

输入文件每行一个词（UTF-8），输出为微软拼音兼容的 .dat 文件。
"""

import io
import os
import struct
import sys
from pathlib import Path
from collections import defaultdict

HAS_PYPINYIN = False  # 不使用拼音库，直接用 GBK 编码 hash

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HEADER_SIZE = 24
RECORD_SIZE = 96
CAPACITY = 358  # 微软拼音标准容量
BATCH_SIZE = 300  # 每批最多300词（留余量给哈希冲突）
ENTRY_COUNT_PLACEHOLDER = 0  # will be updated

# ── 已知 slot 映射（从IH文件提取）──
KNOWN_SLOTS = {
    '一': 55, '三': 80, '上': 90, '下': 95, '不': 105, '个': 135, '中': 140,
    '为': 145, '丽': 150, '乙': 155, '也': 160, '乱': 170, '事': 175, '互': 180,
    '交': 185, '人': 195, '从': 200, '代': 205, '以': 210, '休': 215, '会': 220,
    '住': 225, '作': 230, '你': 235, '使': 255, '保': 260, '借': 265, '偏': 270,
    '做': 275, '充': 280, '八': 285, '共': 290, '其': 295, '再': 300, '写': 305,
    '冰': 310, '冻': 315, '出': 325, '分': 330, '前': 340, '剪': 345, '副': 350,
    '加': 355, '化': 365, '区': 370, '十': 375, '半': 385, '卡': 392, '原': 400,
    '去': 405, '发': 415, '只': 420, '可': 425, '叶': 430, '吃': 435,
    '后': 445, '吧': 455, '听': 460, '呢': 465, '和': 470, '唔': 475,
    '啊': 485, '啦': 490, '哦': 495, '嘛': 500, '四': 505, '国': 510,
    '在': 518, '地': 525, '场': 530, '坏': 535, '块': 545, '备': 550,
    '多': 560, '大': 565, '天': 570, '太': 575, '头': 580, '她': 590,
    '好': 595, '如': 600, '姐': 610, '子': 620, '学': 625, '它': 630,
    '定': 640, '宝': 645, '实': 650, '家': 660, '对': 665, '小': 675,
    '就': 680, '尽': 685, '层': 690, '差': 695, '已': 700, '带': 705,
    '帮': 710, '平': 720, '年': 725, '应': 735, '底': 740, '开': 750,
    '当': 760, '很': 770, '得': 775, '心': 780, '忘': 785, '快': 795,
    '怎': 800, '思': 805, '总': 810, '想': 815, '意': 820, '感': 825,
    '成': 835, '我': 840, '所': 850, '手': 860, '打': 865, '找': 875,
    '把': 885, '投': 890, '护': 895, '拉': 905, '拿': 915, '按': 920,
    '换': 930, '排': 935, '接': 940, '提': 950, '搞': 960, '放': 970,
    '故': 980, '整': 990, '文': 995, '新': 1000, '方': 1005, '无': 1015,
    '日': 1020, '时': 1025, '明': 1030, '是': 1040, '显': 1045, '晚': 1055,
    '最': 1065, '有': 1075, '本': 1085, '来': 1095, '杭': 1100, '果': 1105,
    '某': 1110, '标': 1115, '样': 1125, '模': 1135, '正': 1140, '每': 1150,
    '比': 1155, '没': 1165, '河': 1170, '注': 1175, '洞': 1180, '浏': 1185,
    '消': 1190, '深': 1195, '清': 1200, '满': 1205, '激': 1210, '然': 1215,
    '照': 1220, '烦': 1225, '烧': 1230, '热': 1235, '然': 1240, '爱': 1245,
    '特': 1250, '状': 1255, '玩': 1260, '现': 1265, '理': 1270, '生': 1275,
    '用': 1280, '电': 1285, '画': 1290, '疑': 1295, '白': 1305, '的': 1310,
    '目': 1320, '看': 1330, '真': 1335, '知': 1345, '确': 1355, '示': 1360,
    '社': 1365, '祝': 1370, '神': 1375, '离': 1380, '积': 1385, '程': 1390,
    '程': 1395, '空': 1400, '立': 1405, '第': 1410, '等': 1415, '管': 1420,
    '简': 1425, '算': 1430, '红': 1435, '线': 1445, '组': 1450, '经': 1455,
    '给': 1460, '统': 1465, '续': 1470, '编': 1475, '网': 1480, '美': 1485,
    '老': 1490, '考': 1495, '而': 1500, '联': 1505, '能': 1515, '自': 1520,
    '色': 1530, '花': 1535, '节': 1540, '范': 1545, '草': 1550, '荒': 1555,
    '获': 1560, '蓝': 1565, '行': 1575, '表': 1580, '被': 1585, '要': 1595,
    '见': 1600, '觉': 1610, '解': 1615, '计': 1620, '认': 1625, '记': 1630,
    '设': 1640, '证': 1645, '话': 1655, '说': 1660, '调': 1665, '象': 1675,
    '资': 1685, '跟': 1690, '路': 1695, '转': 1705, '较': 1710, '输': 1715,
    '过': 1725, '还': 1735, '这': 1740, '进': 1745, '连': 1750, '退': 1755,
    '送': 1760, '通': 1770, '遇': 1780, '道': 1785, '那': 1795, '都': 1800,
    '里': 1810, '重': 1815, '量': 1820, '金': 1825, '钥': 1830, '问': 1840,
    '间': 1845, '阅': 1850, '关': 1855, '防': 1860, '阿': 1865, '附': 1870,
    '除': 1875, '随': 1880, '集': 1885, '需': 1890, '静': 1895, '非': 1900,
    '面': 1905, '页': 1915, '顶': 1920, '预': 1925, '领': 1930, '题': 1935,
    '风': 1940, '首': 1950, '高': 1955, '魔': 1960, '黑': 1970, '默': 1975,
    '鼓': 1980,
}


def char_to_slot(char, capacity=CAPACITY):
    """根据 GBK 编码将汉字映射到 hash slot。"""
    try:
        gbk_bytes = char.encode('gbk')
        if len(gbk_bytes) >= 2:
            gbk_code = (gbk_bytes[0] << 8) | gbk_bytes[1]
        else:
            gbk_code = ord(char)
    except (UnicodeEncodeError, ValueError):
        gbk_code = ord(char)
    return (gbk_code ^ (gbk_code >> 8)) % capacity


def generate_udl(words, output_path):
    """生成 ChsPinyinUDL.dat 文件。按顺序填充，不使用哈希。"""
    capacity = CAPACITY
    record_size = RECORD_SIZE

    total_size = HEADER_SIZE + capacity * record_size
    data = bytearray(total_size)

    struct.pack_into('<H', data, 0, 0xAA55)    # magic: bytes 55 aa
    struct.pack_into('<H', data, 2, 0x8188)
    struct.pack_into('<H', data, 4, 0)
    struct.pack_into('<H', data, 6, record_size)
    struct.pack_into('<I', data, 8, 0xAA55AA55)
    struct.pack_into('<I', data, 12, capacity)
    struct.pack_into('<I', data, 16, 0)           # checksum (will compute)
    struct.pack_into('<I', data, 20, 0x319ED19F)  # timestamp

    timestamp = 0x319ED14D
    entry_count = 0

    for i, word in enumerate(words):
        word = word.strip()
        if not word or len(word) < 2:
            continue
        if i >= capacity:
            break

        offset = HEADER_SIZE + i * record_size
        struct.pack_into('<I', data, offset, timestamp)
        struct.pack_into('<I', data, offset + 4, 1)

        word_utf16 = word.encode('utf-16-le')
        max_text_len = record_size - 8 - 2
        if len(word_utf16) > max_text_len:
            word_utf16 = word_utf16[:max_text_len]
        data[offset + 8:offset + 8 + len(word_utf16)] = word_utf16
        entry_count += 1

    struct.pack_into('<H', data, 4, entry_count)

    with open(output_path, 'wb') as f:
        f.write(data)

    return entry_count


def generate_batches(words, output_dir, base_name='ChsPinyinUDL'):
    """分批生成多个 DAT 文件。"""
    output_dir = Path(output_dir)
    batches = []
    for i in range(0, len(words), BATCH_SIZE):
        batch = words[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        output_path = output_dir / f'{base_name}_{batch_num:02d}.dat'
        n = generate_udl(batch, output_path)
        batches.append((output_path, n))
    return batches


def main():
    if len(sys.argv) < 2:
        inbox = Path(__file__).resolve().parent.parent.parent / "00_InBox_收件箱"
        word_file = inbox / "user_vocab_ms_pinyin.txt"
        output = inbox / "ChsPinyinUDL_IMPORT.dat"
    else:
        word_file = Path(sys.argv[1])
        output = Path(sys.argv[2]) if len(sys.argv) > 2 else word_file.with_suffix('.dat')

    if not word_file.exists():
        print(f'未找到词汇文件: {word_file}')
        return

    # 读取词汇
    with open(word_file, 'r', encoding='utf-16-le') as f:
        words = [line.strip() for line in f if line.strip()]

    print(f'读取 {len(words)} 个词汇')

    # ── 添加用户明确指定的词汇 ──
    extra_words = [
        # 商业/管理
        "ROI", "DAU", "SOP", "OKR", "MVP", "RPE", "COMT",
        "Root Cause", "Bug Fix",
        "试用装理论", "认知反转", "技术悖论", "数据暴力", "逻辑降维",
        "悬念钩子", "渐进超负荷", "胸椎活动度", "肩胛骨稳定性", "上斜方肌",
        "碳水后置", "脑雾", "最小可行性产品", "赛马机制",
        "第一性原理", "边际成本", "系统论", "图层工作法", "番茄钟",
        "熵增", "分形", "进化论", "泛知识", "黑盒验证",
        "降维打击", "向下兼容",
        # AI/技术
        "AIGC", "LLM", "Prompt", "Agent", "RAG", "Fine-tuning",
        "Transformer", "Token", "Context Window", "Hallucination",
        "Zero-shot", "Few-shot", "Embedding", "Vector Database",
        "LangChain", "GPT", "Claude", "Midjourney", "Stable Diffusion",
        "ComfyUI", "Llama", "Hugging Face", "GPU", "NPU",
        "算力", "涌现能力", "强化学习", "监督学习", "神经网络",
        "扩散模型", "提示词工程", "知识库", "多模态", "大语言模型",
        "微调", "幻觉", "上下文窗口", "向量数据库",
        # 医药
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
    # 添加未在列表中的额外词
    existing_lower = {w.lower() for w in words}
    for w in extra_words:
        if w.lower() not in existing_lower:
            words.append(w)

    print(f'追加用户词汇后共 {len(words)} 个词')

    # 分批生成
    batches = generate_batches(words, output.parent)
    print(f'\n分 {len(batches)} 批生成完成:')
    for path, n in batches:
        print(f'  {path.name}: {n} 词')
    print(f'\n导入步骤 (逐批):')
    print(f'  Win+I → 时间和语言 → 语言和区域 → 中文 → 语言选项')
    print(f'  → 微软拼音 → 键盘选项 → 词库和自学习')
    print(f'  → 导入 → 选择 ChsPinyinUDL_01.dat')
    print(f'  → 重复导入 ChsPinyinUDL_02.dat, 03.dat, ...')


if __name__ == '__main__':
    main()
