# -*- coding: utf-8 -*-
"""版本号 1.0.6 -> 1.0.7（纯 python，避免 PowerShell 编码/转义坑）"""
import json

p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = 'VERSION = "1.0.6"'
new = 'VERSION = "1.0.7"'
assert old in s, 'version.py 未找到 1.0.6'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py ->', new)

v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.7'
v['url'] = 'https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.7/DocFormatTool.exe'
v['note'] = '自动更新增强：下载进度窗口 + 60秒超时兜底（网络慢不再无限等待，失败给出手动下载指引）'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json ->', v['version'])
raw = open('version.json', 'rb').read(3)
print('无BOM:', raw != b'\xef\xbb\xbf')
