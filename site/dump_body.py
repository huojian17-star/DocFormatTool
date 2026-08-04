# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
m = re.search(r'st = \{.*?\}', src, re.S)
print('--- st 初始化 ---')
print(m.group(0) if m else '未找到')
print()
m2 = re.search(r'elif t == "body":.*?(?=\n    elif |\n    else)', src, re.S)
print('--- body 分支 ---')
print(m2.group(0)[:700] if m2 else '未找到')
