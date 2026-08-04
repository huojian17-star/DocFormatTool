# -*- coding: utf-8 -*-
"""版本号 1.0.8 -> 1.0.9（样式修复）"""
import json

p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = 'VERSION = "1.0.8"'
new = 'VERSION = "1.0.9"'
assert old in s, 'version.py 未找到 1.0.8'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py ->', new)

v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.9'
v['full_url'] = 'https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.9/DocFormatTool.exe'
v['note'] = ('v1.0.9：修复标题样式问题——摘要/目录/参考文献进入样式集与导航（Heading1），'
             '论文题目用标题样式；此前部分标题显示为正文。')
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json ->', v['version'])
print('full_url ->', v['full_url'])
