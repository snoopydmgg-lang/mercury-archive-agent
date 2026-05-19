# -*- coding: utf-8 -*-
import requests
import sys
import io
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APP_ID = "cli_a90dbd544bb8dcb2"
APP_SECRET = "dwBXEcMgSD4pxGGEqSKB3tYQDdiBwgf2"
BITABLE_TOKEN = "MZAobRwwnaxN0ls1NGpcvPNhnSb"  # 用户正确的表格
TABLE_ID = "tblox3GzJPGvtkZf"  # 选品追踪表

# 字段名映射
FIELD_MAP = {
    "客单价": "fldFZf4XAH",
    "佣金率": "fldg1PI87r",
    "昨日转化率": "flds8Tl48B",
    "近30天销量": "fldpEcph3K",
    "出单达人数": "fld6oidwie",
    "商家体验分": "fldD8KbrId",
}


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

    if experience > 0 and experience < 4.3:
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

    print(f"共 {len(records)} 条记录\n")

    CORE_FIELDS = ["昨日转化率", "近30天销量", "出单达人数", "商家体验分"]

    missing_report = []
    valid_records = []

    for r in records:
        fields = r.get("fields", {})
        name = fields.get("产品名称", fields.get("商品名称", "未命名"))
        missing = [f for f in CORE_FIELDS if safe_float(fields.get(f)) is None]
        if missing:
            missing_report.append({"产品名称": name, "record_id": r.get("record_id"), "缺失字段": " / ".join(missing)})
        else:
            valid_records.append(r)

    print(f"[WARNING] {len(missing_report)} 条缺失数据")
    for m in missing_report[:5]:
        print(f"  - {m['产品名称'][:25]}: {m['缺失字段']}")
    if len(missing_report) > 5:
        print(f"  ... 还有 {len(missing_report)-5} 条")
    print()

    if not valid_records:
        print("[ERROR] 无有效记录")
        return

    # 计算范围
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

    print(f"有效记录: {len(valid_records)} 条")
    print(f"预估佣金范围: {stats['comm_min']:.2f} ~ {stats['comm_max']:.2f}")
    print(f"转化率范围: {stats['conv_min']:.2f}% ~ {stats['conv_max']:.2f}%")
    print(f"销量范围: {stats['sales_min']:.0f} ~ {stats['sales_max']:.0f}")
    print()

    # 先创建 Score 字段
    r = requests.post(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields",
        headers=headers, json={"field_name": "Score", "type": 2}
    )
    result = r.json()
    if result.get("code") == 0:
        score_field_id = result["data"]["field"]["field_id"]
        print(f"Score字段创建成功: {score_field_id}")
    else:
        # 字段可能已存在，查找它
        r = requests.get(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/fields", headers=headers)
        for f in r.json().get("data", {}).get("items", []):
            if f.get("field_name") == "Score":
                score_field_id = f.get("field_id")
                print(f"Score字段已存在: {score_field_id}")
                break
        else:
            print(f"Score字段创建失败: {result.get('msg')}")
            return

    print()
    print(f"{'序号':<4} {'产品名称':<28} {'总分':<8} {'状态':<10}")
    print("-" * 56)

    scored = []
    for idx, r in enumerate(valid_records, 1):
        fields = r.get("fields", {})
        name = fields.get("产品名称", fields.get("商品名称", "未命名"))[:26]
        score, status = calculate_score(r, stats)
        rid = r.get("record_id")

        # 写入飞书
        resp = requests.put(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_TOKEN}/tables/{TABLE_ID}/records/{rid}",
            headers=headers, json={"fields": {"Score": score}}
        )
        write_ok = resp.json().get("code") == 0
        reason = " [熔断]" if status == "熔断" else ""
        print(f"{idx:<4} {name:<28} {score:<8.1f} {status:<10}{reason} | {'OK' if write_ok else 'FAIL'}")
        scored.append({"产品名称": name, "总分": score, "状态": status})

    # 保存
    score_path = "E:/1.work/douyin/1.shuixing/04_数据分析结果/选品评分报告_v5.csv"
    with open(score_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["产品名称", "总分", "状态"])
        writer.writeheader()
        writer.writerows(scored)

    miss_path = "E:/1.work/douyin/1.shuixing/04_数据分析结果/选品缺失数据报告.csv"
    with open(miss_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["产品名称", "record_id", "缺失字段"])
        writer.writeheader()
        writer.writerows(missing_report)

    print(f"\n评分报告: {score_path}")
    print(f"缺失报告: {miss_path}")


if __name__ == "__main__":
    main()
