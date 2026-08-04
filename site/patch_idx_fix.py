# -*- coding: utf-8 -*-
"""修复：forced_map 用 enumerate 的 idx（循环体提前 return 时 para_idx 会不同步）"""
src = open(r'engine\build_docx.py', encoding='utf-8').read()

old = '''        in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map,
                                           forced_map.get(str(para_idx), None))
        para_idx += 1'''
new = '''        in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map,
                                           forced_map.get(str(idx), None))'''
assert old in src, '调用点未找到'
src = src.replace(old, new, 1)

# 删除 para_idx 初始化
old2 = '''    in_cover = True
    para_idx = 0  # 段落索引（低置信确认覆盖表用，保持与 GUI 扫描一致：顶层正文段落顺序）
    outline_map = _build_outline_map(doc)  # 输入样式的大纲级别索引（强信号）'''
new2 = '''    in_cover = True
    outline_map = _build_outline_map(doc)  # 输入样式的大纲级别索引（强信号）'''
assert old2 in src, 'para_idx 初始化未找到'
src = src.replace(old2, new2, 1)

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('已改用 enumerate idx')
