"""
抓取 OpenRouter 所有模型定价，生成 Wiki 页面
输出到 03_Assets_全局库/wiki/AI工具谱/openrouter-pricing.md
"""

import json
import urllib.request
from datetime import datetime

URL = "https://openrouter.ai/api/v1/models"

def fetch_models():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())["data"]

def fmt_price(p):
    """将每 token 价格转换为每百万 token 价格（美元）"""
    if p is None or p == "0":
        return "FREE"
    val = float(p) * 1_000_000
    if val == 0:
        return "FREE"
    if val < 0.001:
        return f"${val:.6f}"
    if val < 0.01:
        return f"${val:.4f}"
    if val < 1:
        return f"${val:.3f}"
    return f"${val:.2f}"

def group_by_provider(models):
    groups = {}
    for m in models:
        provider = m["id"].split("/")[0]
        groups.setdefault(provider, []).append(m)
    return groups

def build_wiki(models):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append(f"# OpenRouter 模型定价表\n")
    lines.append(f"> 数据来源：[openrouter.ai/api/v1/models](https://openrouter.ai/api/v1/models)  \n> 更新时间：{today}  \n> 单位：美元 / 百万 Token（M tokens）\n")
    lines.append("---\n")

    # 汇总免费模型
    free_models = [m for m in models if m["pricing"]["prompt"] == "0" and m["pricing"]["completion"] == "0"]
    paid_models = [m for m in models if not (m["pricing"]["prompt"] == "0" and m["pricing"]["completion"] == "0")]

    # 收费模型按价格排序（输入价格）
    def input_price(m):
        try:
            return float(m["pricing"]["prompt"])
        except:
            return 999

    paid_models.sort(key=input_price)

    lines.append("## 收费模型（按输入价格升序）\n")
    lines.append("| 模型 ID | 名称 | 输入 $/M | 输出 $/M | 上下文 |")
    lines.append("|---------|------|----------|----------|--------|")

    for m in paid_models:
        mid = m["id"]
        name = m["name"]
        ctx = f"{m['context_length']//1000}K" if m['context_length'] else "-"
        inp = fmt_price(m["pricing"].get("prompt"))
        out = fmt_price(m["pricing"].get("completion"))
        lines.append(f"| `{mid}` | {name} | {inp} | {out} | {ctx} |")

    lines.append("")
    lines.append("---\n")
    lines.append(f"## 免费模型（{len(free_models)} 个）\n")
    lines.append("| 模型 ID | 名称 | 上下文 |")
    lines.append("|---------|------|--------|")
    for m in free_models:
        mid = m["id"]
        name = m["name"]
        ctx = f"{m['context_length']//1000}K" if m['context_length'] else "-"
        lines.append(f"| `{mid}` | {name} | {ctx} |")

    lines.append("")
    lines.append("---\n")

    # 按厂商分组汇总
    lines.append("## 按厂商汇总（收费模型）\n")
    groups = group_by_provider(paid_models)
    for provider in sorted(groups.keys()):
        ms = groups[provider]
        lines.append(f"### {provider} ({len(ms)} 个模型)\n")
        lines.append("| 模型 ID | 输入 $/M | 输出 $/M | 上下文 |")
        lines.append("|---------|----------|----------|--------|")
        for m in sorted(ms, key=input_price):
            mid = m["id"]
            ctx = f"{m['context_length']//1000}K" if m['context_length'] else "-"
            inp = fmt_price(m["pricing"].get("prompt"))
            out = fmt_price(m["pricing"].get("completion"))
            lines.append(f"| `{mid}` | {inp} | {out} | {ctx} |")
        lines.append("")

    return "\n".join(lines)

def main():
    print("正在抓取 OpenRouter 模型列表...")
    models = fetch_models()
    print(f"共获取 {len(models)} 个模型")

    wiki = build_wiki(models)

    out_path = "E:/1.work/douyin/1.shuixing/03_Assets_全局库/wiki/AI工具谱/openrouter-pricing.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(wiki)

    print(f"已写入：{out_path}")

    # 统计
    free = sum(1 for m in models if m["pricing"]["prompt"] == "0" and m["pricing"]["completion"] == "0")
    paid = len(models) - free
    print(f"  收费模型：{paid} 个，免费模型：{free} 个")

if __name__ == "__main__":
    main()
