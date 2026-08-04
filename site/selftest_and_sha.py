# -*- coding: utf-8 -*-
"""本地测 selftest + 计算 releases exe sha256 写入 version.json + version 设 1.0.13"""
import sys, os, hashlib, json, re
sys.path.insert(0, '.')

# 1) 本地 selftest（源码）
import license.version as v
print('=== 源码 selftest ===')
v.selftest(keep=False)

# 2) 计算 releases exe sha256
p = r'releases\DocFormatTool.exe'
h = hashlib.sha256()
with open(p, 'rb') as f:
    for c in iter(lambda: f.read(1048576), b''):
        h.update(c)
sha = h.hexdigest()
print('\nreleases exe sha256:', sha)

# 3) version.json 更新
vj = json.load(open('version.json', encoding='utf-8'))
vj['version'] = '1.0.13'
vj['sha256'] = sha
vj['full_url'] = 'https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/releases/DocFormatTool.exe'
vj['note'] = 'v1.0.13：测试版（验证更新链路，稍后恢复）。'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json → 1.0.13 + sha256')
