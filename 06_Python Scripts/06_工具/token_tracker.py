#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Token 使用量追踪器 - 本地累积统计 + DeepSeek 官方 CSV EMA 校准
用法:
  python token_tracker.py                    # Rich 仪表盘（默认，彩色单块）
  python token_tracker.py --compact          # 纯 ASCII 仪表盘（无颜色）
  python token_tracker.py --rich             # 旧 ANSI 字符画仪表盘
  python token_tracker.py --detail           # 详细模式（需配合 --rich）
  python token_tracker.py --session          # 仅当前 session
  python token_tracker.py --today            # 仅今天
  python token_tracker.py --month            # 仅本月
  python token_tracker.py --json             # JSON 输出（供其他脚本消费）
  python token_tracker.py --update-cache     # 强制更新缓存
"""

import csv
import hashlib
import json
import sys
import io
import os
import calendar
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta
from collections import defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED

console = Console(width=72, force_terminal=True, color_system="truecolor", highlight=False)

# ── 费率配置 ──────────────────────────────────────────────
PRICING = {
    "deepseek-v4-pro": {
        "input": 3.00,
        "output": 6.00,
        "cache_hit": 0.025,
        "currency": "RMB",
        "note": "DeepSeek V4 Pro 2.5折优惠价 (原价 ¥12/¥24/¥0.1), 有效期至 2026/05/31"
    },
}

DEFAULT_MODEL = "deepseek-v4-pro"

MODEL_ALIAS_MAP = {
    "claude-opus-4-7": "deepseek-v4-pro",
    "deepseek-v4-pro": "deepseek-v4-pro",
}

CACHE_VERSION = 3

# Windows 终端编码
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOME = Path.home()
PROJECTS_DIR = HOME / '.claude' / 'projects'
CACHE_FILE = HOME / '.claude' / '.token_usage_cache.json'
CACHE_TTL_HOURS = 1

ANSI_RED = '\033[91m'
ANSI_YELLOW = '\033[93m'
ANSI_GREEN = '\033[92m'
ANSI_CYAN = '\033[96m'
ANSI_RESET = '\033[0m'
ANSI_BOLD = '\033[1m'
ANSI_DIM = '\033[2m'

# ── SQLite 持久化配置 ────────────────────────────────────
DB_PATH = str(Path(__file__).resolve().parent.parent / 'token_metrics.db')
DAILY_BUDGET = 10.00
MONTHLY_BUDGET = 200.00

# ── EMA 校准配置 ─────────────────────────────────────────
EMA_ALPHA_TABLE = {
    (1, 3): 0.40,
    (4, 10): 0.25,
    (11, float('inf')): 0.15,
}
CALIBRATION_RATIO_MIN = 0.05
CALIBRATION_RATIO_MAX = 2.0

# ── 官方账单过滤 ─────────────────────────────────────────
EXCLUDE_API_KEYS = ['贺杉专用']  # 排除指定 API Key 的用量

# ── 官方账单搜索路径 ─────────────────────────────────────
_inbox_search_paths = [
    Path(__file__).resolve().parent.parent.parent / "00_InBox_收件箱",
    Path(__file__).resolve().parent.parent / "00_InBox_收件箱",
]


def format_tokens(n):
    if n >= 1_000_000:
        return f'{n/1_000_000:.2f}M'
    elif n >= 1_000:
        return f'{n/1_000:.1f}K'
    return str(n)


def resolve_model(transcript_model):
    if not transcript_model:
        return DEFAULT_MODEL
    return MODEL_ALIAS_MAP.get(transcript_model, DEFAULT_MODEL)


def calculate_cost(input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, model=None):
    model = resolve_model(model)
    pricing = PRICING.get(model, PRICING[DEFAULT_MODEL])
    billable_input = input_tokens + cache_creation_tokens
    ic = billable_input / 1_000_000 * pricing['input']
    oc = output_tokens / 1_000_000 * pricing['output']
    cc = cache_read_tokens / 1_000_000 * pricing['cache_hit']
    return {
        'input_cost': ic,
        'output_cost': oc,
        'cache_cost': cc,
        'total': ic + oc + cc,
        'model': model,
        'pricing': pricing,
        'currency': pricing.get('currency', 'RMB'),
    }


# ══════════════════════════════════════════════════════════
#  官方 CSV 账单解析
# ══════════════════════════════════════════════════════════

def find_billing_csvs():
    for inbox in _inbox_search_paths:
        if not inbox.exists():
            continue
        amounts = sorted(inbox.glob("amount-*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        costs = sorted(inbox.glob("cost-*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if amounts and costs:
            return amounts[0], costs[0]
    return None, None


def file_hash(path):
    """SHA256 of file content for dedup."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_official_billing(amount_path, cost_path, model='deepseek-v4-pro', exclude_api_keys=None):
    """解析官方 CSV，返回按日期聚合的 {date: {cost, tokens_by_type}}。

    排除 exclude_api_keys 中指定的 API Key 用量（amount CSV 中有 api_key_name 字段）。
    cost CSV 没有 api_key 粒度，按 token 占比同比例缩减。
    """
    if exclude_api_keys is None:
        exclude_api_keys = []

    if not amount_path or not cost_path:
        return None
    if not amount_path.exists() or not cost_path.exists():
        return None

    cost_by_date = defaultdict(lambda: defaultdict(float))
    with open(cost_path, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cost_by_date[row['utc_date']][row['model']] += float(row['cost'])

    tokens_by_date = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    excluded_by_date = defaultdict(lambda: defaultdict(int))  # model -> date -> excluded token count
    with open(amount_path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            typ = row['type']
            if typ == 'request_count':
                continue
            date_key = row['utc_date']
            model_key = row['model']
            amt = int(row['amount'])
            if row.get('api_key_name', '') in exclude_api_keys:
                excluded_by_date[model_key][date_key] += amt
            else:
                tokens_by_date[date_key][model_key][typ] += amt

    # 按 token 占比缩减 cost（cost CSV 没有 api_key 粒度）
    result = {}
    all_dates = set(cost_by_date.keys()) | set(tokens_by_date.keys())
    for d in sorted(all_dates):
        if model in cost_by_date[d] or model in tokens_by_date[d]:
            tok_data = dict(tokens_by_date[d].get(model, {}))
            total_tok = sum(tok_data.values())
            excluded_tok = excluded_by_date.get(model, {}).get(d, 0)
            ratio = total_tok / (total_tok + excluded_tok) if (total_tok + excluded_tok) > 0 else 1.0
            adjusted_cost = cost_by_date[d].get(model, 0.0) * ratio
            result[d] = {
                'cost': adjusted_cost,
                'tokens': tok_data,
            }
    return result


def aggregate_official(billing_data, this_month=None):
    """聚合官方账单: today_cost, month_cost, all_cost, days_active, month_tokens。"""
    if not billing_data:
        return None
    today_str = date.today().isoformat()
    if this_month is None:
        this_month = today_str[:7]

    info = {'today_cost': 0.0, 'month_cost': 0.0, 'all_cost': 0.0,
            'today_tokens': 0, 'month_tokens': 0, 'days_active': 0, 'days': []}
    for d, v in billing_data.items():
        info['all_cost'] += v['cost']
        tok = sum(v['tokens'].values())
        if d == today_str:
            info['today_cost'] += v['cost']
            info['today_tokens'] += tok
        if d.startswith(this_month):
            info['month_cost'] += v['cost']
            info['month_tokens'] += tok
            info['days_active'] += 1
            info['days'].append(d)
    return info


# ══════════════════════════════════════════════════════════
#  EMA 校准引擎
# ══════════════════════════════════════════════════════════

def get_ema_alpha(sample_count):
    """根据样本数量返回 EMA alpha。"""
    for (lo, hi), alpha in EMA_ALPHA_TABLE.items():
        if lo <= sample_count <= hi:
            return alpha
    return 0.15


def is_anomalous_ratio(ratio):
    """判断校准比例是否异常。"""
    return ratio < CALIBRATION_RATIO_MIN or ratio > CALIBRATION_RATIO_MAX


def load_calibration(conn):
    """从 billing_calibration 表加载最新的校准因子。"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT calibration_factor, sample_count, last_ratio, last_updated
        FROM billing_calibration
        ORDER BY id DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    if row:
        return {'factor': row[0], 'samples': row[1], 'last_ratio': row[2], 'updated': row[3]}
    return None


def save_calibration(conn, factor, sample_count, last_ratio):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO billing_calibration (calibration_factor, sample_count, last_ratio)
        VALUES (?, ?, ?)
    ''', (factor, sample_count, last_ratio))
    conn.commit()


def is_csv_imported(conn, amount_hash, cost_hash, config_hash):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM official_billing_imports
        WHERE amount_hash = ? AND cost_hash = ? AND config_hash = ?
    ''', (amount_hash, cost_hash, config_hash))
    return cursor.fetchone() is not None


def mark_csv_imported(conn, amount_hash, cost_hash, config_hash, amount_path, cost_path):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO official_billing_imports (amount_hash, cost_hash, config_hash, amount_file, cost_file)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount_hash, cost_hash, config_hash, str(amount_path), str(cost_path)))
    conn.commit()


def update_ema_calibration(amount_path, cost_path, raw_estimated_month_cost, billing_data):
    """从官方 CSV 更新 EMA 校准因子。

    Returns:
        (calibration_factor, sample_count, mode, official_info) or None on skip
    """
    this_month = date.today().strftime('%Y-%m')
    official = aggregate_official(billing_data, this_month)
    if not official or official['month_cost'] <= 0:
        return None
    if raw_estimated_month_cost <= 0:
        return None

    ratio = official['month_cost'] / raw_estimated_month_cost

    # 异常检测
    if is_anomalous_ratio(ratio):
        return None

    conn = sqlite3.connect(DB_PATH)

    # 去重（配置变更也触发重新校准）
    config_str = ','.join(sorted(EXCLUDE_API_KEYS))
    x_hash = hashlib.sha256(config_str.encode()).hexdigest()[:16]
    a_hash = file_hash(amount_path)
    c_hash = file_hash(cost_path)
    if is_csv_imported(conn, a_hash, c_hash, x_hash):
        conn.close()
        return None

    # 加载历史因子
    prev = load_calibration(conn)
    if prev:
        alpha = get_ema_alpha(prev['samples'] + 1)
        new_factor = alpha * ratio + (1 - alpha) * prev['factor']
        new_samples = prev['samples'] + 1
    else:
        alpha = get_ema_alpha(1)
        new_factor = ratio
        new_samples = 1

    save_calibration(conn, new_factor, new_samples, ratio)
    mark_csv_imported(conn, a_hash, c_hash, x_hash, amount_path, cost_path)
    conn.close()

    return {
        'factor': new_factor,
        'samples': new_samples,
        'alpha': alpha,
        'ratio': ratio,
        'mode': 'OFFICIAL_CSV',
        'official': official,
    }


# ══════════════════════════════════════════════════════════
#  SQLite 持久化引擎
# ══════════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 核心 session metrics 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            session_id TEXT UNIQUE,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_creation_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            input_cost REAL DEFAULT 0.0,
            output_cost REAL DEFAULT 0.0,
            cache_cost REAL DEFAULT 0.0,
            total_cost REAL DEFAULT 0.0,
            model TEXT,
            billing_source TEXT DEFAULT 'transcript_estimate',
            official_cost REAL,
            estimated_cost REAL,
            deviation_ratio REAL,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # 每日账单快照
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing_daily (
            date TEXT PRIMARY KEY,
            billing_source TEXT NOT NULL,
            official_cost REAL NOT NULL,
            estimated_cost REAL,
            deviation_ratio REAL,
            official_tokens INTEGER,
            estimated_tokens INTEGER,
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # EMA 校准因子历史
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing_calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calibration_factor REAL NOT NULL,
            sample_count INTEGER NOT NULL,
            last_ratio REAL,
            last_updated TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # 官方 CSV 导入去重
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS official_billing_imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_hash TEXT NOT NULL,
            cost_hash TEXT NOT NULL,
            config_hash TEXT DEFAULT '',
            amount_file TEXT,
            cost_file TEXT,
            imported_at TEXT DEFAULT (datetime('now', 'localtime')),
            UNIQUE(amount_hash, cost_hash, config_hash)
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_billing_date ON billing_daily(date)')

    # 迁移：旧表可能没有 config_hash 列
    try:
        cursor.execute("ALTER TABLE official_billing_imports ADD COLUMN config_hash TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # 迁移旧表
    for col in ['billing_source', 'official_cost', 'estimated_cost', 'deviation_ratio']:
        try:
            cursor.execute(f"ALTER TABLE metrics ADD COLUMN {col} TEXT DEFAULT 'transcript_estimate'")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


def get_latest_calibration():
    """获取最新校准因子（不依赖当前 CSV）。"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cal = load_calibration(conn)
        conn.close()
        return cal
    except Exception:
        return None


def run_alerts(mode, display_cost, eom_prediction):
    """预算预警与熔断。"""
    today_str = date.today().isoformat()

    print(f"\n[Token Metrics] Daily: ¥{display_cost.get('today', 0):.2f} | "
          f"Monthly: ¥{display_cost.get('month', 0):.2f} | "
          f"EOM Run-Rate: ¥{eom_prediction:.2f} | "
          f"Mode: {mode}")

    if display_cost.get('today', 0) > DAILY_BUDGET:
        print(f"[WARNING] Daily budget exceeded! "
              f"(¥{display_cost['today']:.2f} / ¥{DAILY_BUDGET:.2f})")

    if mode == 'OFFICIAL_CSV' and eom_prediction > MONTHLY_BUDGET:
        print(f"\n[CIRCUIT BREAKER] "
              f"EOM Run-Rate (¥{eom_prediction:.2f}) exceeds budget (¥{MONTHLY_BUDGET:.2f})!")
        if "--confirm-overbudget" not in sys.argv:
            sys.exit(1)
        else:
            print(f"Bypass flag '--confirm-overbudget' detected. Continuing...")
    elif mode != 'OFFICIAL_CSV' and eom_prediction > MONTHLY_BUDGET:
        print(f"[WARNING] EOM (¥{eom_prediction:.2f}) exceeds budget, "
              f"but mode={mode} — no hard breaker.")


def save_session_to_db(session_data):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO metrics (
                date, session_id, input_tokens, output_tokens,
                cache_read_tokens, cache_creation_tokens, total_tokens,
                input_cost, output_cost, cache_cost, total_cost, model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date.today().isoformat(),
            session_data.get('session_id', 'unknown'),
            session_data.get('input_tokens', 0),
            session_data.get('output_tokens', 0),
            session_data.get('cache_read_tokens', 0),
            session_data.get('cache_creation_tokens', 0),
            session_data.get('total_tokens', 0),
            session_data.get('input_cost', 0.0),
            session_data.get('output_cost', 0.0),
            session_data.get('cache_cost', 0.0),
            session_data.get('total_cost', 0.0),
            session_data.get('model', DEFAULT_MODEL)
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def sync_billing_daily(official_info, est_month_cost, cal_factor):
    """同步每日账单快照到 billing_daily 表，并写 cache JSON 供 statusline 读取。"""
    if not official_info:
        return
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today_str = date.today().isoformat()

    off_cost = official_info['month_cost']
    deviation = (est_month_cost / off_cost) if off_cost > 0 else 0.0

    cursor.execute('''
        INSERT OR REPLACE INTO billing_daily
            (date, billing_source, official_cost, estimated_cost, deviation_ratio,
             official_tokens, estimated_tokens)
        VALUES (?, 'OFFICIAL_CSV', ?, ?, ?, ?, ?)
    ''', (
        today_str, off_cost, est_month_cost, deviation,
        official_info.get('month_tokens', 0), 0
    ))

    daily_cost = official_info.get('today_cost', 0)

    conn.commit()
    conn.close()

    # 写 JSON cache 供 statusline 读取（避免每 tick 启动 Python）
    cache_path = str(Path(DB_PATH).parent / 'billing_cache.json')
    import json
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump({
            'daily': round(daily_cost, 2),
            'monthly': round(off_cost, 2),
            'updated': datetime.now().isoformat()
        }, f, ensure_ascii=False)


def sync_cache_to_db(cache):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    written = 0
    for s in cache.get('sessions', []):
        cost = calculate_cost(
            s['input'], s['output'],
            s.get('cache_read', 0), s.get('cache_creation', 0),
            s.get('model')
        )
        session_id = Path(s.get('file', 'unknown')).stem
        try:
            cursor.execute('''
                INSERT INTO metrics (
                    date, session_id, input_tokens, output_tokens,
                    cache_read_tokens, cache_creation_tokens, total_tokens,
                    input_cost, output_cost, cache_cost, total_cost, model,
                    billing_source, estimated_cost
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'transcript_estimate', ?)
            ''', (
                s['date'], session_id,
                s['input'], s['output'],
                s.get('cache_read', 0), s.get('cache_creation', 0),
                s['total'],
                cost['input_cost'], cost['output_cost'], cost['cache_cost'],
                cost['total'], cost['model'],
                cost['total']
            ))
            written += 1
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()
    return written


def get_transcript_dirs():
    if not PROJECTS_DIR.exists():
        return []
    dirs = []
    for d in PROJECTS_DIR.iterdir():
        if d.is_dir():
            jsonl_files = list(d.glob('*.jsonl'))
            if jsonl_files:
                dirs.append(d)
    return dirs


def parse_transcript(filepath):
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_creation = 0
    session_date = None
    session_time = None
    model = None
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if session_date is None and 'timestamp' in msg:
                    ts = msg['timestamp']
                    try:
                        session_date = ts[:10]
                        session_time = ts[11:16] if len(ts) >= 16 else None
                    except Exception:
                        pass
                usage = msg.get('message', {}).get('usage')
                if not usage:
                    continue
                total_input += usage.get('input_tokens', 0)
                total_output += usage.get('output_tokens', 0)
                total_cache_read += usage.get('cache_read_input_tokens', 0)
                total_cache_creation += usage.get('cache_creation_input_tokens', 0)
                if model is None:
                    model = msg.get('message', {}).get('model')
    except Exception:
        pass
    if session_date is None:
        mtime = os.path.getmtime(filepath)
        dt = datetime.fromtimestamp(mtime)
        session_date = dt.strftime('%Y-%m-%d')
        session_time = dt.strftime('%H:%M')
    return session_date, session_time, total_input, total_output, total_cache_read, total_cache_creation, model


def collect_all_usage(force=False):
    if not force and CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
            if cache.get('version') == CACHE_VERSION:
                cache_time = datetime.fromisoformat(cache['updated_at'])
                if datetime.now() - cache_time < timedelta(hours=CACHE_TTL_HOURS):
                    return cache
        except Exception:
            pass

    sessions = []
    daily = defaultdict(lambda: {'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0})
    monthly = defaultdict(lambda: {'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0})

    for proj_dir in get_transcript_dirs():
        for jsonl_file in proj_dir.glob('*.jsonl'):
            size = jsonl_file.stat().st_size
            if size == 0 or size > 100_000_000:
                continue
            result = parse_transcript(jsonl_file)
            s_date, s_time, s_input, s_output, s_cache_read, s_cache_creation, s_model = result
            if s_input + s_output + s_cache_read + s_cache_creation == 0:
                continue
            sessions.append({
                'date': s_date, 'time': s_time or '', 'file': str(jsonl_file),
                'input': s_input, 'output': s_output,
                'cache_read': s_cache_read, 'cache_creation': s_cache_creation,
                'cache_total': s_cache_read + s_cache_creation,
                'total': s_input + s_output + s_cache_read + s_cache_creation,
                'model': s_model,
            })
            daily[s_date]['input'] += s_input
            daily[s_date]['output'] += s_output
            daily[s_date]['cache_read'] += s_cache_read
            daily[s_date]['cache_creation'] += s_cache_creation
            daily[s_date]['sessions'] += 1
            month_key = s_date[:7]
            monthly[month_key]['input'] += s_input
            monthly[month_key]['output'] += s_output
            monthly[month_key]['cache_read'] += s_cache_read
            monthly[month_key]['cache_creation'] += s_cache_creation
            monthly[month_key]['sessions'] += 1

    sessions.sort(key=lambda s: s['date'] + s.get('time', ''), reverse=True)
    cache_data = {
        'version': CACHE_VERSION,
        'updated_at': datetime.now().isoformat(),
        'sessions': sessions,
        'daily': {k: dict(v) for k, v in sorted(daily.items(), reverse=True)},
        'monthly': {k: dict(v) for k, v in sorted(monthly.items(), reverse=True)},
    }
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass
    try:
        sync_cache_to_db(cache_data)
    except Exception:
        pass
    return cache_data


def get_current_session_id():
    current_proj = Path.cwd()
    # 向上查找匹配的 project dir（CWD 可能在子目录中）
    for _ in range(5):
        proj_key = str(current_proj).replace(':', '-').replace('\\', '-').replace('.', '-')
        proj_dir = PROJECTS_DIR / proj_key
        if proj_dir.exists():
            jsonl_files = sorted(proj_dir.glob('*.jsonl'),
                               key=lambda f: f.stat().st_mtime, reverse=True)
            if jsonl_files:
                return jsonl_files[0]
        current_proj = current_proj.parent
    return None


def get_session_bar(value, max_value, width=20):
    filled = int(value / max_value * width) if max_value > 0 else 1
    return f'{"█" * filled}{"░" * (width - filled)}'


def get_ascii_bar(value, max_value, width=10):
    """ASCII progress bar: [#####-----] no unicode, no ANSI."""
    filled = int(value / max_value * width) if max_value > 0 else 0
    filled = min(filled, width)
    return f"[{'#' * filled}{'-' * (width - filled)}]"


def make_rich_bar(value, max_value, width=15):
    """Rich-markup progress bar: ████░░░░ with color by ratio."""
    if max_value <= 0:
        max_value = 1
    ratio = value / max_value
    filled = min(int(ratio * width), width)
    bar = "█" * filled + "░" * (width - filled)
    if ratio > 0.8:
        return f"[red]{bar}[/red]"
    elif ratio > 0.4:
        return f"[yellow]{bar}[/yellow]"
    else:
        return f"[dim]{bar}[/dim]"


def get_cache_status(rate):
    if rate >= 90:
        return '\U0001f7e2 优秀', ANSI_GREEN
    elif rate >= 70:
        return '\U0001f7e1 正常', ANSI_YELLOW
    else:
        return '\U0001f534 偏低', ANSI_RED


def detect_anomalies(sessions, large_threshold=10_000_000):
    results = []
    for s in sessions:
        tags = []
        if s['total'] > large_threshold:
            tags.append('large')
        input_like = s['input'] + s.get('cache_creation', 0) + s.get('cache_read', 0)
        s_cache_rate = (s.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        if s_cache_rate < 30 and input_like > 1_000_000:
            tags.append('low_cache')
        if tags:
            results.append((s, tags))
    return results


def generate_suggestions(cache_hit_rate, today_tokens, recent_sessions, month_sessions, mode):
    suggestions = []
    if cache_hit_rate >= 90:
        suggestions.append(('good', '上下文复用良好，Cache 命中率优秀'))
    elif cache_hit_rate < 70:
        suggestions.append(('warn', 'Cache 命中率偏低 —— 可能频繁新开会话或上下文变化过大'))

    anomalies = detect_anomalies(recent_sessions[:10])
    large_count = sum(1 for _, tags in anomalies if 'large' in tags)
    lowc_count = sum(1 for _, tags in anomalies if 'low_cache' in tags)
    if large_count > 0:
        suggestions.append(('warn', f'最近 {large_count} 个 Session 超过 10M tokens,建议检查任务拆分'))
    if lowc_count > 0:
        suggestions.append(('warn', f'最近 {lowc_count} 个 Session Cache 命中率 <30%,新会话开销较大'))
    if today_tokens > 100_000_000:
        suggestions.append(('warn', '今日用量较高 (>100M),建议检查是否有异常大 Session'))
    if month_sessions > 100:
        suggestions.append(('info', f'本月已开 {month_sessions} 个 Session,频繁新开会话会降低 Cache 利用率'))

    if not suggestions:
        suggestions.append(('good', '各项指标正常'))
    return suggestions


# ══════════════════════════════════════════════════════════
#  紧凑 ASCII 仪表盘（默认输出）
# ══════════════════════════════════════════════════════════

def build_dashboard_data(cache, billing_ctx=None):
    """构建仪表盘所需数据，返回 dict。"""
    today_str = date.today().isoformat()
    this_month = today_str[:7]
    today = date.today()

    month_total_in = month_total_out = month_total_cr = month_total_cc = month_sessions = 0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            month_total_in += m_data['input']
            month_total_out += m_data['output']
            month_total_cr += m_data.get('cache_read', 0)
            month_total_cc += m_data.get('cache_creation', 0)
            month_sessions += m_data['sessions']

    month_total_tokens = month_total_in + month_total_out + month_total_cr + month_total_cc
    month_input_like = month_total_in + month_total_cc + month_total_cr
    cache_hit_rate = (month_total_cr / month_input_like * 100 if month_input_like > 0 else 0)

    est_cost = calculate_cost(month_total_in, month_total_out, month_total_cr, month_total_cc)
    raw_est_month = est_cost['total']

    if billing_ctx is None:
        billing_ctx = {
            'mode': 'RAW_ESTIMATE', 'display_cost': {'month': raw_est_month, 'today': 0},
            'raw_cost': raw_est_month, 'calibration': None, 'official_info': None,
        }

    mode = billing_ctx['mode']
    display_cost = billing_ctx['display_cost']
    cal = billing_ctx.get('calibration')
    off_info = billing_ctx.get('official_info')

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    month_cost = display_cost.get('month', raw_est_month)
    daily_avg = month_cost / days_elapsed if days_elapsed > 0 else 0
    eom_prediction = (month_cost / days_elapsed * days_in_month) if days_elapsed > 0 else 0

    current_file = get_current_session_id()
    s_in = s_out = s_cr = s_cc = 0
    if current_file:
        _, _, s_in, s_out, s_cr, s_cc, _ = parse_transcript(current_file)
    s_total = s_in + s_out + s_cr + s_cc

    today_data = cache['daily'].get(today_str, {
        'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0
    })
    t_est_total = (today_data['input'] + today_data['output']
                   + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))
    if s_total > t_est_total:
        t_est_total = s_total

    recent_5 = cache['sessions'][:5]
    suggestions = generate_suggestions(cache_hit_rate, t_est_total, recent_5, month_sessions, mode)

    deviation = None
    if mode == 'OFFICIAL_CSV' and off_info and off_info['month_cost'] > 0:
        deviation = raw_est_month / off_info['month_cost']

    return {
        'model': est_cost['model'], 'mode': mode, 'month_key': this_month,
        'pricing': est_cost['pricing'],
        'month_cost': month_cost, 'daily_avg': daily_avg, 'eom_prediction': eom_prediction,
        'raw_est_month': raw_est_month, 'today_cost': display_cost.get('today', 0),
        'deviation': deviation,
        'input_cost': est_cost['input_cost'], 'output_cost': est_cost['output_cost'],
        'cache_cost': est_cost['cache_cost'],
        'session_total': s_total, 'today_total': t_est_total, 'month_total': month_total_tokens,
        'cache_hit_rate': cache_hit_rate,
        'calibration': cal, 'recent_5': recent_5, 'suggestions': suggestions,
        'daily_budget': DAILY_BUDGET, 'monthly_budget': MONTHLY_BUDGET,
        'over_daily': display_cost.get('today', 0) > DAILY_BUDGET,
        'over_monthly': eom_prediction > MONTHLY_BUDGET,
    }


def render_compact_dashboard(data) -> str:
    """Render compact single-block dashboard — ASCII only, no ANSI, no markdown tables."""
    lines = []
    W = 68

    # Cache status
    cache_rate = data['cache_hit_rate']
    if cache_rate >= 90:
        cache_status = "优秀"
    elif cache_rate >= 70:
        cache_status = "正常"
    else:
        cache_status = "偏低"

    # ── Header ──
    lines.append(f"Token 仪表盘 · {data['month_key']}    {data['model']}    口径: {data['mode']}")
    lines.append("─" * W)

    # ── 1. 费用概览 ──
    if data['mode'] == 'OFFICIAL_CSV':
        lines.append(f"费用  官方账单 ¥{data['month_cost']:.2f}  |  日均 ¥{data['daily_avg']:.2f}  |  月末预测 ¥{data['eom_prediction']:.2f}")
    elif data['mode'] == 'CALIBRATED_ESTIMATE':
        lines.append(f"费用  校准估算 ¥{data['month_cost']:.2f}  |  日均 ¥{data['daily_avg']:.2f}  |  月末预测 ¥{data['eom_prediction']:.2f}")
    else:
        lines.append(f"费用  原始估算 ¥{data['raw_est_month']:.2f}  |  日均 ¥{data['daily_avg']:.2f}  |  月末预测 ¥{data['eom_prediction']:.2f}")
    if data['mode'] == 'OFFICIAL_CSV' and data['deviation'] is not None:
        lines.append(f"      原始估算 ¥{data['raw_est_month']:.2f}  |  偏差 {data['deviation']:.1f}x")

    # ── 2. Token 概览 ──
    lines.append(f"Token  本次 {format_tokens(data['session_total']):>8}  |  今日 {format_tokens(data['today_total']):>8}  |  本月 {format_tokens(data['month_total']):>8}")

    # ── 3. Cache 状态 ──
    lines.append(f"Cache  {cache_status}  {cache_rate:.1f}%")

    # ── 4. 费用拆分 ──
    p = data['pricing']
    lines.append(f"拆分  Input ¥{data['input_cost']:.2f}  |  Output ¥{data['output_cost']:.2f}  |  Cache ¥{data['cache_cost']:.2f}  (¥/M: I={p['input']} O={p['output']} C={p['cache_hit']})")

    # ── 5. 校准详情 ──
    cal = data['calibration']
    if cal:
        alpha_str = f"{cal['alpha']:.2f}" if cal.get('alpha') else f"{get_ema_alpha(cal['samples']):.2f}"
        last_ratio = cal.get('ratio') or cal.get('last_ratio') or 0
        calibrated = data['raw_est_month'] * cal['factor']
        lines.append(f"校准  因子 {cal['factor']:.4f}  |  样本 {cal['samples']}  |  EMA a={alpha_str}  |  ratio {last_ratio:.4f}  |  校准后 ¥{calibrated:.2f}")

    # ── 6. 最近 5 个 Session ──
    lines.append("─" * W)
    lines.append("最近 5 个 Session")
    max_total = max(s_['total'] for s_ in data['recent_5']) if data['recent_5'] else 1
    for s_ in data['recent_5']:
        total = s_['total']
        input_like = s_['input'] + s_.get('cache_creation', 0) + s_.get('cache_read', 0)
        s_cache_rate = (s_.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        bar = get_ascii_bar(total, max_total)
        time_part = f" {s_.get('time', '')}" if s_.get('time') else ''
        date_part = s_['date'][5:]

        flags = ''
        if total > 10_000_000:
            flags += ' !!'
        if s_cache_rate < 30 and input_like > 1_000_000:
            flags += ' LOW'

        lines.append(f"  {date_part}{time_part}  {format_tokens(total):>8}  {bar}  c{s_cache_rate:.0f}%{flags}")

    # ── 7. 今日建议 ──
    lines.append("─" * W)
    for level, text in data['suggestions']:
        if level == 'good':
            lines.append(f"  [OK] {text}")
        elif level == 'warn':
            lines.append(f"  [!!] {text}")
        else:
            lines.append(f"  [--] {text}")

    if data['over_daily']:
        lines.append(f"  [!!] 今日费用 ¥{data['today_cost']:.2f} 超出日预算 ¥{data['daily_budget']:.2f}")

    lines.append("─" * W)
    return "\n".join(lines)


def render_rich_dashboard(data):
    """Rich single-block dashboard — fixed width, colored bars, aligned columns."""
    from rich.console import Group

    W = 70

    # Cache status
    cache_rate = data['cache_hit_rate']
    if cache_rate >= 90:
        cache_dot = "[green]●[/green]"
    elif cache_rate >= 70:
        cache_dot = "[yellow]●[/yellow]"
    else:
        cache_dot = "[red]●[/red]"

    lines = []

    # Header
    lines.append(f"[bold]Token 仪表盘 · {data['month_key']}[/bold]")
    lines.append(f"[dim]{data['model']}                            口径: {data['mode']}[/dim]")
    lines.append("")

    # 1. 费用概览
    lines.append("[bold]费用概览[/bold]")
    if data['mode'] == 'OFFICIAL_CSV':
        lines.append(f"  官方账单 ¥{data['month_cost']:.2f}    日均 ¥{data['daily_avg']:.2f}    月末预测 ¥{data['eom_prediction']:.2f}")
    elif data['mode'] == 'CALIBRATED_ESTIMATE':
        lines.append(f"  校准估算 ¥{data['month_cost']:.2f}    日均 ¥{data['daily_avg']:.2f}    月末预测 ¥{data['eom_prediction']:.2f}")
    else:
        lines.append(f"  原始估算 ¥{data['raw_est_month']:.2f}    日均 ¥{data['daily_avg']:.2f}    月末预测 ¥{data['eom_prediction']:.2f}")
    if data['mode'] == 'OFFICIAL_CSV' and data['deviation'] is not None:
        lines.append(f"  原始估算 ¥{data['raw_est_month']:.2f}    偏差 [yellow]{data['deviation']:.1f}x[/yellow]")
    lines.append("")

    # 2. Token 概览
    lines.append("[bold]Token 概览[/bold]")
    lines.append(f"  本次 {format_tokens(data['session_total']):>8}    今日 {format_tokens(data['today_total']):>8}    本月 {format_tokens(data['month_total']):>8}")
    lines.append("")

    # 3. Cache 状态
    lines.append("[bold]Cache 状态[/bold]")
    lines.append(f"  {cache_dot} {cache_rate:.1f}%")
    lines.append("")

    # 4. 费用拆分
    p = data['pricing']
    lines.append("[bold]费用拆分（估算）[/bold]")
    lines.append(f"  Input ¥{data['input_cost']:.2f}    Output ¥{data['output_cost']:.2f}    Cache ¥{data['cache_cost']:.2f}")
    lines.append(f"  [dim]@¥/M: I={p['input']} O={p['output']} C={p['cache_hit']}[/dim]")
    lines.append("")

    # 5. 校准详情
    cal = data['calibration']
    if cal:
        alpha_str = f"{cal['alpha']:.2f}" if cal.get('alpha') else f"{get_ema_alpha(cal['samples']):.2f}"
        last_ratio = cal.get('ratio') or cal.get('last_ratio') or 0
        calibrated = data['raw_est_month'] * cal['factor']
        lines.append("[bold]校准详情[/bold]")
        lines.append(f"  因子 [bold]{cal['factor']:.4f}[/bold]    样本 {cal['samples']}    EMA α={alpha_str}    ratio {last_ratio:.4f}")
        lines.append(f"  校准后估算 [bold]¥{calibrated:.2f}[/bold]  =  {data['raw_est_month']:.2f} x {cal['factor']:.4f}")
        lines.append("")

    # 6. 最近 5 个 Session — fixed column layout
    lines.append("[bold]最近 5 个 Session[/bold]")
    max_total = max(s_['total'] for s_ in data['recent_5']) if data['recent_5'] else 1
    for s_ in data['recent_5']:
        total = s_['total']
        input_like = s_['input'] + s_.get('cache_creation', 0) + s_.get('cache_read', 0)
        s_cache_rate = (s_.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        bar = make_rich_bar(total, max_total)
        time_part = f" {s_.get('time', '')}" if s_.get('time') else ''
        label = (s_['date'][5:] + time_part).ljust(14)
        tok_str = format_tokens(total).rjust(8)

        flags = ""
        if total > 10_000_000:
            flags += " [red]!![/red]"
        if s_cache_rate < 30 and input_like > 1_000_000:
            flags += " [yellow]LOW[/yellow]"

        lines.append(f"  {label}{tok_str}  {bar}  c{s_cache_rate:.0f}%{flags}")
    lines.append("")

    # 7. 今日建议
    lines.append("[bold]今日建议[/bold]")
    for level, text in data['suggestions']:
        if level == 'good':
            lines.append(f"  [green]\\[OK][/green] {text}")
        elif level == 'warn':
            lines.append(f"  [yellow]\\[!!][/yellow] {text}")
        else:
            lines.append(f"  [dim]\\[--][/dim] {text}")

    if data['over_daily']:
        lines.append(f"  [yellow]\\[!!][/yellow] 今日费用 ¥{data['today_cost']:.2f} 超出日预算 ¥{data['daily_budget']:.2f}")

    # ── Wrap in Panel ──
    content = Group(*[Text.from_markup(line) for line in lines])
    panel = Panel(
        content,
        width=W,
        padding=(1, 2),
        border_style="cyan",
        box=ROUNDED,
    )
    console.print(panel)


# ══════════════════════════════════════════════════════════
#  显示（--rich 旧格式）
# ══════════════════════════════════════════════════════════

def display_full(cache, detail=False, billing_ctx=None):
    """billing_ctx = {mode, display_cost, raw_cost, calibration, official_info}"""
    today_str = date.today().isoformat()
    this_month = today_str[:7]
    today = date.today()

    # ── 聚合 transcript 月数据 ──
    month_total_in = month_total_out = month_total_cr = month_total_cc = month_sessions = 0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            month_total_in += m_data['input']
            month_total_out += m_data['output']
            month_total_cr += m_data.get('cache_read', 0)
            month_total_cc += m_data.get('cache_creation', 0)
            month_sessions += m_data['sessions']

    month_total_tokens = month_total_in + month_total_out + month_total_cr + month_total_cc
    month_input_like = month_total_in + month_total_cc + month_total_cr
    cache_hit_rate = (month_total_cr / month_input_like * 100 if month_input_like > 0 else 0)

    est_cost = calculate_cost(month_total_in, month_total_out, month_total_cr, month_total_cc)
    raw_est_month = est_cost['total']

    # ── 计费上下文 ──
    if billing_ctx is None:
        billing_ctx = {'mode': 'RAW_ESTIMATE', 'display_cost': {'month': raw_est_month, 'today': 0},
                       'raw_cost': raw_est_month, 'calibration': None, 'official_info': None}

    mode = billing_ctx['mode']
    display_cost = billing_ctx['display_cost']
    cal = billing_ctx.get('calibration')
    off_info = billing_ctx.get('official_info')

    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    month_cost = display_cost.get('month', raw_est_month)
    daily_avg = month_cost / days_elapsed if days_elapsed > 0 else 0
    eom_prediction = (month_cost / days_elapsed * days_in_month) if days_elapsed > 0 else 0

    # ── 当前 session ──
    current_file = get_current_session_id()
    s_in = s_out = s_cr = s_cc = 0
    if current_file:
        _, _, s_in, s_out, s_cr, s_cc, _ = parse_transcript(current_file)
    s_total = s_in + s_out + s_cr + s_cc

    # ── 今日 ──
    today_data = cache['daily'].get(today_str, {'input': 0, 'output': 0, 'cache_read': 0, 'cache_creation': 0, 'sessions': 0})
    t_est_total = (today_data['input'] + today_data['output']
                   + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))
    t_sessions = today_data['sessions']

    # ── 历史 ──
    all_in = sum(s_['input'] for s_ in cache['sessions'])
    all_out = sum(s_['output'] for s_ in cache['sessions'])
    all_cr = sum(s_.get('cache_read', 0) for s_ in cache['sessions'])
    all_cc = sum(s_.get('cache_creation', 0) for s_ in cache['sessions'])
    all_total = all_in + all_out + all_cr + all_cc
    all_sessions = len(cache['sessions'])

    # ── 状态 ──
    cache_status, cache_color = get_cache_status(cache_hit_rate)
    recent_5 = cache['sessions'][:5]
    suggestions = generate_suggestions(cache_hit_rate, t_est_total, recent_5, month_sessions, mode)

    # ── 色彩 ──
    C, R, B, D, G, Y = ANSI_CYAN, ANSI_RESET, ANSI_BOLD, ANSI_DIM, ANSI_GREEN, ANSI_YELLOW
    eom_color = ANSI_RED if eom_prediction > MONTHLY_BUDGET else ''
    eom_reset = ANSI_RESET if eom_prediction > MONTHLY_BUDGET else ''

    W = 70

    def strip_ansi(text):
        result = ''
        i = 0
        while i < len(text):
            if text[i] == '\033' and i + 1 < len(text) and text[i + 1] == '[':
                i += 2
                while i < len(text) and text[i] not in 'mHJABCDEFGKSThlfsu':
                    i += 1
                i += 1
            else:
                result += text[i]
                i += 1
        return result

    def panel_line(content=''):
        pad = max(0, W - 4 - len(strip_ansi(content)))
        print(f"{C}│{R} {content}{' ' * pad} {C}│{R}")

    def panel_sep():
        print(f"{C}├{'─' * (W - 2)}┤{R}")

    # Header
    print(f"\n{C}╭{'─' * (W - 2)}╮{R}")
    panel_line(f"{B}Token 仪表盘 · {this_month}{R}    {D}{est_cost['model']}{R}    {D}口径: {mode}{R}")
    panel_sep()

    # 1. 费用概览
    panel_line(f"{B}费用概览{R}")
    if mode == 'OFFICIAL_CSV':
        panel_line(f"  官方账单  {B}¥{month_cost:.2f}{R}  |  日均 ¥{daily_avg:.2f}  |  月末预测 {eom_color}¥{eom_prediction:.2f}{eom_reset}")
        if detail:
            panel_line(f"  {D}({days_elapsed}/{days_in_month} 天, 官方 {off_info['days_active'] if off_info else '?'} 天有记录){R}")
    elif mode == 'CALIBRATED_ESTIMATE':
        panel_line(f"  校准估算  {B}¥{month_cost:.2f}{R}  |  日均 ¥{daily_avg:.2f}  |  月末预测 {eom_color}¥{eom_prediction:.2f}{eom_reset}")
        if cal:
            panel_line(f"  因子 {Y}{cal['factor']:.4f}{R}  x  原始 ¥{raw_est_month:.2f}  =  校准后 ¥{month_cost:.2f}")
    else:
        panel_line(f"  原始估算  {B}¥{raw_est_month:.2f}{R}  |  日均 ¥{daily_avg:.2f}  |  月末预测 {eom_color}¥{eom_prediction:.2f}{eom_reset}")
        panel_line(f"  {Y}费用仅供趋势参考，非真实计费{R}")

    # 官方/原始对比行
    if mode == 'OFFICIAL_CSV' and off_info:
        deviation = (raw_est_month / off_info['month_cost']) if off_info['month_cost'] > 0 else 0
        panel_line(f"  原始估算  {D}¥{raw_est_month:.2f}{R}  |  偏差 {Y}{deviation:.1f}x{R}")
    panel_line()

    # 2. Token 概览
    panel_line(f"{B}Token 概览{R}")
    panel_line(f"  本次 {format_tokens(s_total):>8}  |  今日 {format_tokens(t_est_total):>8}  |  本月 {format_tokens(month_total_tokens):>8}")
    if detail:
        panel_line(f"  输入 {format_tokens(month_total_in):>8}  |  输出 {format_tokens(month_total_out):>8}  |  Cache {format_tokens(month_total_cr + month_total_cc):>8}")
        panel_line(f"  历史 {format_tokens(all_total):>8}  |  {all_sessions} Sessions")
    panel_line()

    # 3. Cache 状态
    panel_line(f"{B}Cache 状态{R}      {cache_color}{cache_status}  {cache_hit_rate:.1f}%{R}")
    if detail:
        panel_line(f"  Cache Read  {format_tokens(month_total_cr):>8}    命中率基数  {format_tokens(month_input_like):>8}")
    panel_line()

    # 4. 费用拆分 (估算)
    p = est_cost['pricing']
    panel_line(f"{B}费用拆分 (估算){R}  {D}(@¥/M: I={p['input']} O={p['output']} C={p['cache_hit']}){R}")
    panel_line(f"  Input {B}¥{est_cost['input_cost']:.2f}{R}  |  Output {B}¥{est_cost['output_cost']:.2f}{R}  |  Cache {B}¥{est_cost['cache_cost']:.2f}{R}")
    if detail:
        panel_line(f"  {D}Input:  {format_tokens(month_total_in + month_total_cc):>8} x ¥{p['input']}/M   = ¥{est_cost['input_cost']:.2f}{R}")
        panel_line(f"  {D}Output: {format_tokens(month_total_out):>8} x ¥{p['output']}/M  = ¥{est_cost['output_cost']:.2f}{R}")
        panel_line(f"  {D}Cache:  {format_tokens(month_total_cr):>8} x ¥{p['cache_hit']}/M = ¥{est_cost['cache_cost']:.2f}{R}")
    panel_line()

    # 5. 校准详情
    if cal:
        panel_line(f"{B}校准详情{R}")
        alpha_str = f"{cal['alpha']:.2f}" if cal.get('alpha') else f"{get_ema_alpha(cal['samples']):.2f}"
        last_ratio = cal.get('ratio') or cal.get('last_ratio') or 0
        panel_line(f"  因子 {B}{cal['factor']:.4f}{R}  |  样本 {cal['samples']}  |  EMA alpha {alpha_str}  |  最新 ratio {last_ratio:.4f}")
        panel_line(f"  校准后估算  {raw_est_month * cal['factor']:.2f}  =  {D}{raw_est_month:.2f}{R} x {Y}{cal['factor']:.4f}{R}")
        panel_line()

    # 6. 最近 5 个 Session
    panel_line(f"{B}最近 5 个 Session{R}")
    max_total = max(s_['total'] for s_ in recent_5) if recent_5 else 1
    for s_ in recent_5:
        total = s_['total']
        input_like = s_['input'] + s_.get('cache_creation', 0) + s_.get('cache_read', 0)
        s_cache_rate = (s_.get('cache_read', 0) / input_like * 100 if input_like > 0 else 0)
        bar = get_session_bar(total, max_total)
        time_part = f" {s_.get('time', '')}" if s_.get('time') else ''
        date_part = s_['date'][5:]

        is_large = total > 10_000_000
        is_low_cache = s_cache_rate < 30 and input_like > 1_000_000
        flags = ''
        if is_large:
            flags += f' {ANSI_RED}!!{ANSI_RESET}'
        if is_low_cache:
            flags += f' {ANSI_YELLOW}c{ANSI_RESET}'

        if is_large:
            entry = f"  {ANSI_RED}{date_part}{time_part}  {format_tokens(total):>8}  {bar}  c{s_cache_rate:.0f}%{flags}{ANSI_RESET}"
        else:
            entry = f"  {date_part}{time_part}  {format_tokens(total):>8}  {bar}  c{s_cache_rate:.0f}%{flags}"
        panel_line(entry)
        if detail:
            panel_line(f"  {D}In:{format_tokens(s_['input']):>7} Out:{format_tokens(s_['output']):>7} CR:{format_tokens(s_.get('cache_read', 0)):>7} CC:{format_tokens(s_.get('cache_creation', 0)):>7}{R}")
    panel_line()

    # 7. 今日建议
    panel_line(f"{B}今日建议{R}")
    for level, text in suggestions:
        if level == 'good':
            icon = f'{ANSI_GREEN}OK{ANSI_RESET}'
        elif level == 'warn':
            icon = f'{ANSI_YELLOW}!!{ANSI_RESET}'
        else:
            icon = f'{C}--{R}'
        panel_line(f"  [{icon}] {text}")
    panel_line()

    print(f"{C}╰{'─' * (W - 2)}╯{R}\n")


def output_json(cache):
    today_str = date.today().isoformat()
    this_month = today_str[:7]
    today = date.today()

    current_file = get_current_session_id()
    session_data = None
    if current_file:
        result = parse_transcript(current_file)
        s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
        s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
        session_data = {'input': s_in, 'output': s_out, 'cache_read': s_cr, 'cache_creation': s_cc,
                        'total': s_in + s_out + s_cr + s_cc, 'model': s_model, 'cost': s_cost}

    today_data = cache['daily'].get(today_str, {})
    today_tokens = (today_data.get('input', 0) + today_data.get('output', 0)
                    + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))

    month_total_in = month_total_out = month_total_cr = month_total_cc = month_sessions = 0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            month_total_in += m_data['input']
            month_total_out += m_data['output']
            month_total_cr += m_data.get('cache_read', 0)
            month_total_cc += m_data.get('cache_creation', 0)
            month_sessions += m_data['sessions']

    month_cost = calculate_cost(month_total_in, month_total_out, month_total_cr, month_total_cc)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day
    eom_prediction = (month_cost['total'] / days_elapsed * days_in_month) if days_elapsed > 0 else 0

    result = {
        'session': session_data,
        'today': {'input': today_data.get('input', 0), 'output': today_data.get('output', 0),
                  'cache_read': today_data.get('cache_read', 0), 'cache_creation': today_data.get('cache_creation', 0),
                  'total': today_tokens, 'sessions': today_data.get('sessions', 0)},
        'month': {'key': this_month, 'input': month_total_in, 'output': month_total_out,
                  'cache_read': month_total_cr, 'cache_creation': month_total_cc,
                  'total': month_total_in + month_total_out + month_total_cr + month_total_cc,
                  'sessions': month_sessions, 'cost': month_cost, 'eom_prediction': eom_prediction,
                  'days_elapsed': days_elapsed, 'days_in_month': days_in_month},
        'all_time': {'sessions': len(cache['sessions']), 'total': sum(s['total'] for s in cache['sessions'])},
        'updated_at': cache['updated_at'],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ══════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════

def resolve_billing_context(raw_est_month_cost, cache):
    """根据官方 CSV 和校准因子决定最终计费口径。"""
    amount_path, cost_path = find_billing_csvs()
    billing_data = None
    cal_result = None

    if amount_path and cost_path:
        billing_data = load_official_billing(amount_path, cost_path, exclude_api_keys=EXCLUDE_API_KEYS)
        if billing_data:
            # 尝试更新 EMA（首次导入或换文件时生效）
            cal_result = update_ema_calibration(amount_path, cost_path, raw_est_month_cost, billing_data)

    # 如果 CSV 存在且覆盖当月，始终以 OFFICIAL_CSV 为准
    this_month = date.today().strftime('%Y-%m')
    if billing_data:
        official = aggregate_official(billing_data, this_month)
        if official and official['month_cost'] > 0:
            return {
                'mode': 'OFFICIAL_CSV',
                'display_cost': {'month': official['month_cost'], 'today': official['today_cost']},
                'raw_cost': raw_est_month_cost,
                'calibration': cal_result or get_latest_calibration(),
                'official_info': official,
                'breaker_eom': _compute_eom(official['month_cost']),
            }

    # 无官方 CSV，尝试用历史校准因子
    cal = get_latest_calibration()
    if cal and cal['factor'] > 0:
        calibrated_month = raw_est_month_cost * cal['factor']
        return {
            'mode': 'CALIBRATED_ESTIMATE',
            'display_cost': {'month': calibrated_month, 'today': 0},
            'raw_cost': raw_est_month_cost,
            'calibration': cal,
            'official_info': None,
            'breaker_eom': _compute_eom(calibrated_month),
        }

    # 无任何校准
    return {
        'mode': 'RAW_ESTIMATE',
        'display_cost': {'month': raw_est_month_cost, 'today': 0},
        'raw_cost': raw_est_month_cost,
        'calibration': None,
        'official_info': None,
        'breaker_eom': None,
    }


def _compute_eom(month_cost):
    now = datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    current_day = now.day
    return (month_cost / current_day * days_in_month) if current_day > 0 else 0.0


def main():
    force_update = '--update-cache' in sys.argv or '--force' in sys.argv

    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return

    init_db()
    cache = collect_all_usage(force=force_update)

    # 计算原始估算月费
    this_month = date.today().strftime('%Y-%m')
    raw_est_month = 0.0
    for m_key, m_data in cache['monthly'].items():
        if m_key == this_month:
            c = calculate_cost(m_data['input'], m_data['output'],
                              m_data.get('cache_read', 0), m_data.get('cache_creation', 0))
            raw_est_month += c['total']

    # 解析计费上下文
    billing_ctx = resolve_billing_context(raw_est_month, cache)

    # 同步每日快照
    if billing_ctx.get('official_info'):
        try:
            sync_billing_daily(billing_ctx['official_info'], raw_est_month,
                             billing_ctx.get('calibration', {}).get('factor', 0))
        except Exception:
            pass

    # 预算预警
    eom = billing_ctx.get('breaker_eom')
    if eom is None:
        days_in_month = calendar.monthrange(date.today().year, date.today().month)[1]
        days_elapsed = date.today().day
        eom = (billing_ctx['display_cost']['month'] / days_elapsed * days_in_month) if days_elapsed > 0 else 0

    run_alerts(billing_ctx['mode'], billing_ctx['display_cost'], eom)

    # 路由
    if '--json' in sys.argv:
        output_json(cache)
        return

    if '--session' in sys.argv:
        current_file = get_current_session_id()
        if current_file:
            result = parse_transcript(current_file)
            s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
            s_total = s_in + s_out + s_cr + s_cc
            s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
            print(f'输入: {format_tokens(s_in)}  |  输出: {format_tokens(s_out)}')
            print(f'Cache read: {format_tokens(s_cr)}  |  Cache write: {format_tokens(s_cc)}')
            print(f'合计: {format_tokens(s_total)}')
            print(f'费用: ¥ {s_cost["total"]:.4f}')
            save_session_to_db({
                'session_id': current_file.stem,
                'input_tokens': s_in, 'output_tokens': s_out,
                'cache_read_tokens': s_cr, 'cache_creation_tokens': s_cc,
                'total_tokens': s_total,
                'input_cost': s_cost['input_cost'], 'output_cost': s_cost['output_cost'],
                'cache_cost': s_cost['cache_cost'], 'total_cost': s_cost['total'],
                'model': s_cost['model']
            })
        else:
            print('无当前 session 数据')
        return

    if '--today' in sys.argv:
        today_str = date.today().isoformat()
        today_data = cache['daily'].get(today_str, {})
        t_total = (today_data.get('input', 0) + today_data.get('output', 0)
                   + today_data.get('cache_read', 0) + today_data.get('cache_creation', 0))
        print(f'{today_str}: {format_tokens(t_total)}  ({today_data.get("sessions", 0)} sessions)')
        return

    if '--month' in sys.argv:
        m_in = m_out = m_cr = m_cc = m_sessions = 0
        for m_key, m_data in cache['monthly'].items():
            if m_key == this_month:
                m_in += m_data['input']
                m_out += m_data['output']
                m_cr += m_data.get('cache_read', 0)
                m_cc += m_data.get('cache_creation', 0)
                m_sessions += m_data['sessions']
        m_total = m_in + m_out + m_cr + m_cc
        m_cost = calculate_cost(m_in, m_out, m_cr, m_cc)
        print(f'{this_month}: {format_tokens(m_total)}  ({m_sessions} sessions)')
        print(f'费用(估算): ¥ {m_cost["total"]:.2f}')
        return

    detail = '--detail' in sys.argv
    use_rich = '--rich' in sys.argv
    use_compact = '--compact' in sys.argv

    data = build_dashboard_data(cache, billing_ctx)

    if use_compact:
        text = render_compact_dashboard(data)
        print(text)
        txt_path = Path(__file__).resolve().parent / 'token_dashboard.txt'
        try:
            txt_path.write_text(text, encoding='utf-8')
        except Exception:
            pass
    elif use_rich:
        display_full(cache, detail=detail, billing_ctx=billing_ctx)
    else:
        render_rich_dashboard(data)

    # 持久化当前 session
    current_file = get_current_session_id()
    if current_file:
        result = parse_transcript(current_file)
        s_date, s_time, s_in, s_out, s_cr, s_cc, s_model = result
        if s_in + s_out + s_cr + s_cc > 0:
            s_cost = calculate_cost(s_in, s_out, s_cr, s_cc, s_model)
            save_session_to_db({
                'session_id': current_file.stem,
                'input_tokens': s_in, 'output_tokens': s_out,
                'cache_read_tokens': s_cr, 'cache_creation_tokens': s_cc,
                'total_tokens': s_in + s_out + s_cr + s_cc,
                'input_cost': s_cost['input_cost'],
                'output_cost': s_cost['output_cost'],
                'cache_cost': s_cost['cache_cost'],
                'total_cost': s_cost['total'],
                'model': s_cost['model']
            })


if __name__ == '__main__':
    main()
