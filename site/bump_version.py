# -*- coding: utf-8 -*-
"""版本号 1.0.4 -> 1.0.5（纯 python 改，避免 PowerShell 编码坑）"""
import json

# 1. license/version.py
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = 'VERSION = "1.0.4"'
new = 'VERSION = "1.0.5"'
assert old in s, 'version.py 未找到 1.0.4'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py ->', new)

# 2. version.json
v = json.load(open('version.json', encoding='utf-8'))
v['version'] = '1.0.5'
v['url'] = 'https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.5/DocFormatTool.exe'
v['note'] = '参考文献 OpenXML 规范化：强制左对齐防短条目字距拉伸、清除下划线/加粗残留、悬挂缩进；下划线上下文清洗（封面/表单填空下划线智能保留）；标题主题色统一黑色；新增保留原文颜色/斜体开关'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json ->', v['version'])

# 3. 验证
raw = open('version.json', 'rb').read(3)
print('version.json 无BOM:', raw != b'\xef\xbb\xbf')
from license import version
print('import OK, VERSION =', version.VERSION)
