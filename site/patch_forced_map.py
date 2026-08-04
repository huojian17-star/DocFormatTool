# -*- coding: utf-8 -*-
"""注入 forced_map（用户低置信确认覆盖表）支持：
reformat_existing(cfg, src, dst, forced_map=None) → _reformat_paragraph 按索引查覆盖"""
src = open(r'engine\build_docx.py', encoding='utf-8').read()

# 1) reformat_existing 签名
old1 = '''def reformat_existing(cfg: dict, src: str, dst: str) -> dict:
    """改写式排版入口：异常时记录错误日志并抛出（GUI 显示给用户）。"""
    try:
        return _reformat_existing_core(cfg, src, dst)'''
new1 = '''def reformat_existing(cfg: dict, src: str, dst: str, forced_map: dict = None) -> dict:
    """改写式排版入口：异常时记录错误日志并抛出（GUI 显示给用户）。
    forced_map: {段落索引: 强制角色} —— 用户对低置信段落的确认覆盖（如 {"12": "body", "15": "heading1"}）。"""
    try:
        return _reformat_existing_core(cfg, src, dst, forced_map or {})'''
assert old1 in src, 'reformat_existing 签名未找到'
src = src.replace(old1, new1, 1)

# 2) _reformat_existing_core 签名 + 传参
old2 = '''def _reformat_existing_core(cfg: dict, src: str, dst: str) -> dict:'''
new2 = '''def _reformat_existing_core(cfg: dict, src: str, dst: str, forced_map: dict = None) -> dict:
    forced_map = forced_map or {}'''
assert old2 in src, 'core 签名未找到'
src = src.replace(old2, new2, 1)

old3 = '''    in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map)'''
new3 = '''    in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map,
                                           forced_map.get(str(para_idx), None))
        para_idx += 1'''
assert old3 in src, '调用点未找到'
src = src.replace(old3, new3, 1)

# 在循环前初始化 para_idx（找调用点上下文里的 for）
old4 = '''    in_cover = True
    outline_map = _build_outline_map(doc)  # 输入样式的大纲级别索引（强信号）'''
new4 = '''    in_cover = True
    para_idx = 0  # 段落索引（低置信确认覆盖表用，保持与 GUI 扫描一致：顶层正文段落顺序）
    outline_map = _build_outline_map(doc)  # 输入样式的大纲级别索引（强信号）'''
assert old4 in src, 'para_idx 初始化点未找到'
src = src.replace(old4, new4, 1)

# 3) _reformat_paragraph 签名加 forced_type
old5 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None, outline_map=None):'''
new5 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None, outline_map=None,
                      forced_type=None):'''
assert old5 in src, '签名未找到'
src = src.replace(old5, new5, 1)

# 4) 强信号之前：先查 forced_type（用户确认最高优先级）
old6 = '''    # 强信号优先：输入段落已带标题样式/大纲级别 → 直接采用，不靠正则猜（防误判漏判）
    style_lvl = _style_heading_level(p_el, doc, outline_map)'''
new6 = '''    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定
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
assert old6 in src, '强信号块未找到'
src = src.replace(old6, new6, 1)

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('forced_map 注入完成')
