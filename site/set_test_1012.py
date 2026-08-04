# -*- coding: utf-8 -*-
"""临时切到 1.0.12 测试版：version.py + version.json（version=1.0.12, full_url 指向 releases/ 的 1.0.12 exe）"""
import json, re

# 1) version.py → 1.0.12
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
s = re.sub(r'VERSION\s*=\s*"[^"]+"', 'VERSION = "1.0.12"', s)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py → 1.0.12')

# 2) version.json
v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.12'
v['full_url'] = 'https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/releases/DocFormatTool.exe'
v['note'] = 'v1.0.12：测试版（验证自动更新链路，稍后恢复）。'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json → 1.0.12, full_url 指向 releases/')
