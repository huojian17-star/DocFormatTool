# -*- coding: utf-8 -*-
"""版本号 1.0.5 -> 1.0.6（纯 python 改，避免 PowerShell 编码坑）"""
import json

# 1. license/version.py
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = 'VERSION = "1.0.5"'
new = 'VERSION = "1.0.6"'
assert old in s, 'version.py 未找到 1.0.5'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py ->', new)

# 2. version.json
v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.6'
v['url'] = 'https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.6/DocFormatTool.exe'
v['note'] = '修复自动更新问题（检查超时放宽/下载失败给出手动下载指引/覆盖失败提示）；高级选项展开后底部按钮不再被挤出'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json ->', v['version'])

raw = open('version.json', 'rb').read(3)
print('version.json 无BOM:', raw != b'\xef\xbb\xbf')
