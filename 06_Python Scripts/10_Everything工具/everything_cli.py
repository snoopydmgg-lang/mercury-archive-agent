#!/usr/bin/env python3
"""
Everything CLI Tool
快速文件搜索工具

注意: 需要在 Everything 中启用 HTTP 服务器
设置 → HTTP服务器 → 启用HTTP服务器（默认端口 80）
"""

import subprocess
import sys
import os
import io
import json
import re
from pathlib import Path
from datetime import datetime
import html.parser
from urllib.parse import unquote, quote

# 修复 Windows 控制台中文显示
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置
EVERYTHING_PATH = "D:/Everything/Everything.exe"
EVERYTHING_INI = "C:/Users/Administrator/AppData/Roaming/Everything/Everything.ini"
HTTP_API_URL = "http://127.0.0.1:80"


class EverythingResultParser(html.parser.HTMLParser):
    """解析 Everything HTTP 搜索结果"""

    def __init__(self):
        super().__init__()
        self.results = []
        self.in_result_tr = False
        self.current_td_class = None
        self.current_data = ""
        self.current_row = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'tr':
            if attrs_dict.get('class') in ('trdata1', 'trdata2'):
                self.in_result_tr = True
                self.current_row = {'name': '', 'path': '', 'size': 0}
                self.current_data = ""

        elif tag == 'td' and self.in_result_tr:
            self.current_td_class = attrs_dict.get('class', '')
            self.current_data = ""

        elif tag == 'a' and self.in_result_tr and self.current_td_class in ('file', 'folder'):
            # 提取链接中的文件名
            href = attrs_dict.get('href', '')
            if href:
                # URL 解码
                from urllib.parse import unquote
                filename = unquote(href.split('/')[-1])
                if self.current_td_class == 'file':
                    if not self.current_row.get('name'):
                        self.current_row['name'] = filename
                    self.current_row['path'] = unquote('/'.join(href.split('/')[:-1]).lstrip('/')).replace('/', '\\')

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_result_tr:
            text = self.current_data.strip()
            if self.current_td_class == 'sizedata' and text:
                self.current_row['size'] = self.parse_size(text)
            self.current_td_class = None

        elif tag == 'tr' and self.in_result_tr:
            if self.current_row and self.current_row.get('name'):
                self.results.append(self.current_row)
            self.in_result_tr = False
            self.current_row = None

    def handle_data(self, data):
        if self.in_result_tr and self.current_td_class:
            self.current_data += data

    @staticmethod
    def parse_size(size_str):
        """解析文件大小字符串"""
        if not size_str or size_str == '-':
            return 0
        size_str = size_str.strip().upper()
        match = re.match(r'([\d.,]+)\s*([KMGT]?B?)', size_str)
        if not match:
            return 0
        value = float(match.group(1).replace(',', ''))
        unit = match.group(2)
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        return int(value * multipliers.get(unit, 1))


# 颜色
def c(msg, color=''):
    """带颜色的打印"""
    colors = {
        'r': '\033[91m', 'g': '\033[92m', 'y': '\033[93m',
        'b': '\033[94m', 'c': '\033[96m', '': '\033[0m'
    }
    return f"{colors.get(color, '')}{msg}{colors['']}"


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes is None or size_bytes == 0:
        return ""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def is_http_server_enabled():
    """检查 HTTP 服务器是否启用"""
    try:
        response = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', HTTP_API_URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        return response.stdout.strip() == '200'
    except:
        return False


def search_via_http(query, max_results=50):
    """通过 HTTP API 搜索"""
    url = f"{HTTP_API_URL}/?search={query}&max-results={max_results}"
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10
        )
        return result.stdout
    except Exception as e:
        return ""


def parse_results(html_content):
    """解析 HTML 搜索结果"""
    parser = EverythingResultParser()
    try:
        parser.feed(html_content)
        return parser.results
    except:
        return []


def list_results(results, show_path=True, show_size=True, limit=50):
    """显示搜索结果"""
    if not results:
        print(c("\n没有找到结果", 'y'))
        return

    print(f"\n{c(f'=== 搜索结果 ({len(results)} 个) ===', 'c')}\n")

    for i, r in enumerate(results[:limit]):
        name = r.get('name', 'Unknown')
        path = r.get('path', '')
        size = r.get('size', 0)

        print(f"{i+1}. {c(name, 'g')}")
        if show_path and path:
            print(f"   {path}")
        if show_size and size:
            print(f"   {format_size(size)}")
        print()


