# -*- coding: utf-8 -*-
src = open(r'app\main.py', encoding='utf-8').read()
for kw in ['可拖拽', 'DnD.TEntry', 'DragEnter']:
    idx = src.find(kw)
    if idx >= 0:
        print(kw, '→ 找到, 上下文:', repr(src[max(0,idx-60):idx+40]))
    else:
        print(kw, '→ 未找到')
