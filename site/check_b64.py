# -*- coding: utf-8 -*-
import re
src = open(r'app\main.py', encoding='utf-8').read()
m = re.search(r'_MASCOT_B64 = "([^"]*)"', src)
if m:
    print('b64 长度:', len(m.group(1)))
else:
    print('未找到 _MASCOT_B64')
for l in src.splitlines():
    if 'subsample' in l:
        print('subsample 行:', l.strip()[:90])
