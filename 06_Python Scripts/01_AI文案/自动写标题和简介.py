# -*- coding: utf-8 -*-
"""
抖音发布文案生成器（整合75个爆款公式 + 12类心理触发器）
输入话题，输出：视频标题(20字) + 简介(50-100字) + 商品短标题(≤10字)

用法：
  python 自动写标题和简介.py [话题] [风格类型]

示例：
  python 自动写标题和简介.py "宫崎骏作品集" "大师画像型"
  python 自动写标题和简介.py "飞鸟集" "故事叙事型"
"""
import requests
import json
import time
import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ================= 配置区 =================
DEEPSEEK_API_KEY = "sk-cb35b9eb2b15405aae2f5061efa9cb03"
FEISHU_APP_ID = "cli_a90dbd544bb8dcb2"
FEISHU_APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
FEISHU_BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"
FEISHU_TABLE_ID = "tblSBx7rHX0siCnD"

# ================= 75个爆款公式库 =================
# 12类心理触发器：认知冲突/好奇缺口/恐惧损失/身份代入/数字锚点/
#                  结果承诺/社会证明/争议挑衅/场景条件/行动号召/权威借力/互动测试

TITLE_FORMULAS = {
    "认知冲突": [
        {"formula": "99%的人都不知道的XX", "example": "99%的人都不知道的上海小众书店", "reason": "打破认知，建立信息差"},
        {"formula": "XX？错！恰恰相反", "example": "努力赚钱？错！恰恰相反", "reason": "反转认知，引发好奇"},
        {"formula": "被骂了30年，终于有人说实话了", "example": "被骂了30年的国货，终于有人说实话了", "reason": "挑战权威，制造悬念"},
        {"formula": "谁说XX不能YY", "example": "谁说绘本不能有深度", "reason": "打破偏见，对立冲突"},
        {"formula": "XX的真相是——", "example": "宫崎骏七次退休的真相是——", "reason": "揭秘真相，激发点击"},
    ],
    "好奇缺口": [
        {"formula": "XX的秘密藏在这里", "example": "宫崎骏骗局的秘密藏在这里", "reason": "暗示内幕，引发窥探"},
        {"formula": "直到今天才有人说清楚", "example": "直到今天才有人说清楚敦煌配色", "reason": "信息稀缺感"},
        {"formula": "曝光XX不为人知的一面", "example": "曝光宫崎骏不为人知的一面", "reason": "揭秘心理"},
        {"formula": "原来XX是这个意思", "example": "原来《风起了》是这个意思", "reason": "认知翻转"},
        {"formula": "大多数人都理解错了", "example": "大多数人都理解错了宫崎骏的温柔", "reason": "纠正心理"},
    ],
    "恐惧损失": [
        {"formula": "错过XX，你会损失什么", "example": "错过这本绘本，你会损失什么", "reason": "制造损失焦虑"},
        {"formula": "XX正在消失/绝版", "example": "吉卜力原版绘本正在绝版", "reason": "稀缺性焦虑"},
        {"formula": "看完这篇你就知道有多后悔", "example": "看完这篇你就知道有多后悔没买", "reason": "后悔驱动"},
        {"formula": "XX以后不会再有了", "example": "宫崎骏以后不会再有了", "reason": "稀缺承诺"},
        {"formula": "错过一次，遗憾一生", "example": "错过一次，遗憾一生的艺术启蒙", "reason": "永久损失恐惧"},
    ],
    "身份代入": [
        {"formula": "XX的人都在悄悄做这件事", "example": "有品味的人都在悄悄做这件事", "reason": "身份归属"},
        {"formula": "我是XX，但我不是普通人", "example": "我是普通人，但我不是普通人", "reason": "身份反差"},
        {"formula": "如果你也是XX，请举手", "example": "如果你也爱宫崎骏，请举手", "reason": "圈层认同"},
        {"formula": "XX的人才能看懂", "example": "只有爱过宫崎骏的人才能看懂", "reason": "专属感"},
        {"formula": "真正的XX都明白这个道理", "example": "真正的艺术爱好者都明白这个道理", "reason": "权威归属"},
    ],
    "数字锚点": [
        {"formula": "XX个XX，一次讲清楚", "example": "7次退休7次复出，一次讲清楚", "reason": "量化承诺"},
        {"formula": "XX天刷完XX遍，我发现了XX", "example": "1000天刷完宫崎骏10遍，我发现了真相", "reason": "数据说服"},
        {"formula": "XX年发行，至今无人超越", "example": "1988年发行，至今无人超越", "reason": "时间背书"},
        {"formula": "XX万人在看，但只有1%%懂", "example": "10万人在看，但只有1%%懂宫崎骏", "reason": "数字反差"},
        {"formula": "XX岁XX岁XX岁，意义完全不同", "example": "10岁30岁60岁看宫崎骏，意义完全不同", "reason": "年龄对比"},
    ],
    "结果承诺": [
        {"formula": "学会XX，只需XX天", "example": "了解宫崎骏，只需3分钟", "reason": "速成承诺"},
        {"formula": "看完这篇，你就能XX", "example": "看完这篇，你就能看懂宫崎骏的温柔", "reason": "收益明确"},
        {"formula": "只要XX分钟，彻底搞懂XX", "example": "只要5分钟，彻底搞懂宫崎骏的世界", "reason": "时间锚定"},
        {"formula": "一张图讲清楚XX", "example": "一张图讲清楚宫崎骏的配色美学", "reason": "简洁承诺"},
        {"formula": "零基础XX天达到XX水平", "example": "零基础审美提升的看书指南", "reason": "进阶路径"},
    ],
    "社会证明": [
        {"formula": "XX人都在找的XX终于找到了", "example": "10万人都在找的绘本终于找到了", "reason": "从众心理"},
        {"formula": "豆瓣9.8，好评率99%%", "example": "豆瓣9.8，宫崎骏粉好评率99%%", "reason": "数据背书"},
        {"formula": "XX推荐的XX果然没错", "example": "博主推荐的果然没错", "reason": "信任转嫁"},
        {"formula": "XX人已入手，都在找", "example": "10000人已入手，都在找原版", "reason": "规模效应"},
        {"formula": "全网都在找的XX", "example": "全网都在找的吉卜力官方授权", "reason": "全网热度"},
    ],
    "争议挑衅": [
        {"formula": "XX凭什么被封神", "example": "宫崎骏凭什么被封神", "reason": "质疑权威"},
        {"formula": "XX真的YY吗", "example": "宫崎骏真的值得封神吗", "reason": "引发争论"},
        {"formula": "别再被XX骗了", "example": "别再被盗版绘本骗了", "reason": "反权威"},
        {"formula": "XX不过是YY的借口", "example": "宫崎骏不过是资本包装的借口", "reason": "颠覆认知"},
        {"formula": "为什么我劝你XX", "example": "为什么我劝你别买盗版绘本", "reason": "反从众"},

    ],
    "场景条件": [
        {"formula": "在XX的人一定要看", "example": "在北上广的人一定要看", "reason": "精准人群"},
        {"formula": "适合XX的场景XX部作品", "example": "适合亲子共读的5部宫崎骏作品", "reason": "场景契合"},
        {"formula": "如果你XX，那一定要XX", "example": "如果你也怀旧，那一定要看", "reason": "条件句"},
        {"formula": "XX岁时最该看的XX", "example": "30岁时最该看的一本书", "reason": "年龄场景"},
        {"formula": "下雨天和XX最配", "example": "下雨天和宫崎骏最配", "reason": "情境营造"},
    ],
    "行动号召": [
        {"formula": "XX限时XX，赶紧XX", "example": "绝版限时，赶紧入手", "reason": "紧迫感"},
        {"formula": "现在就XX，附XX方法", "example": "现在就收藏，附选书方法", "reason": "行动+方法"},
        {"formula": "别等了，XX立刻XX", "example": "别等了，绘本立刻入手", "reason": "催促行动"},
        {"formula": "先收藏，XX再说", "example": "先收藏，买书再说", "reason": "收藏优先"},
        {"formula": "XX的正确打开方式", "example": "宫崎骏作品的正确打开方式", "reason": "方法引导"},
    ],
    "权威借力": [
        {"formula": "XX亲口说XX", "example": "宫崎骏亲口说他想退休", "reason": "权威引用"},
        {"formula": "XX都在用的XX方法", "example": "设计师都在用的配色方法", "reason": "权威群体"},
        {"formula": "XX强推的XX", "example": "豆瓣强推的绘本", "reason": "平台背书"},
        {"formula": "连XX都认可的XX", "example": "连宫崎骏都认可的画师", "reason": "跨界背书"},
        {"formula": "XX都在推荐的XX", "example": "知乎都在推荐的绘本", "reason": "媒体背书"},
    ],
    "互动测试": [
        {"formula": "XX个里有多少XX", "example": "宫崎骏10部作品你看过几部", "reason": "挑战式"},
        {"formula": "测测你是XX还是XX", "example": "测测你是普通人还是宫崎骏粉", "reason": "身份测试"},
        {"formula": "XX的XX程度有多高", "example": "你的宫崎骏了解程度有多高", "reason": "兴趣探测"},
        {"formula": "答对这XX道题才算XX", "example": "答对3道题才算真爱粉", "reason": "游戏化"},
        {"formula": "你是XX%%的XX", "example": "你是80%%的宫崎骏铁粉", "reason": "标签赋值"},
    ],
}

