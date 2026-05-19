# -*- coding: utf-8 -*-
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

input_path = r'E:\1.work\douyin\1.shuixing\00_InBox_收件箱\zhihu_codex\codex可以100%正式接管所有编程工作了吗？\codex可以100%正式接管所有编程工作了吗？.md'
output_path = r'E:\1.work\douyin\1.shuixing\00_InBox_收件箱\zhihu_codex\codex清洗版.md'

with open(input_path, 'r', encoding='utf-8') as f:
    raw = f.read()

# ===== 彻底清洗 =====

# 1. 把换行符临时替换
text = raw.replace('\n', '|||NL|||')

# 2. 删除所有图片和链接
text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
text = re.sub(r'\[.*?\]\(//www[^\)]*\)', '', text)
text = re.sub(r'\[.*?\]\(https?://[^\)]*\)', '', text)
text = re.sub(r'data:image[^,)]*', '', text)

# 3. 删除知乎UI残留词
ui_words = [
    '编程', 'AI编程', 'CODEX', 'GPT-5-Codex', 'AI请接招',
    '人工智能话题下的优秀著者', '话题收录',
    '滨绥图佳保安第三旅上校团副', '天地大观，志存高远',
    '清华大学', '计算机科学技术硕士',
    '关注问题', '写回答', '邀请回答',
    '登录后你可以', '不限量看优质回答', '私信', '精彩内容一键收藏',
    '查看全部', '关于作者', '被收藏',
    '更多回答', '收起', '关注', '新智元', '青梅如豆', '字节', 'Nate',
    '关注者', '被浏览',
    '好问题', '分享', '条评论',
    '1,300', '1,954,065',
    '显示全部', '创作中心', '搜索', '首页', '发现', '等你来答',
]
for word in ui_words:
    text = text.replace(word, '')

# 4. 恢复换行符
text = text.replace('|||NL|||', '\n')

# 5. 删除整行UI残留
lines = text.split('\n')
cleaned = []
skip_patterns = [
    r'^\s*$',
    r'^[\[\]!]+$',
    r'^\s*\[\s*\]\s*$',
    r'^\s*//www[^\s]*$',
    r'^\s*https?://[^\s]*$',
    r'^\s*\d+\s*人赞同.*$',
    r'^\s*\d+\s*条评论.*$',
    r'^\s*\*\*\d+[,0-9]*\*\*.*$',
    r'^\s*相关问题.*$',
    r'^\s*大家都在搜.*$',
    r'^\s*换一换.*$',
    r'^\s*low code.*$',
    r'^\s*hello code.*$',
    r'^\s*学好计算机.*$',
    r'^\s*伊朗局势.*$',
    r'^\s*女企业家.*$',
    r'^\s*郭艾伦.*$',
    r'^\s*白宫.*$',
    r'^\s*王楚钦.*$',
    r'^\s*网传全红婵.*$',
    r'^\s*25.*$',
    r'^\s*同事.skill.*$',
    r'^\s*黄晓明.*$',
    r'^\s*创作.*$',
    r'^\s*搜索.*$',
    r'^\s*首页.*$',
    r'^\s*发现.*$',
    r'^\s*等你来答.*$',
    r'^\s*年.*$',
    r'^\s*月.*$',
    r'^\s*日.*$',
    r'^\s*编辑于.*$',
    r'^\s*辽宁.*$',
    r'^\s*赞同.*$',
    r'^\s*收藏.*$',
    r'^\s*喜欢.*$',
    r'^\s*答案.*$',
    r'^\s*回答.*$',
    r'^\s*问题.*$',
    r'^\s*作者.*$',
    r'^\s*来源.*$',
    r'^\s*链接.*$',
    r'^\s*出处.*$',
    r'^\s*作者：.*$',
    r'^\s*发布于.*$',
    r'^\s*\[图片\].*$',
    r'^\s*创建.*$',
]
for line in lines:
    line = line.strip()
    if not line:
        continue
    skip = False
    for pat in skip_patterns:
        if re.match(pat, line):
            skip = True
            break
    if skip:
        continue
    # 清理残留**和**
    line = re.sub(r'\*\*+', '', line)
    # 跳过纯符号行
    symbols = r'^[\[\](){}<>!@#$%^&*_.,?/:;\"\'-]+$'
    if re.match(symbols, line):
        continue
    if line.strip():
        cleaned.append(line)

content = '\n'.join(cleaned)

# 6. 再次清理多余空行
content = re.sub(r'\n{3,}', '\n\n', content)
content = content.strip()

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("清洗完成！输出:", output_path)
print("大小:", len(content), "字符")

# 预览
print("\n=== 预览前60行 ===")
for i, line in enumerate(content.split('\n')[:60]):
    if line.strip():
        print(i+1, ":", line[:100])
