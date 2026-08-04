# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
i = src.find('def build(')
print('--- build() 中 cover 处理 ---')
for m in re.finditer(r'"cover"', src[i:i + 6000]):
    j = m.start() + i
    print('L%d: %r' % (src[:j].count(chr(10)) + 1, src[max(0, j - 90):j + 130]))
