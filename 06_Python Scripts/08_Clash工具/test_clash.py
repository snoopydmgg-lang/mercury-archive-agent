#!/usr/bin/env python3
"""Quick test for Clash CLI"""
import requests

CLASH_API = "http://127.0.0.1:8856"

print("Testing Clash API...")
try:
    r = requests.get(f"{CLASH_API}/configs", timeout=3)
    cfg = r.json()
    print(f"  Mode: {cfg.get('mode')}")
    print(f"  Port: {cfg.get('mixed-port')}")
    print(f"  Allow LAN: {cfg.get('allow-lan')}")

    r2 = requests.get(f"{CLASH_API}/proxies", timeout=3)
    proxies = r2.json()
    g = proxies.get('proxies', {}).get('GLOBAL', {})
    print(f"  Current node: {g.get('now') if isinstance(g, dict) else 'N/A'}")

    r3 = requests.get(f"{CLASH_API}/traffic", timeout=3)
    traffic = r3.json()
    print(f"  Upload: {traffic.get('up', 0)}, Download: {traffic.get('down', 0)}")

    print("\n[OK] All tests passed!")
except Exception as e:
    print(f"[ERROR] {e}")
