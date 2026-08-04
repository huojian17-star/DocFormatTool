# -*- coding: utf-8 -*-
import re
src = open(r'engine\build_docx.py', encoding='utf-8').read()
# 主循环：找 for ... 段落分类 循环体
i = src.find('    # 目录：文档原无目录')
j = src.find('_ensure_custom_style', i)  # 已注入位置
# 打印 abstract_heading 到 keywords 之间完整循环（含 body else）
k = src.find('for p_el', i)
print('--- 主循环段（分类循环） ---')
# 找 classify 调用处
for m in re.finditer(r'.{30}t, _ = .{10}', src[i:], re.S):
    pass
m = re.search(r'for (p_el|i)[^\n]*\n(?:.*\n){0,3}', src[i:i+6000])
print(m.group(0)[:200] if m else '未找到 for')
# 直接打印 abstract_heading 前后大段
l = src.find('for p_el')
if l < 0:
    l = src.find('for ' + chr(112) + '_el')
print('abstract_heading 出现位置:', src.find('"abstract_heading"'))
