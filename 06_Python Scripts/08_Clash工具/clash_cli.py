#!/usr/bin/env python3
"""
Clash Verge Rev CLI Tool
通过 RESTful API 与 Mihomo 核心交互
"""

import click
import requests
import json
import sys
import os
from pathlib import Path

# 配置 - Clash Verge Rev
CLASH_API = "http://127.0.0.1:9097"
CLASH_SECRET = "set-your-secret"
CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "io.github.clash-verge-rev.clash-verge-rev"


def get_headers():
    """获取 API 请求头（含 secret）"""
    headers = {"Content-Type": "application/json"}
    if CLASH_SECRET:
        headers["Authorization"] = f"Bearer {CLASH_SECRET}"
    return headers

# 颜色定义 (兼容 Windows)
class Colors:
    HEADER = ''
    BLUE = ''
    CYAN = ''
    GREEN = ''
    YELLOW = ''
    RED = ''
    ENDC = ''
    BOLD = ''


def echo(msg, **kwargs):
    """Print wrapper"""
    click.echo(msg, **kwargs)


def api_get(endpoint: str) -> dict:
    """发送 GET 请求到 Clash API"""
    try:
        resp = requests.get(f"{CLASH_API}{endpoint}", headers=get_headers(), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        click.echo(f"[ERROR] Cannot connect to Clash API ({CLASH_API}). Is Clash Verge Rev running?", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)


def api_put(endpoint: str, data: dict) -> dict:
    """发送 PUT 请求到 Clash API"""
    try:
        resp = requests.put(f"{CLASH_API}{endpoint}", json=data, headers=get_headers(), timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        sys.exit(1)


def get_proxies() -> dict:
    return api_get("/proxies")


def get_config() -> dict:
    return api_get("/configs")


def get_traffic() -> dict:
    return api_get("/traffic")


def format_bytes(num: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PB"


@click.group()
def cli():
    """Clash for Windows CLI - 通过命令行管理 Clash"""
    pass


@cli.command("status")
def cmd_status():
    """查看当前状态"""
    config = get_config()
    traffic = get_traffic()
    proxies = get_proxies()

    click.echo("\n=== Clash Status ===")
    click.echo(f"  Mixed Port: {config.get('mixed-port', 'N/A')}")
    click.echo(f"  Mode: {config.get('mode', 'N/A')}")
    click.echo(f"  Allow LAN: {'Yes' if config.get('allow-lan') else 'No'}")

    global_proxy = proxies.get('proxies', {}).get('GLOBAL', {})
    current_node = global_proxy.get('now', 'N/A') if isinstance(global_proxy, dict) else 'N/A'
    click.echo(f"  Current Node: {current_node}")

    up = traffic.get('up', 0)
    down = traffic.get('down', 0)
    click.echo(f"  Upload: {format_bytes(up)} | Download: {format_bytes(down)}")
    click.echo()


@cli.command("proxies")
def cmd_proxies():
    """列出所有代理节点"""
    data = get_proxies()
    proxy_groups = data.get('proxies', {})

    click.echo("\n=== Proxy Nodes ===\n")

    groups = {
        '香港 (HK)': [],
        '新加坡 (SG)': [],
        '日本 (JP)': [],
        '美国 (US)': [],
        '台湾': [],
        '其他': []
    }

    for name, proxy in proxy_groups.items():
        if name in ['DIRECT', 'REJECT', 'GLOBAL']:
            continue

        if not isinstance(proxy, dict):
            continue

        now = proxy.get('now', '')

        if any(x in name for x in ['Hong Kong', 'HK', '香港']):
            groups['香港 (HK)'].append((name, now))
        elif any(x in name for x in ['Singapore', 'SG', '新加坡']):
            groups['新加坡 (SG)'].append((name, now))
        elif any(x in name for x in ['Japan', 'JP', '日本']):
            groups['日本 (JP)'].append((name, now))
        elif any(x in name for x in ['US', '美国']):
            groups['美国 (US)'].append((name, now))
        elif any(x in name for x in ['Taipei', '台湾']):
            groups['台湾'].append((name, now))
        else:
            groups['其他'].append((name, now))

    for gname, nodes in groups.items():
        if not nodes:
            continue
        click.echo(f"{gname}:")
        for name, now in nodes:
            marker = f" [*]" if now == name else ""
            click.echo(f"  {name}{marker}")
        click.echo()


@cli.command("select")
@click.argument('node')
def cmd_select(node: str):
    """切换代理节点"""
    data = get_proxies()
    proxy_groups = data.get('proxies', {})

    found = None
    for name in proxy_groups.keys():
        if node.lower() in name.lower():
            found = name
            break

    if not found:
        click.echo(f"[ERROR] Node '{node}' not found", err=True)
        return

    try:
        api_put("/proxies/GLOBAL", {"name": found})
        click.echo(f"[OK] Switched to: {found}")
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)


@cli.command("mode")
@click.argument('mode', type=click.Choice(['rule', 'global', 'direct']))
def cmd_mode(mode: str):
    """切换代理模式 (rule/global/direct)"""
    try:
        api_put("/configs", {"mode": mode})
        click.echo(f"[OK] Mode switched to: {mode}")
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)


@cli.command("config")
def cmd_config():
    """显示当前配置"""
    data = get_config()

    click.echo("\n=== Clash Config ===\n")
    click.echo(f"  Mixed Port:    {data.get('mixed-port', 'N/A')}")
    click.echo(f"  SOCKS Port:    {data.get('socks-port', 'N/A')}")
    click.echo(f"  HTTP Port:     {data.get('port', 'N/A')}")
    click.echo(f"  Redir Port:    {data.get('redir-port', 'N/A')}")
    click.echo(f"  Allow LAN:     {'Yes' if data.get('allow-lan') else 'No'}")
    click.echo(f"  Bind Address:  {data.get('bind-address', 'N/A')}")
    click.echo(f"  Mode:          {data.get('mode', 'N/A')}")
    click.echo(f"  Log Level:     {data.get('log-level', 'N/A')}")
    click.echo(f"  IPv6:          {'Yes' if data.get('ipv6') else 'No'}")
    click.echo()


@cli.command("logs")
@click.option('--limit', default=10, help='Number of lines to show')
def cmd_logs(limit: int):
    """查看 Clash Verge Rev 日志"""
    log_dir = CONFIG_DIR / "logs"

    if not log_dir.exists():
        click.echo(f"[ERROR] Log directory not found: {log_dir}")
        return

    log_files = sorted(log_dir.glob("*.log"), key=os.path.getmtime, reverse=True)

    if not log_files:
        click.echo("No log files found")
        return

    latest_log = log_files[0]
    try:
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent = lines[-limit:] if len(lines) > limit else lines

        click.echo(f"\n=== Recent Logs ({latest_log.name}) ===\n")
        for line in recent:
            line = line.strip()
            if line:
                click.echo(line)
    except Exception as e:
        click.echo(f"[ERROR] Reading log: {e}")


@cli.command("profiles")
def cmd_profiles():
    """列出配置文件"""
    profile_dir = CONFIG_DIR / "profiles"

    if not profile_dir.exists():
        click.echo(f"[ERROR] Profile directory not found: {profile_dir}")
        return

    click.echo("\n=== Clash Verge Rev Profiles ===\n")

    # Clash Verge Rev uses profiles.yaml
    profiles_yaml = CONFIG_DIR / "profiles.yaml"
    if profiles_yaml.exists():
        try:
            import yaml
            with open(profiles_yaml, 'r', encoding='utf-8') as f:
                profile_list = yaml.safe_load(f)

            if profile_list and isinstance(profile_list, list):
                for p in profile_list:
                    name = p.get('name', 'Unknown')
                    file_name = p.get('file', 'N/A')
                    click.echo(f"  {name}")
                    click.echo(f"    File: {file_name}")
                    click.echo()
            elif profile_list and 'profiles' in profile_list:
                for p in profile_list['profiles']:
                    name = p.get('name', 'Unknown')
                    file_name = p.get('file', 'N/A')
                    click.echo(f"  {name}")
                    click.echo(f"    File: {file_name}")
                    click.echo()
        except ImportError:
            click.echo("(PyYAML not installed, showing raw files)")
        except Exception as e:
            click.echo(f"Error reading profiles: {e}")

    click.echo("Profile files:")
    for f in sorted(profile_dir.glob("*.yaml")):
        size = f.stat().st_size
        click.echo(f"  {f.name} ({size} bytes)")


@cli.command("restart")
def cmd_restart():
    """重启 Clash 核心"""
    click.echo("Note: Restart is managed by Clash for Windows GUI")
    try:
        api_put("/configs", {"restart": True})
        click.echo("[OK] Restart signal sent")
    except Exception as e:
        click.echo(f"[ERROR] {e}")


@cli.command("import")
@click.argument('url')
@click.argument('name', required=False)
def cmd_import(url: str, name: str = None):
    """导入订阅链接

    URL: 订阅链接
    NAME: 可选，自定义名称
    """
    import time
    import yaml

    profile_dir = CONFIG_DIR / "profiles"
    if not profile_dir.exists():
        click.echo(f"[ERROR] Profile directory not found: {profile_dir}")
        return

    # 生成时间戳文件名
    timestamp = str(int(time.time() * 1000))
    profile_file = profile_dir / f"{timestamp}.yaml"

    # 下载订阅
    click.echo(f"Downloading subscription from {url}...")
    try:
        resp = requests.get(url, timeout=30, headers={
            'User-Agent': 'ClashVergeRev/2.5.1'
        })
        resp.raise_for_status()
        content = resp.text

        # 检查是否是有效配置
        if 'proxies:' not in content and 'proxy-providers:' not in content:
            click.echo("[ERROR] Invalid subscription - no proxies found")
            return

        # 保存配置文件
        with open(profile_file, 'w', encoding='utf-8') as f:
            f.write(content)
        click.echo(f"[OK] Saved to {profile_file.name}")

    except requests.exceptions.Timeout:
        click.echo("[ERROR] Download timeout")
        return
    except requests.exceptions.RequestException as e:
        click.echo(f"[ERROR] Download failed: {e}")
        return

    # 更新 profiles.yaml
    profiles_yaml = CONFIG_DIR / "profiles.yaml"

    # 读取现有配置
    profile_list = []
    if profiles_yaml.exists():
        try:
            with open(profiles_yaml, 'r', encoding='utf-8') as f:
                profile_list = yaml.safe_load(f) or []
        except:
            pass

    # 生成名称
    if not name:
        name = f"订阅 {len(profile_list) + 1}"

    # 添加新订阅
    new_entry = {
        'name': name,
        'file': profile_file.name,
        'url': url,
        'selected': [],
        'type': 'remote'
    }

    profile_list.append(new_entry)

    # 保存 profiles.yaml
    try:
        with open(profiles_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(profile_list, f, allow_unicode=True, default_flow_style=False)
        click.echo(f"[OK] Added to profiles: {name}")
        click.echo("")
        click.echo("Note: Restart Clash Verge Rev or reload profile for changes to take effect.")
    except Exception as e:
        click.echo(f"[ERROR] Failed to update profiles.yaml: {e}")


@cli.command("delete")
@click.argument('name')
def cmd_delete(name: str):
    """删除订阅

    NAME: 订阅名称（支持模糊匹配）
    """
    import yaml

    profile_dir = CONFIG_DIR / "profiles"
    profiles_yaml = CONFIG_DIR / "profiles.yaml"

    if not profiles_yaml.exists():
        click.echo("[ERROR] profiles.yaml not found")
        return

    try:
        with open(profiles_yaml, 'r', encoding='utf-8') as f:
            profile_list = yaml.safe_load(f) or []
    except Exception as e:
        click.echo(f"[ERROR] Failed to read profiles.yaml: {e}")
        return

    deleted = False

    for i, p in enumerate(profile_list):
        if name.lower() in p.get('name', '').lower():
            file_name = p.get('file')
            if file_name:
                profile_file = profile_dir / file_name
                if profile_file.exists():
                    profile_file.unlink()
                    click.echo(f"[OK] Deleted {file_name}")

            profile_list.pop(i)
            deleted = True
            click.echo(f"[OK] Removed from profiles: {p.get('name')}")
            break

    if deleted:
        try:
            with open(profiles_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(profile_list, f, allow_unicode=True, default_flow_style=False)
            click.echo("")
            click.echo("Note: Restart Clash Verge Rev or reload profile for changes to take effect.")
        except Exception as e:
            click.echo(f"[ERROR] Failed to write profiles.yaml: {e}")
    else:
        click.echo(f"[ERROR] Profile '{name}' not found")


if __name__ == '__main__':
    cli()
