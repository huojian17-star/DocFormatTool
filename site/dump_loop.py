# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
print('--- 主循环分支 ---')
for m in re.finditer(r'    elif t == "(\w+)"', src):
    print(m.group(1), end=' ')
print()
i = src.find('def reformat_existing')
if i > 0:
    print()
    print('--- reformat_existing 开头 ---')
    print(src[i:i+1400])
