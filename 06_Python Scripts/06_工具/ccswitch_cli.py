#!/usr/bin/env python3
"""
ccswitch - cc-switch GUI 的命令行控制工具

用法：
    ccswitch list [app]          列出所有 provider（可筛选 app 类型）
    ccswitch use <name> [app]    切换 provider
    ccswitch current [app]       显示当前 provider
    ccswitch info <name>         显示 provider 详情
    ccswitch fix-sub             修复原生订阅失效问题（切回 Official + 清缓存）

示例：
    python ccswitch_cli.py list
    python ccswitch_cli.py list claude
    python ccswitch_cli.py use OfoxAI
    python ccswitch_cli.py use DeepSeek claude
    python ccswitch_cli.py current
    python ccswitch_cli.py current claude
    python ccswitch_cli.py info MiniMax
    python ccswitch_cli.py fix-sub

原理说明：
    cc-switch 切换第三方 Provider 时，会把 ANTHROPIC_BASE_URL 等 env 写入
    ~/.claude/settings.json。Claude Code 订阅状态检查打到第三方节点，返回
    hasAvailableSubscription=False 并缓存到 ~/.claude.json。切回 Official
    后缓存不自动清除，导致订阅持续显示失效。
    fix-sub 命令：切回 Official Provider + 清理 settings.json 中的 ANTHROPIC_*
    注入 + 重置 .claude.json 中的订阅缓存，彻底恢复原生订阅。
"""

import sys
import io
import json
import sqlite3
from pathlib import Path

# 修复 Windows 终端中文乱码
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DB_PATH = Path.home() / ".cc-switch" / "cc-switch.db"
SETTINGS_PATH = Path.home() / ".cc-switch" / "settings.json"

APP_TYPES = ["claude", "codex", "openclaw"]

SETTINGS_KEY_MAP = {
    "claude": "currentProviderClaude",
    "codex": "currentProviderCodex",
    "openclaw": "currentProviderOpenclaw",
}


def get_conn():
    if not DB_PATH.exists():
        print(f"[ERROR] 找不到数据库：{DB_PATH}", file=sys.stderr)
        sys.exit(1)
    return sqlite3.connect(str(DB_PATH))


def load_settings():
    if not SETTINGS_PATH.exists():
        return {}
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_list(app_filter=None):
    conn = get_conn()
    cur = conn.cursor()

    if app_filter:
        cur.execute(
            "SELECT id, app_type, name, is_current FROM providers WHERE app_type=? ORDER BY app_type, created_at",
            (app_filter,),
        )
    else:
        cur.execute(
            "SELECT id, app_type, name, is_current FROM providers ORDER BY app_type, created_at"
        )

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("没有找到 provider")
        return

    current_app = None
    for row in rows:
        pid, app, name, is_current = row
        if app != current_app:
            print(f"\n[{app.upper()}]")
            current_app = app
        marker = " *" if is_current else "  "
        print(f"{marker} {name:<25} id={pid[:8]}...")


def cmd_current(app_filter=None):
    conn = get_conn()
    cur = conn.cursor()

    if app_filter:
        cur.execute(
            "SELECT id, app_type, name, settings_config FROM providers WHERE app_type=? AND is_current=1",
            (app_filter,),
        )
    else:
        cur.execute(
            "SELECT id, app_type, name, settings_config FROM providers WHERE is_current=1 ORDER BY app_type"
        )

    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("没有激活的 provider")
        return

    for row in rows:
        pid, app, name, cfg_json = row
        print(f"\n[{app.upper()}] 当前 Provider: {name}")
        print(f"  ID: {pid}")
        if cfg_json:
            try:
                cfg = json.loads(cfg_json)
                env = cfg.get("env", {})
                if env:
                    base_url = env.get("ANTHROPIC_BASE_URL", env.get("base_url", ""))
                    if base_url:
                        print(f"  Base URL: {base_url}")
                    model = env.get("ANTHROPIC_MODEL", "")
                    if model:
                        print(f"  Model: {model}")
            except Exception:
                pass


def cmd_use(name, app_filter=None):
    conn = get_conn()
    cur = conn.cursor()

    # 模糊搜索（不区分大小写）
    if app_filter:
        cur.execute(
            "SELECT id, app_type, name FROM providers WHERE lower(name)=lower(?) AND app_type=?",
            (name, app_filter),
        )
    else:
        cur.execute(
            "SELECT id, app_type, name FROM providers WHERE lower(name)=lower(?)",
            (name,),
        )

    rows = cur.fetchall()

    if not rows:
        print(f"[ERROR] 未找到 provider: {name}")
        if app_filter:
            print(f"  (已过滤 app_type={app_filter})")
        conn.close()
        sys.exit(1)

    if len(rows) > 1:
        print(f"[WARN] 找到多个匹配的 provider，请指定 app 类型：")
        for r in rows:
            print(f"  {r[1]}: {r[2]}")
        conn.close()
        sys.exit(1)

    target_id, target_app, target_name = rows[0]

    # 更新数据库：同 app_type 的其他 provider 置 0，目标置 1
    cur.execute(
        "UPDATE providers SET is_current=0 WHERE app_type=?",
        (target_app,),
    )
    cur.execute(
        "UPDATE providers SET is_current=1 WHERE id=?",
        (target_id,),
    )
    conn.commit()
    conn.close()

    # 同步更新 settings.json
    settings_key = SETTINGS_KEY_MAP.get(target_app)
    if settings_key:
        settings = load_settings()
        settings[settings_key] = target_id
        save_settings(settings)
        print(f"[OK] 已切换 [{target_app.upper()}] Provider: {target_name}")
        print(f"  settings.json -> {settings_key} = {target_id[:8]}...")
    else:
        print(f"[OK] 已切换 [{target_app.upper()}] Provider: {target_name}（settings.json 无对应字段）")

    print("\n提示：如果 cc-switch 正在运行，可能需要重启才能生效。")


