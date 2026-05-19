#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
下载百度图片的脚本
"""

import os
import requests
import urllib.parse

# 代理设置
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 3:4比例的书籍封面URL列表
image_urls = [
    "https://img0.baidu.com/it/u=2131425301,2976142436&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667",
    "https://img1.baidu.com/it/u=3772581655,3818464207&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667",
    "https://img0.baidu.com/it/u=2519880319,3361742493&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667",
    "https://img1.baidu.com/it/u=1979320076,1053382986&fm=253&app=138&f=JPEG?w=500&h=667",
    "https://img2.baidu.com/it/u=2532779440,1896446188&fm=253&app=138&f=JPEG?w=500&h=667",
    "https://img2.baidu.com/it/u=2320766855,1905886795&fm=253&app=138&f=JPEG?w=500&h=667",
    "https://img0.baidu.com/it/u=961711560,3741667110&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=695",
    "https://img2.baidu.com/it/u=3371816641,2890829682&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=667",
    "https://img1.baidu.com/it/u=3283431765,3023947880&fm=253&app=138&f=JPEG?w=500&h=667",
    "https://img0.baidu.com/it/u=151114794,1877762080&fm=253&app=138&f=JPEG?w=500&h=667",
]

# 输出目录
output_dir = r"E:\1.work\douyin\1.shuixing\01_Projects_制作中\莎士比亚集\封面候选"
os.makedirs(output_dir, exist_ok=True)

# 下载图片
for i, url in enumerate(image_urls, 1):
    try:
        # 对URL进行编码处理
        parsed = urllib.parse.urlparse(url)
        new_query = urllib.parse.quote(parsed.query, safe='=&?')
        full_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

        response = requests.get(full_url, proxies=proxies, timeout=30)
        if response.status_code == 200:
            filename = f"封面候选_{i}.jpg"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[OK] 下载成功: {filename}")
        else:
            print(f"[FAIL] 下载失败 ({response.status_code}): {url}")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")

print("\n下载完成！")
