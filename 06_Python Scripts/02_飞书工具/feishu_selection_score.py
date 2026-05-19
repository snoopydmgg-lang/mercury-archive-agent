# -*- coding: utf-8 -*-
"""
飞书选品评分脚本 v4 - 最终版
使用 cli_a90dbd544bb8dcb2 (有写入权限)
评分字段: Score (ASCII字段名避免编码问题)
"""
import requests
import sys
import io
import json
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "DS65bww0Kazokosc3AXcITPsnUf"
TABLE_ID = "tblZP96FGm0KpTjR"
SCORE_FIELD = "Score"  # ASCII字段名，避免编码问题

CORE_FIELDS = ["昨日转化率", "近30天销量", "出单达人数", "商家体验分"]


def get_token():
    resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return resp.json().get("tenant_access_token")


def safe_float(val, default=None):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    try:
        return float(str(val).replace("%", "").strip())
    except:
        return default


def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 50.0
    if value is None:
        return 0.0
    return max(0.0, min(100.0, (value - min_val) / (max_val - min_val) * 100))


def calculate_score(record, stats):
    fields = record.get("fields", {})
    price = safe_float(fields.get("客单价"), 0)
    commission = safe_float(fields.get("佣金率"), 0)
    conversion = safe_float(fields.get("昨日转化率"), 0)
    sales_30d = safe_float(fields.get("近30天销量"), 0)
    influencers = safe_float(fields.get("出单达人数"), 0)
    experience = safe_float(fields.get("商家体验分"), 0)

    absolute_commission = price * commission / 100

    comm_score = normalize(absolute_commission, stats["comm_min"], stats["comm_max"])
    conv_score = normalize(conversion, stats["conv_min"], stats["conv_max"])
    module_a = comm_score * 0.25 + conv_score * 0.20

    sales_score = normalize(sales_30d, stats["sales_min"], stats["sales_max"])
    infl_score = normalize(influencers, stats["infl_min"], stats["infl_max"])
    module_b = sales_score * 0.25 + infl_score * 0.15

    exp_score = normalize(experience, stats["exp_min"], stats["exp_max"])
    module_c = exp_score * 0.15

    if experience > 0 and experience < 43:
        return 0.0, "熔断"

    return round(module_a + module_b + module_c, 1), "OK"


def main():
    token = get_token()
    if not token:
        print("获取token失败")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.get(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records",
        headers=headers, params={"page_size": 100}
    )
    records = resp.json().get("data", {}).get("items", [])
    if not records:
        print("未获取到任何记录")
        return

    print(f"=== 选品评分 v4 - 共 {len(records)} 条记录 ===\n")

    # 分离有效数据和缺失数据
    missing_report = []
    valid_records = []

    for r in records:
        fields = r.get("fields", {})
        name = fields.get("产品名称", "未命名")
        missing = [f for f in CORE_FIELDS if safe_float(fields.get(f)) is None]
        if missing:
            missing_report.append({"产品名称": name, "record_id": r.get("record_id"), "缺失字段": " / ".join(missing)})
        else:
            valid_records.append(r)

    # 输出缺失数据
    if missing_report:
        print(f"[WARNING] {len(missing_report)} 条记录存在数据缺失:\n")
        for m in missing_report:
            print(f"  - {m['产品名称'][:30]}: 缺失 [{m['缺失字段']}]")
        print()

        csv_path = "E:/1.work/douyin/1.shuixing/04_数据分析结果/选品缺失数据报告.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["产品名称", "record_id", "缺失字段"])
            writer.writeheader()
            writer.writerows(missing_report)
        print(f"缺失数据报告: {csv_path}\n")
    else:
        print("[INFO] 所有记录核心指标完整\n")

    if not valid_records:
        print("[ERROR] 无有效记录")
        return

    # 计算标准化范围
    comms = [safe_float(r["fields"].get("客单价"), 0) * safe_float(r["fields"].get("佣金率"), 0) / 100 for r in valid_records]
    sales = [safe_float(r["fields"].get("近30天销量"), 0) for r in valid_records]
    convs = [safe_float(r["fields"].get("昨日转化率"), 0) for r in valid_records]
    infls = [safe_float(r["fields"].get("出单达人数"), 0) for r in valid_records]
    exps = [safe_float(r["fields"].get("商家体验分"), 0) for r in valid_records]

    stats = {
        "comm_min": min(comms), "comm_max": max(comms),
        "sales_min": min(sales), "sales_max": max(sales),
        "conv_min": min(convs), "conv_max": max(convs),
        "infl_min": min(infls), "infl_max": max(infls),
        "exp_min": min(exps), "exp_max": max(exps),
    }

    print(f"标准化范围（{len(valid_records)} 条有效记录）:")
    print(f"  预估单笔佣金: {stats['comm_min']:.2f} ~ {stats['comm_max']:.2f}")
    print(f"  转化率: {stats['conv_min']:.2f}% ~ {stats['conv_max']:.2f}%")
    print(f"  近30天销量: {stats['sales_min']:.0f} ~ {stats['sales_max']:.0f}")
    print(f"  出单达人数: {stats['infl_min']:.0f} ~ {stats['infl_max']:.0f}")
    print(f"  商家体验分: {stats['exp_min']:.2f} ~ {stats['exp_max']:.2f}")
    print()

    print(f"{'序号':<4} {'产品名称':<30} {'总分':<8} {'状态':<10}")
    print("-" * 58)

    scored = []
    for idx, r in enumerate(valid_records, 1):
        fields = r.get("fields", {})
        name = fields.get("产品名称", "未命名")[:28]
        score, status = calculate_score(r, stats)
        rid = r.get("record_id")

        # 写入飞书
        write_ok = False
        if rid:
            resp = requests.put(
                f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{rid}",
                headers=headers, json={"fields": {SCORE_FIELD: score}}
            )
            write_ok = resp.json().get("code") == 0

        write_status = "写入OK" if write_ok else "写入FAIL"
        reason = " [熔断]" if status == "熔断" else ""
        print(f"{idx:<4} {name:<30} {score:<8.1f} {status:<10}{reason} | {write_status}")
        scored.append({"产品名称": fields.get("产品名称"), "总分": score, "状态": status})

    # 保存报告
    score_path = "E:/1.work/douyin/1.shuixing/04_数据分析结果/选品评分报告_v4.csv"
    with open(score_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["产品名称", "总分", "状态"])
        writer.writeheader()
        writer.writerows(scored)

    print(f"\n评分报告: {score_path}")
    print(f"有效记录: {len(valid_records)} | 缺失数据: {len(missing_report)}")


if __name__ == "__main__":
    main()
