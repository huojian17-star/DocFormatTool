# -*- coding: utf-8 -*-
"""v1.0.16 发布准备：版本号 + version.json + sha256 + full_url"""
import json, hashlib, os, sys

VER = "1.0.16"

# 1. version.py
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
import re
s2 = re.sub(r'VERSION = "[^"]*"', 'VERSION = "%s"' % VER, s, count=1)
assert s2 != s
open(p, 'w', encoding='utf-8', newline='').write(s2)
print('version.py →', VER)

# 2. exe sha256（dist 里最新的 exe = v1.0.15 构建产物，作为 1.0.16 的安装载体）
exe = r'dist\DocFormatTool.exe'
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
print('sha256:', sha[:16], '...')

# 3. version.json
vj = {
    "version": VER,
    "note": "v1.0.16：全新界面（AiNiee 风格侧边栏+卡片+莫兰迪配色）+ 单栏模板 + 标题/关键词识别修复 + 更新链路加固",
    "full_url": "https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v" + VER + "/DocFormatTool.exe",
    "full_sha256": sha,
    "manual_url": "https://wwavh.lanzoul.com/iu1i640hnz6b",
    "min_version": "1.0.0"
}
open(r'site\version.json', 'w', encoding='utf-8').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json →', VER)
