# -*- coding: utf-8 -*-
"""临时升测试版 1.0.13（验证 explorer 重启，测完恢复 1.0.11）"""
import json, hashlib

# 算 releases v1.0.13 的 sha256
h = hashlib.sha256()
with open(r'releases\DocFormatTool.exe', 'rb') as f:
    for c in iter(lambda: f.read(1048576), b''):
        h.update(c)
sha = h.hexdigest()

vj = json.load(open('version.json', encoding='utf-8'))
vj['version'] = '1.0.13'
vj['sha256'] = sha
vj['full_url'] = 'https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/releases/DocFormatTool.exe'
vj['note'] = 'v1.0.13：测试版（验证自动重启修复，测完恢复）。'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json → 1.0.13 测试版（sha256=%s...）' % sha[:10])
