# -*- coding: utf-8 -*-
import json
p = r'license\version.py'
s = open(p, encoding='utf-8').read().replace('1.0.10', '1.0.11')
open(p, 'w', encoding='utf-8', newline='').write(s)
v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.11'
v['note'] = 'v1.0.11：修复自动更新——点击"自动更新"无反应/进度窗口不显示/失败无提示（三个线程与闭包问题）。'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.py/version.json → 1.0.11')