# ================= 辅助函数 =================
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return resp.json().get("tenant_access_token")

def build_formulas_prompt(topic, style):
    """构建75个公式说明，用于prompt"""
    lines = []
    for trigger, formulas in TITLE_FORMULAS.items():
        lines.append(f"\n## {trigger}")
        for f in formulas:
            lines.append(f"  - {f['formula']}（例：{f['example']}）")
    return "\n".join(lines)

# ================= 核心：DeepSeek生成发布文案 =================
def generate_publish_info(book_name, oral_script, style_type=""):
    print(f"DeepSeek 正在为《{book_name}》撰写发布文案...")

    style_desc = ""
    if style_type == "大师画像型":
        style_desc = "大师画像型（人格背书+价值观输出）：矛盾反差开篇 + 极致数据支撑 + 价值观升华"
    elif style_type == "故事叙事型":
        style_desc = "故事叙事型（情感治愈+亲子场景）：戏剧性悬念开篇 + 揭秘共情 + 治愈感收束"
    elif style_type == "视觉展示型":
        style_desc = "视觉展示型（工艺震撼+稀缺性促单）：视觉冲击开篇 + 工艺细节轰炸"
    else:
        style_desc = "请根据口播文案内容自行判断最佳标题风格"

    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}

    prompt = f"""
你是抖音带货运营专家，擅长从75个爆款公式中匹配最合适的标题。

【任务】
根据以下口播文案，从12类心理触发器中匹配，生成最优标题。

【口播文案】
{oral_script[:2000]}

【可选风格】
{style_desc}

【75个爆款公式 - 必须从中选择最匹配的1-2个】
{build_formulas_prompt(book_name, style_type)}

【12类心理触发器速查】
1. 认知冲突：打破读者认知（99%的人都不知道 / XX？错！恰恰相反）
2. 好奇缺口：制造信息差（秘密藏在这里 / 原来是这个意思）
3. 恐惧损失：不做会后悔（错过XX你会损失什么 / 正在绝版）
4. 身份代入：我是这样的人（XX的人都在悄悄做 / 真正的XX都明白）
5. 数字锚点：具体数字说服（XX个XX / XX年发行至今）
6. 结果承诺：承诺明确效果（只需XX天 / 看完就能XX）
7. 社会证明：大家都在用（XX人都在找 / 豆瓣9.8）
8. 争议挑衅：引发讨论（XX凭什么 / 别再被骗了）
9. 场景条件：在XX情况下（适合XX的场景 / 如果你XX）
10. 行动号召：立刻行动（限时 / 别等了 / 先收藏）
11. 权威借力：专家都说（XX亲口说 / XX都在用）
12. 互动测试：测试类（你做过XX吗 / 测测你是XX还是XX）

【输出格式 - 必须严格返回JSON】
{{
    "video_title": "视频标题（20字以内，必须包含强情绪符号?！：——，制造悬念或冲突）",
    "video_desc": "视频简介（50-100字，必须包含3-5个#话题标签，必须有互动引导）",
    "product_short_name": "商品短标题（严格10字以内，突出稀缺性或唯一性）",
    "matched_formulas": ["匹配到的1-2个公式名称，如：认知冲突-99%的人都不知道的XX"],
    "reason": "选择这些公式的理由"
}}

【标题生成原则】
1. 必须包含强情绪符号（？！：——）之一
2. 必须制造悬念或冲突感，禁止平铺直叙
3. 必须匹配口播文案的核心情绪（口播文案是崇敬/温暖/悬念/愤怒？）
4. 商品短标题要突出稀缺性：限定版/珍藏礼盒/绝版
5. 禁止：教你/必看/几招/什么是XX（平铺直叙）
"""

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        content = resp.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"生成失败: {e}")
        return None