def show_help():
    """显示帮助"""
    print(f"""
{c('Everything CLI', 'c')}
快速文件搜索工具

{c('用法:', 'y')}
  python everything_cli.py <命令> [参数]

{c('命令:', 'y')}
  search, s <关键词>      搜索文件
  ext <扩展名>           按扩展名搜索（如: ext txt）
  path <路径> <关键词>   在指定路径下搜索
  status                 检查 HTTP 服务器状态
  open                   打开 Everything 窗口
  help                   显示帮助

{c('搜索选项:', 'y')}
  -n, --max <数量>       最大结果数（默认50）
  --no-path              不显示完整路径
  --no-size              不显示文件大小

{c('Everything 搜索语法:', 'y')}
  *.txt                  搜索所有 txt 文件
  report                 搜索包含 report 的文件
  "my document"          精确搜索
  ext:doc                搜索 doc 文档
  size:>1mb              搜索大于 1MB 的文件
  date:2024-01-01        搜索指定日期修改的文件
  regex:^a.*\.pdf$        使用正则表达式

{c('示例:', 'y')}
  python everything_cli.py s "*.py"
  python everything_cli.py search "document" --max 20
  python everything_cli.py ext pdf
  python everything_cli.py open
  python everything_cli.py status
""")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd in ('help', '-h', '--help'):
        show_help()

    elif cmd == 'status':
        if is_http_server_enabled():
            print(c("[OK] HTTP 服务器已启用", 'g'))
            print("  可以使用后台搜索功能")
        else:
            print(c("[INFO] HTTP 服务器未启用", 'y'))
            print("  启用方法: Everything → 设置 → HTTP服务器 → 启用HTTP服务器")
            print("  然后重启 Everything")

    elif cmd == 'open':
        subprocess.Popen([EVERYTHING_PATH, "-newwindow"])
        print(c("[OK] 已打开 Everything 窗口", 'g'))

    elif cmd in ('search', 's'):
        max_results = 50
        show_path = True
        show_size = True

        # 解析参数
        args = sys.argv[2:]
        query = None

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ('-n', '--max'):
                if i + 1 < len(args):
                    max_results = int(args[i + 1])
                    i += 2
                else:
                    i += 1
            elif arg in ('--no-path', '-p'):
                show_path = False
                i += 1
            elif arg in ('--no-size', '-s'):
                show_size = False
                i += 1
            elif not arg.startswith('-'):
                query = arg
                i += 1
            else:
                i += 1

        if not query:
            print("[ERROR] 请提供搜索关键词")
            show_help()
            sys.exit(1)

        if is_http_server_enabled():
            html_content = search_via_http(query, max_results)
            results = parse_results(html_content) if html_content else []
            list_results(results, show_path, show_size, max_results)
        else:
            print(c("[INFO] HTTP 服务器未启用", 'y'))
            print("  启用方法: Everything → 设置 → HTTP服务器 → 启用HTTP服务器")
            print("  然后重启 Everything")

    elif cmd == 'ext':
        # ext <扩展名>
        if len(sys.argv) < 3:
            print("[ERROR] 用法: everything_cli.py ext <扩展名>")
            sys.exit(1)
        ext = sys.argv[2]
        query = f"*.{ext.lstrip('.')}"

        if is_http_server_enabled():
            html_content = search_via_http(query, 50)
            results = parse_results(html_content) if html_content else []
            list_results(results, True, True, 50)
        else:
            print(c("[INFO] HTTP 服务器未启用", 'y'))

    elif cmd == 'path':
        # path <路径> <关键词>
        if len(sys.argv) < 4:
            print("[ERROR] 用法: everything_cli.py path <路径> <关键词>")
            sys.exit(1)
        search_path = sys.argv[2]
        query = sys.argv[3]
        full_query = f'"{search_path}\\{query}"'

        if is_http_server_enabled():
            html_content = search_via_http(full_query, 50)
            results = parse_results(html_content) if html_content else []
            list_results(results, True, True, 50)
        else:
            print(c("[INFO] HTTP 服务器未启用", 'y'))

    else:
        # 默认为搜索
        query = ' '.join(sys.argv[1:])
        if query:
            if is_http_server_enabled():
                html_content = search_via_http(query, 50)
                results = parse_results(html_content) if html_content else []
                list_results(results)
            else:
                print(c("[INFO] HTTP 服务器未启用", 'y'))
                print("  启用方法: Everything → 设置 → HTTP服务器 → 启用HTTP服务器")
        else:
            show_help()
