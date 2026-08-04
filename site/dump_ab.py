# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
i = src.find('elif t == "abstract_heading"')
print('--- abstract_heading 上下文 ---')
print(src[i-500:i+300])
print()
j = src.find('def _add_para')
print('--- _add_para ---')
print(src[j:j+600])