# ================= 飞书操作 =================
def get_records_with_scripts():
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_TOKEN}/tables/{FEISHU_TABLE_ID}/records?page_size=100"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    records = resp.json().get("data", {}).get("items", [])
    tasks = []
    for item in records:
        fields = item.get("fields", {})
        status = fields.get("状态", "")
        # 状态是"待筛选"且有口播文案
        if status in ["待筛选", "待下单", "已下单", "已拍摄"]:
            script = fields.get("口播文案", "")
            if script:
                tasks.append({
                    "id": item.get("record_id"),
                    "book": fields.get("选题标题", "未知书籍"),
                    "script": script,
                    "status": status
                })
    return tasks

def update_feishu_publish_info(record_id, info):
    token = get_feishu_token()
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_TOKEN}/tables/{FEISHU_TABLE_ID}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    fields = {
        "标题": info.get('video_title', ''),
        "简介": info.get('video_desc', ''),
        "商品短标题": info.get('product_short_name', '')
    }
    resp = requests.put(url, headers=headers, json={"fields": fields})
    return resp.json().get("code") == 0

# ================= 主程序 =================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='抖音发布文案生成器')
    parser.add_argument('topic', nargs='?', help='话题/书名')
    parser.add_argument('style', nargs='?', help='风格类型：大师画像型/故事叙事型/视觉展示型')
    parser.add_argument('--script', dest='script', help='口播文案内容')
    parser.add_argument('--record-id', dest='record_id', help='飞书记录ID，直接回填该记录')
    parser.add_argument('--feishu', action='store_true', help='从飞书获取待处理任务并回填')
    args = parser.parse_args()

    if args.feishu:
        # 从飞书获取任务
        print("扫描飞书待处理任务...")
        tasks = get_records_with_scripts()
        print(f"扫描到 {len(tasks)} 个待生成文案的任务")
        for task in tasks:
            print(f"\n--- 处理: {task['book']} [{task['status']}] ---")
            if not task['script']:
                print("跳过：无口播文案")
                continue
            result = generate_publish_info(task['book'], task['script'])
            if result:
                print(f"  标题: {result.get('video_title', '')}")
                print(f"  短标题: {result.get('product_short_name', '')}")
                print(f"  匹配公式: {result.get('matched_formulas', [])}")
                ok = update_feishu_publish_info(task['id'], result)
                print(f"  回填: {'OK' if ok else 'FAIL'}")
            time.sleep(1)
        print("\n全部完成！")

    elif args.topic:
        # 直接生成
        script = args.script or "（无口播文案，请根据话题自行生成）"
        result = generate_publish_info(args.topic, script, args.style or "")
        if result:
            print("\n========== 生成结果 ==========")
            print(f"视频标题: {result.get('video_title', '')}")
            print(f"视频简介: {result.get('video_desc', '')}")
            print(f"商品短标题: {result.get('product_short_name', '')}")
            print(f"匹配公式: {result.get('matched_formulas', [])}")
            print(f"选择理由: {result.get('reason', '')}")

            if args.record_id:
                ok = update_feishu_publish_info(args.record_id, result)
                print(f"\n飞书回填: {'OK' if ok else 'FAIL'}")

    else:
        print("用法:")
        print("  python 自动写标题和简介.py --feishu              # 从飞书获取任务并回填")
        print("  python 自动写标题和简介.py '宫崎骏作品集' '大师画像型' --script '口播文案...'")
        print("  python 自动写标题和简介.py '宫崎骏作品集' '故事叙事型' --record-id 'recxxx'")
