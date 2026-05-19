"""
选品数据抓取工具
用于从各种渠道抓取商品数据，并整理成飞书表格可导入的格式

支持：
1. 单品抓取：输入商品链接
2. 批量处理：输入多个链接或从文件读取
3. 手动录入：直接输入数据

输出：JSON格式，便于导入飞书表格
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import io
import argparse

# 设置控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 模拟User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def detect_source(url):
    """检测商品链接来源"""
    if not url:
        return "unknown"

    url = url.lower()

    if "huitun" in url or "灰豚" in url:
        return "灰豚数据"
    elif "douyin" in url or "字节" in url:
        return "抖音精选联盟"
    elif "dangdang" in url or "当当" in url:
        return "当当网"
    elif "jd.com" in url or "京东" in url:
        return "京东"
    elif "taobao" in url or "淘宝" in url:
        return "淘宝"
    elif "tmall" in url or "天猫" in url:
        return "天猫"
    else:
        return "unknown"


def parse_douyin_jingxuan(url):
    """解析抖音精选联盟商品"""
    # 抖音精选联盟链接格式
    # https://haohuo.jinritemai.com/ecommerce/channel/list?id=xxx
    # https://www.douyin.com/aweme/v1/web/aweme/v2/?...

    result = {
        "source": "抖音精选联盟",
        "product_name": "",
        "price": 0,
        "commission_rate": 0,
        "sales_30d": 0,
        "shop_score": 0,
        "good_rate": 0,
        "video_ratio": 0,
        "conversion_rate": 0,
        "creator_count": 0,
        "url": url
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试从页面提取信息
        # 商品标题通常在 title 或者特定 class 中
        title = soup.find('title')
        if title:
            result["product_name"] = title.text.strip()

        # 提取价格
        price_pattern = re.compile(r'[\d.]+')
        price_elem = soup.find(string=re.compile(r'价格|¥|￥'))
        if price_elem:
            price_match = price_pattern.search(price_elem)
            if price_match:
                result["price"] = float(price_match.group())

    except Exception as e:
        print(f"抓取失败: {e}")

    return result


def parse_dangdang(url):
    """解析当当网商品"""
    result = {
        "source": "当当网",
        "product_name": "",
        "price": 0,
        "commission_rate": 0,  # 当当通常没有佣金
        "sales_30d": 0,
        "shop_score": 0,
        "good_rate": 0,
        "video_ratio": 0,
        "conversion_rate": 0,
        "creator_count": 0,
        "url": url
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 商品名称
        name_elem = soup.find('h1') or soup.find('title')
        if name_elem:
            result["product_name"] = name_elem.text.strip()

        # 价格
        price_elem = soup.find('span', class_='price_n')
        if price_elem:
            price_text = price_elem.text.replace('¥', '').replace('￥', '')
            try:
                result["price"] = float(price_text)
            except:
                pass

        # 好评率
        rate_elem = soup.find('span', id='comments_count')
        if rate_elem:
            result["good_rate"] = 95  # 默认值，需要进一步解析

    except Exception as e:
        print(f"抓取失败: {e}")

    return result


def parse_jd(url):
    """解析京东商品"""
    result = {
        "source": "京东",
        "product_name": "",
        "price": 0,
        "commission_rate": 0,
        "sales_30d": 0,
        "shop_score": 0,
        "good_rate": 0,
        "video_ratio": 0,
        "conversion_rate": 0,
        "creator_count": 0,
        "url": url
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 商品名称
        name_elem = soup.find('div', class_='sku-name')
        if name_elem:
            result["product_name"] = name_elem.text.strip()
        else:
            title = soup.find('title')
            if title:
                result["product_name"] = title.text.split('_')[0]

        # 价格
        price_elem = soup.find('span', class_='price')
        if price_elem:
            price_text = re.search(r'[\d.]+', price_elem.text)
            if price_text:
                result["price"] = float(price_text.group())

    except Exception as e:
        print(f"抓取失败: {e}")

    return result


def scrape_product(url):
    """根据URL自动识别来源并抓取"""
    source = detect_source(url)
    print(f"检测到来源: {source}")

    if source == "抖音精选联盟":
        return parse_douyin_jingxuan(url)
    elif source == "当当网":
        return parse_dangdang(url)
    elif source == "京东":
        return parse_jd(url)
    elif source == "灰豚数据":
        print("提示: 灰豚数据需要登录，建议手动复制数据或使用其他方式获取")
        return {"source": "灰豚数据", "url": url, "note": "需要手动录入数据"}
    else:
        print("未知来源，尝试通用解析...")
        return parse_generic(url)


def parse_generic(url):
    """通用解析（尝试提取基本信息）"""
    result = {
        "source": detect_source(url),
        "product_name": "",
        "price": 0,
        "commission_rate": 0,
        "sales_30d": 0,
        "shop_score": 0,
        "good_rate": 0,
        "video_ratio": 0,
        "conversion_rate": 0,
        "creator_count": 0,
        "url": url
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试获取标题
        title = soup.find('title')
        if title:
            result["product_name"] = title.text.strip()

    except Exception as e:
        print(f"抓取失败: {e}")

    return result


def manual_input():
    """手动输入商品数据"""
    print("\n=== 手动录入商品数据 ===")
    print("(直接回车使用默认值)\n")

    data = {
        "source": "手动录入",
        "product_name": input("产品名称: ") or "",
        "price": float(input("客单价(元): ") or 0),
        "commission_rate": float(input("佣金率(%): ") or 0),
        "sales_30d": int(input("近30天销量: ") or 0),
        "shop_score": float(input("商家体验分: ") or 0),
        "good_rate": float(input("好评率(%): ") or 0),
        "video_ratio": float(input("短视频出单占比(%): ") or 0),
        "conversion_rate": float(input("昨日转化率(%): ") or 0),
        "creator_count": int(input("出单达人数: ") or 0),
        "url": input("商品链接: ") or "",
        "note": ""
    }

    return data


def calculate_score(data):
    """计算综合评分"""
    score = 0

    # 必须满足（不加分，只检查）
    required_pass = (
        data.get("sales_30d", 0) >= 5000 and
        data.get("video_ratio", 0) >= 50 and
        data.get("shop_score", 0) >= 85
    )

    if not required_pass:
        return 0, "未满足必须项"

    # 加分项
    if data.get("commission_rate", 0) >= 20:
        score += 2
    if 9.9 <= data.get("price", 0) <= 29.9:
        score += 1
    if data.get("good_rate", 0) >= 85:
        score += 1
    if data.get("video_ratio", 0) >= 50:  # 达人榜前三占比暂时用短视频占比代替
        score += 1
    if data.get("conversion_rate", 0) >= 15:
        score += 1
    if data.get("creator_count", 0) < 500:
        score += 1

    # 评级
    if score >= 7:
        rating = "重点跟进"
    elif score >= 5:
        rating = "可尝试"
    else:
        rating = "一般"

    return score, rating


def format_for_feishu(data):
    """格式化为飞书导入格式"""
    score, rating = calculate_score(data)

    return {
        "产品名称": data.get("product_name", ""),
        "商品链接": data.get("url", ""),
        "客单价": data.get("price", 0),
        "佣金率": data.get("commission_rate", 0),
        "近30天销量": data.get("sales_30d", 0),
        "短视频出单占比": data.get("video_ratio", 0),
        "商家体验分": data.get("shop_score", 0),
        "好评率": data.get("good_rate", 0),
        "达人榜前三占比": data.get("top3_ratio", 0),
        "昨日转化率": data.get("conversion_rate", 0),
        "出单达人数": data.get("creator_count", 0),
        "综合评分": score,
        "数据来源": data.get("source", ""),
        "跟进状态": rating,
        "选品理由": data.get("note", ""),
        "备注": ""
    }


def print_result(data):
    """打印结果"""
    feishu_data = format_for_feishu(data)

    print("\n" + "="*50)
    print("抓取结果")
    print("="*50)

    for key, value in feishu_data.items():
        if key == "商品链接":
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")

    print("="*50)
    return feishu_data


def batch_process(urls):
    """批量处理多个URL"""
    results = []

    for url in urls:
        print(f"\n处理: {url}")
        data = scrape_product(url)
        results.append(data)

    return results


def main():
    parser = argparse.ArgumentParser(description='选品数据抓取工具')
    parser.add_argument('--url', '-u', help='商品链接')
    parser.add_argument('--batch', '-b', help='批量处理文件(每行一个URL)')
    parser.add_argument('--manual', '-m', action='store_true', help='手动录入模式')
    parser.add_argument('--output', '-o', help='输出文件(JSON格式)')

    args = parser.parse_args()

    # 手动录入模式
    if args.manual:
        data = manual_input()
        result = print_result(data)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n已保存到: {args.output}")
        return

    # 单URL模式
    if args.url:
        data = scrape_product(args.url)
        result = print_result(data)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n已保存到: {args.output}")
        return

    # 批量模式
    if args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]

        results = batch_process(urls)

        print("\n" + "="*50)
        print(f"批量处理完成，共 {len(results)} 个商品")
        print("="*50)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"已保存到: {args.output}")
        return

    # 交互模式
    print("=== 选品数据抓取工具 ===")
    print("1. 手动录入数据")
    print("2. 输入商品链接")

    choice = input("请选择(1/2): ").strip()

    if choice == "1":
        data = manual_input()
        result = print_result(data)
    elif choice == "2":
        url = input("请输入商品链接: ").strip()
        if url:
            data = scrape_product(url)
            result = print_result(data)
        else:
            print("未输入链接")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()
