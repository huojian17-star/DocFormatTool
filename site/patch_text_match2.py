# -*- coding: utf-8 -*-
"""分步替换：1) 删旧 forced_type 块  2) 强信号前插入文本匹配  3) 调用点/签名改 forced_map"""
src = open(r'engine\build_docx.py', encoding='utf-8').read()

# 1) 删除旧 forced_type 块（含 debug 残留）
old_block = '''    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定

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

'''
assert old_block in src, '旧块未找到'
src = src.replace(old_block, '', 1)
print('旧块已删除')

# 2) 强信号前插入文本匹配
old2 = '''    # 强信号优先：输入段落已带标题样式/大纲级别 → 直接采用，不靠正则猜（防误判漏判）
    style_lvl = _style_heading_level(p_el, doc, outline_map)'''
new2 = '''    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定（键=段落全文，文本匹配不受目录插入影响）
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

    # 强信号优先：输入段落已带标题样式/大纲级别 → 直接采用，不靠正则猜（防误判漏判）
    style_lvl = _style_heading_level(p_el, doc, outline_map)'''
assert old2 in src, '强信号块未找到'
src = src.replace(old2, new2, 1)
print('文本匹配已插入')

# 3) 调用点：传 forced_map
old3 = '''                                           forced_map.get(str(idx), None))'''
new3 = '''                                           forced_map)'''
assert old3 in src, '调用点未找到'
src = src.replace(old3, new3, 1)
print('调用点已改')

# 4) 签名 forced_type → forced_map
old4 = '''                      forced_type=None):'''
new4 = '''                      forced_map=None):'''
assert old4 in src, '签名未找到'
src = src.replace(old4, new4, 1)
print('签名已改')

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('写入完成')
