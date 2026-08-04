# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
for typ in ['abstract_heading', 'keywords', 'ref_heading', 'ref_item', 'appendix']:
    m = re.search(r'elif t == "' + typ + r'".*?(?=\n    elif |\n    else)', src, re.S)
    if m:
        print('====', typ, '====')
        print(m.group(0)[:800])
        print()
