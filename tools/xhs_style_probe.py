# -*- coding: utf-8 -*-
"""抓取小红书 explore 页真实帖子标题，分析"小红书体"风格特征。"""
import re
import urllib.request
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REQ = urllib.request.Request(
    "https://www.xiaohongshu.com/explore",
    headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
    },
)
html = urllib.request.urlopen(REQ, timeout=15).read().decode("utf-8", "ignore")

# 提取标题（JSON 字段与页面文本两种来源）
titles = []
for m in re.finditer(r'"title":"([^"]{4,80})"', html):
    t = m.group(1).encode().decode("unicode_escape", "ignore")
    if t and t not in titles:
        titles.append(t)
for m in re.finditer(r'title="([^"]{4,80})"', html):
    t = m.group(1)
    if t and t not in titles:
        titles.append(t)

print("抓取到标题数:", len(titles))
for t in titles[:50]:
    print(" -", t[:55])

# 风格特征统计
import collections
feats = collections.Counter()
for t in titles:
    if re.search(r"[!！]", t):
        feats["感叹号"] += 1
    if re.search(r"[?？]", t):
        feats["问号"] += 1
    if re.search(r"\.\.\.|…", t):
        feats["省略号"] += 1
    if re.search(r"[😀-🙏🌀-🫿]", t):
        feats["emoji"] += 1
    if re.search(r"\d+[rR分块条个张元钱]|\d+块钱|\d+r", t):
        feats["价格/数字"] += 1
    if re.search(r"[“\"『「]", t):
        feats["引号"] += 1
    if len(t) <= 12:
        feats["短标题(≤12字)"] += 1
print("\n风格特征统计（共%d条）:" % len(titles))
for k, v in feats.most_common():
    print("  %s: %d (%.0f%%)" % (k, v, v / max(len(titles), 1) * 100))
