# -*- coding: utf-8 -*-
"""forced_map 改文本匹配：键=段落全文（strip 后），引擎内部匹配，不依赖索引（目录插入会偏移索引）"""
src = open(r'engine\build_docx.py', encoding='utf-8').read()

# 1) 调用点：传 forced_map 本身（不再 get(idx)）
old = '''        in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map,
                                           forced_map.get(str(idx), None))'''
new = '''        in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map,
                                           forced_map)'''
assert old in src, '调用点未找到'
src = src.replace(old, new, 1)
print('调用点改为传 forced_map')

# 2) 签名 forced_type → forced_map
old2 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None, outline_map=None,
                      forced_type=None):'''
new2 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None, outline_map=None,
                      forced_map=None):'''
assert old2 in src, '签名未找到'
src = src.replace(old2, new2, 1)
print('签名改为 forced_map')

# 3) 函数内：text 算好后按文本匹配；移除 debug 残留
old3 = '''    text = para_text(p_el).strip()
    p = Paragraph(p_el, None)

    # 强信号优先：'''
new3 = '''    text = para_text(p_el).strip()
    p = Paragraph(p_el, None)

    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定（键=段落全文）
    forced_type = forced_map.get(text) if forced_map else None
    if forced_type:
        t = forced_type
        if t.startswith("heading"):
            S.format_heading(p, cfg, int(t[-1]))
            _set_pstyle(p_el, "Heading" + t[-1])
            st["h" + t[-1]] = st.get("h" + t[-1], 0) + 1
        else:
            S.format_body(p, cfg)
        st["paras"] = st.get("paras", 0) + 1
        return _in_cover, _in_toc

    # 强信号优先：'''
assert old3 in src, '插入点未找到'
src = src.replace(old3, new3, 1)
print('文本匹配逻辑已注入')

# 4) 移除旧的 forced_type 块（含 debug 残留）
old4 = '''    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定

    if forced_type and __debug__:
        pass
    if forced_type:
        t = forced_type
        if t.startswith("heading"):
            S.format_heading(p, cfg, int(t[-1]))
            _set_pstyle(p_el, "Heading" + t[-1])
            st["h" + t[-1]] = st.get("h" + t[-1], 0) + 1
        else:
            S.format_body(p, cfg)
        st["paras"] = st.get("paras", 0) + 1
        return _in_cover, _in_toc

    # 强信号优先：'''
assert old4 in src, '旧块未找到'
src = src.replace(old4, '''    # 强信号优先：''', 1)
print('旧块已移除')

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('完成')
