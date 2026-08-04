# -*- coding: utf-8 -*-
"""在 build_docx.py 中注入：1) _ensure_custom_style 函数  2) 摘要长句/关键词/参考文献条目应用自定义样式"""
import re

src = open(r'engine\build_docx.py', encoding='utf-8').read()

# ---- 1) 在 _set_pstyle 函数后插入 _ensure_custom_style ----
if 'def _ensure_custom_style' not in src:
    anchor = 'def _set_pstyle(p_el, style_id: str):'
    idx = src.find(anchor)
    assert idx > 0, '找不到 _set_pstyle'
    insert_after = src.find('\n\n', idx)
    new_fn = '''

def _ensure_custom_style(doc, style_name, base="Normal"):
    """确保文档存在指定名称的段落样式（WPS 样式集会显示中文样式名）。
    已存在则复用；不存在则基于 base 创建。返回样式对象。"""
    try:
        return doc.styles[style_name]
    except KeyError:
        from docx.enum.style import WD_STYLE_TYPE
        st = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        try:
            st.base_style = doc.styles[base]
        except Exception:
            pass
        return st


'''
    src = src[:insert_after] + new_fn + src[insert_after:]
    print('已注入 _ensure_custom_style')

# ---- 2) abstract_heading 长句：应用"摘要"样式 ----
old_abs = '''    elif t == "abstract_heading" and len(text) > 20:
        # "摘要：xxx" 长句（摘要标题+内容混合）→ 按正文处理，不套标题格式
        S.format_body(p, cfg)'''
new_abs = '''    elif t == "abstract_heading" and len(text) > 20:
        # "摘要：xxx" 长句（摘要标题+内容混合）→ 应用"摘要"自定义样式（样式集可见，非正文）
        _ensure_custom_style(doc, "摘要")
        _set_pstyle(p_el, "摘要")
        S.format_body(p, cfg)'''
assert old_abs in src, 'abstract_heading 长句分支未找到'
src = src.replace(old_abs, new_abs)
print('摘要长句 → "摘要"样式')

# ---- 3) keywords：应用"关键词"自定义样式 ----
old_kw = '''    elif t == "keywords":
        # 关键词行：标签（关键词：/Keywords:/Index Terms—/CCS Concepts •）黑体加粗，内容正文
        kw_fd = cfg["fonts"].get("keywords", cfg["fonts"].get("abstract_heading", cfg["fonts"]["heading1"]))'''
new_kw = '''    elif t == "keywords":
        # 关键词行：应用"关键词"自定义样式（样式集可见，非正文）；标签黑体加粗，内容正文
        _ensure_custom_style(doc, "关键词")
        _set_pstyle(p_el, "关键词")
        kw_fd = cfg["fonts"].get("keywords", cfg["fonts"].get("abstract_heading", cfg["fonts"]["heading1"]))'''
assert old_kw in src, 'keywords 分支未找到'
src = src.replace(old_kw, new_kw)
print('关键词 → "关键词"样式')

# ---- 4) ref_item：应用"参考文献"自定义样式 ----
old_ref = '''    elif t == "ref_item":
        fd = cfg["fonts"].get("ref", cfg["fonts"]["body"])'''
new_ref = '''    elif t == "ref_item":
        # 参考文献条目：应用"参考文献"自定义样式（样式集可见，非正文）
        _ensure_custom_style(doc, "参考文献")
        _set_pstyle(p_el, "参考文献")
        fd = cfg["fonts"].get("ref", cfg["fonts"]["body"])'''
assert old_ref in src, 'ref_item 分支未找到'
src = src.replace(old_ref, new_ref)
print('参考文献条目 → "参考文献"样式')

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('写入完成')
