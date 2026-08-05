# -*- coding: utf-8 -*-
import re
p = r'site\make_xhs_1016.py'
src = open(p, encoding='utf-8').read()
pat = re.compile(r'(d\.text\(\([^)]*\), "[^"]*", )(font\([^)]*\), fill=)')
src, n = pat.subn(r'\1font=\2', src)
open(p, 'w', encoding='utf-8', newline='').write(src)
print('修改 %d 处 d.text 调用' % n)
