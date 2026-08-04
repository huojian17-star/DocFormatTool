# -*- coding: utf-8 -*-
"""把强信号块从封面区前移到封面区后（封面区段落优先走封面逻辑）"""
src = open(r'engine\build_docx.py', encoding='utf-8').read()

block = '''    # 强信号优先：输入段落已带标题样式/大纲级别 → 直接采用，不靠正则猜（防误判漏判）
    style_lvl = _style_heading_level(p_el, doc, outline_map)
    if style_lvl and not _in_table(p_el):
        S.format_heading(p, cfg, style_lvl)
        _set_pstyle(p_el, "Heading%d" % style_lvl)
        st["h%d" % style_lvl] = st.get("h%d" % style_lvl, 0) + 1
        st["paras"] = st.get("paras", 0) + 1
        return _in_cover, _in_toc

'''
assert block in src, '强信号块未找到'
src = src.replace(block, '', 1)
print('已移除原位置')

anchor = '''    # 封面区：正文开始前的连续短段，只统一字体（布局/字号不动，安全第一）
    if _in_cover:'''
# 封面区结束（首个非封面段）之后、目录区之前插入
tail = '''        # 首个非封面段：结束封面区，按正常流程继续
    _in_cover = False

'''
assert tail in src, '封面区结束点未找到'
src = src.replace(tail, tail + block, 1)
print('已移到封面区之后')

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