def cmd_info(name):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, app_type, name, is_current, category, settings_config, website_url, notes FROM providers WHERE lower(name)=lower(?)",
        (name,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"[ERROR] 未找到 provider: {name}")
        sys.exit(1)

    for row in rows:
        pid, app, pname, is_current, category, cfg_json, website, notes = row
        print(f"\n{'='*40}")
        print(f"名称：{pname}")
        print(f"App：{app}")
        print(f"ID：{pid}")
        print(f"当前激活：{'是' if is_current else '否'}")
        if category:
            print(f"分类：{category}")
        if website:
            print(f"官网：{website}")
        if notes:
            print(f"备注：{notes}")
        if cfg_json:
            try:
                cfg = json.loads(cfg_json)
                env = cfg.get("env", {})
                if env:
                    print("\n环境变量：")
                    for k, v in env.items():
                        # 隐藏 API Key 中间部分
                        if "key" in k.lower() or "token" in k.lower() or "secret" in k.lower():
                            if len(v) > 12:
                                v = v[:6] + "..." + v[-4:]
                        print(f"  {k} = {v}")
            except Exception:
                pass


CLAUDE_JSON_PATH = Path.home() / ".claude.json"
CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

# 第三方 Provider 会注入的 env keys，切回 Official 时需清除
THIRD_PARTY_ENV_KEYS = [
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_REASONING_MODEL",
]


def cmd_fix_sub():
    """修复原生订阅失效问题"""
    print("=== ccswitch fix-sub ===")
    print()

    # Step 1: 切回 Claude Official
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM providers WHERE app_type='claude' AND lower(name) LIKE '%official%'"
    )
    official = cur.fetchone()

    if not official:
        # 兜底：找 settings_config 为空的 claude provider
        cur.execute(
            "SELECT id, name FROM providers WHERE app_type='claude' AND (settings_config='{}' OR settings_config='')"
        )
        official = cur.fetchone()

    if not official:
        print("[WARN] 未找到 Claude Official provider，跳过 DB 切换")
    else:
        oid, oname = official
        cur.execute("UPDATE providers SET is_current=0 WHERE app_type='claude'")
        cur.execute("UPDATE providers SET is_current=1 WHERE id=?", (oid,))
        conn.commit()
        settings = load_settings()
        settings["currentProviderClaude"] = oid
        save_settings(settings)
        print(f"[OK] Step 1: 已切换到 [{oname}]")

    conn.close()

    # Step 2: 清除 ~/.claude/settings.json 中的第三方 env 注入
    if CLAUDE_SETTINGS_PATH.exists():
        with open(CLAUDE_SETTINGS_PATH, "r", encoding="utf-8") as f:
            cs = json.load(f)

        env = cs.get("env", {})
        removed = []
        for key in THIRD_PARTY_ENV_KEYS:
            if key in env:
                del env[key]
                removed.append(key)

        if removed:
            cs["env"] = env
            with open(CLAUDE_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(cs, f, ensure_ascii=False, indent=2)
            print(f"[OK] Step 2: 已从 settings.json 清除 {len(removed)} 个 ANTHROPIC_* env 变量")
            for k in removed:
                print(f"  - {k}")
        else:
            print("[OK] Step 2: settings.json 中无第三方 env 注入（已干净）")
    else:
        print("[SKIP] Step 2: ~/.claude/settings.json 不存在")

    # Step 3: 重置 ~/.claude.json 订阅缓存
    if CLAUDE_JSON_PATH.exists():
        with open(CLAUDE_JSON_PATH, "r", encoding="utf-8") as f:
            cj = json.load(f)

        changed = []

        if cj.get("hasAvailableSubscription") is False:
            cj["hasAvailableSubscription"] = True
            changed.append("hasAvailableSubscription: False → True")

        # 清除 clientDataCache（订阅状态缓存在里面）
        if "clientDataCache" in cj:
            del cj["clientDataCache"]
            changed.append("clientDataCache: 已删除（强制重新拉取）")

        if changed:
            with open(CLAUDE_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(cj, f, ensure_ascii=False, indent=2)
            print(f"[OK] Step 3: 已重置 .claude.json 订阅缓存：")
            for c in changed:
                print(f"  - {c}")
        else:
            print("[OK] Step 3: .claude.json 缓存已正常，无需修复")
    else:
        print("[SKIP] Step 3: ~/.claude.json 不存在")

    print()
    print("完成！请重启 Claude Code 使更改生效。")
    print("如仍有问题，尝试关闭 cc-switch GUI 再启动 Claude Code。")


def print_help():
    print(__doc__)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return

    cmd = args[0].lower().replace("-", "_")

    if cmd == "list":
        app = args[1] if len(args) > 1 else None
        cmd_list(app)

    elif cmd == "current":
        app = args[1] if len(args) > 1 else None
        cmd_current(app)

    elif cmd == "use":
        if len(args) < 2:
            print("[ERROR] 用法：ccswitch use <provider_name> [app_type]")
            sys.exit(1)
        name = args[1]
        app = args[2] if len(args) > 2 else None
        cmd_use(name, app)

    elif cmd == "info":
        if len(args) < 2:
            print("[ERROR] 用法：ccswitch info <provider_name>")
            sys.exit(1)
        cmd_info(args[1])

    elif cmd == "fix_sub":
        cmd_fix_sub()

    else:
        print(f"[ERROR] 未知命令：{cmd}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
