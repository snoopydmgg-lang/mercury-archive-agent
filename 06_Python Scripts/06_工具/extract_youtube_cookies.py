# -*- coding: utf-8 -*-
"""Extract YouTube cookies from Edge browser and save as Netscape format for yt-dlp"""
import os, sys, io, json, base64, sqlite3, shutil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

EDGE_BASE = os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data")
OUTPUT = "06_Python Scripts/06_工具/youtube_cookies.txt"

# 1. Get encrypted key
with open(os.path.join(EDGE_BASE, "Local State"), "r", encoding="utf-8") as f:
    local_state = json.load(f)
encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
aes_key = CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
print(f"AES key: {len(aes_key)} bytes")

# 2. Copy and extract
src = os.path.join(EDGE_BASE, "Default", "Network", "Cookies")
tmp = os.path.join(os.environ["TEMP"], "edge_cookies_extract.db")
shutil.copy2(src, tmp)
conn = sqlite3.connect(tmp)
rows = conn.execute(
    "SELECT host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly "
    "FROM cookies WHERE host_key LIKE '%youtube.com'"
).fetchall()
conn.close()
os.remove(tmp)
print(f"Found {len(rows)} YouTube cookies")

# 3. Decrypt
cookies = []
for row in rows:
    host, name, enc_val, path, expires, secure, httponly = row
    if not enc_val:
        continue
    try:
        if enc_val[:3] == b"v20":
            nonce = enc_val[3:15]          # 12 bytes
            tag = enc_val[-16:]            # last 16 bytes = GCM auth tag
            ciphertext = enc_val[15:-16]   # middle = encrypted data
            cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
            value = cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8")
        elif enc_val[:3] == b"v10":
            value = CryptUnprotectData(enc_val[3:], None, None, None, 0)[1].decode("utf-8")
        else:
            continue
    except Exception as e:
        print(f"  FAIL {host}:{name}: {e}")
        continue

    if value:
        value = value.replace("\t", "").replace("\n", "").replace("\r", "")
        if value.strip():
            cookies.append((host, name, value, path, expires, secure, httponly))

print(f"Decrypted: {len(cookies)} cookies")
for h, n, v, *rest in cookies:
    print(f"  {h}: {n} = {v[:60]}{'...' if len(v) > 60 else ''}")

# Netscape format
lines = ["# Netscape HTTP Cookie File"]
for host, name, value, path, expires, secure, httponly in cookies:
    domain = host
    flag = "TRUE" if host.startswith(".") else "FALSE"
    sec = "TRUE" if secure else "FALSE"
    expires_unix = int(expires / 1000000) - 11644473600 if expires and expires > 10000000000000000 else 0
    lines.append(f"{domain}\t{flag}\t{path}\t{sec}\t{expires_unix}\t{name}\t{value}")

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, "w", encoding="ascii", errors="replace") as f:
    f.write("\n".join(lines) + "\n")
print(f"Saved: {OUTPUT}")
