# -*- coding: utf-8 -*-
"""给 build_docx.py 注入：输入样式强信号读取（pStyle/outlineLvl）——学生文档已带标题样式/大纲级别时直接采用，不靠正则猜"""
import re

src = open(r'engine\build_docx.py', encoding='utf-8').read()

# ---- 1) 新增函数：读取段落已有样式信号 ----
if 'def _style_heading_level' not in src:
    anchor = 'def _in_table(p_el) -> bool:'
    idx = src.find(anchor)
    assert idx > 0, '找不到 _in_table'
    insert_at = src.find('\n\n', idx)
    new_fn = '''

_STYLE_HEADING_MAP = {
    "Heading1": 1, "Heading2": 2, "Heading3": 3, "Heading4": 4,
    "heading 1": 1, "heading 2": 2, "heading 3": 3, "heading 4": 4,
    "标题1": 1, "标题2": 2, "标题3": 3, "标题4": 4,
    "标题 1": 1, "标题 2": 2, "标题 3": 3, "标题 4": 4,
    "Title": 1, "标题": 1,
}
# 样式 id 正则（WPS/Word 中文样式常以样式名本身作为 id）
_STYLE_ID_RE = re.compile(r"^(Heading|标题|Title)[1-4]?$", re.IGNORECASE)


def _style_heading_level(p_el, doc=None, outline_map=None) -> int:
    """读取段落已带的标题样式/大纲级别（强信号，比正则可靠）。

    返回 1~3 或 0（无标题信号）。优先级：
    1. 段落 pStyle 名直接匹配 Heading1-3 / 标题 1-3 / Title
    2. 样式定义里的 w:outlineLvl（大纲级别 0-2 → 标题1-3）
    """
    pPr = p_el.find(qn("w:pPr"))
    if pPr is None:
        return 0
    ps = pPr.find(qn("w:pStyle"))
    if ps is not None:
        sid = ps.get(qn("w:val")) or ""
        if sid in _STYLE_HEADING_MAP:
            lvl = _STYLE_HEADING_MAP[sid]
            return lvl if lvl <= 3 else 0
        if _STYLE_ID_RE.match(sid.strip()):
            # 样式名含 Heading/标题 但不在表内（如"标题 1.5"变体）→ 查大纲级别
            if outline_map and sid in outline_map:
                lvl = outline_map[sid]
                return lvl if 1 <= lvl <= 3 else 0
    # 段落直接带 outlineLvl（无样式但手工设了大纲级别）
    ol = pPr.find(qn("w:outlineLvl"))
    if ol is not None:
        try:
            lvl = int(ol.get(qn("w:val")) or "9") + 1  # outlineLvl 0→标题1
            return lvl if 1 <= lvl <= 3 else 0
        except ValueError:
            pass
    return 0


def _build_outline_map(doc) -> dict:
    """解析 styles.xml：样式 id → 大纲级别（0 基）。供标题样式继承时使用。"""
    m = {}
    if doc is None:
        return m
    try:
        for st in doc.styles.element.findall(qn("w:style")):
            sid = st.get(qn("w:styleId")) or ""
            pPr = st.find(qn("w:pPr"))
            if pPr is None:
                continue
            ol = pPr.find(qn("w:outlineLvl"))
            if ol is not None:
                try:
                    m[sid] = int(ol.get(qn("w:val")) or "9") + 1
                except ValueError:
                    pass
    except Exception:
        pass
    return m


'''
    src = src[:insert_at] + new_fn + src[insert_at:]
    print('已注入 _style_heading_level + _build_outline_map')

# ---- 2) _reformat_paragraph 开头：classify 之前先查输入样式强信号 ----
old = '''    text = para_text(p_el).strip()
    p = Paragraph(p_el, None)

    # 封面区：'''
new = '''    text = para_text(p_el).strip()
    p = Paragraph(p_el, None)

    # 强信号优先：输入段落已带标题样式/大纲级别 → 直接采用，不靠正则猜（防误判漏判）
    style_lvl = _style_heading_level(p_el, doc, outline_map)
    if style_lvl and not _in_table(p_el):
        S.format_heading(p, cfg, style_lvl)
        _set_pstyle(p_el, "Heading%d" % style_lvl)
        st["h%d" % style_lvl] = st.get("h%d" % style_lvl, 0) + 1
        st["paras"] = st.get("paras", 0) + 1
        return _in_cover, _in_toc

    # 封面区：'''
assert old in src, '未找到插入点'
src = src.replace(old, new, 1)
print('已注入强信号优先逻辑')

# ---- 3) _reformat_existing_core：构造 outline_map 传入 ----
old2 = '''    in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc)'''
new2 = '''    in_cover, in_toc = _reformat_paragraph(p_el, cfg, in_cover, stats, in_toc, next_text, doc, outline_map)'''
assert old2 in src, '调用点未找到'
src = src.replace(old2, new2, 1)

old3 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None):'''
new3 = '''def _reformat_paragraph(p_el, cfg, _in_cover=False, stats=None, _in_toc=False, next_text="", doc=None, outline_map=None):'''
assert old3 in src, '签名未找到'
src = src.replace(old3, new3, 1)

# 调用处构造 outline_map
old4 = '''    in_cover = True'''
new4 = '''    in_cover = True
    outline_map = _build_outline_map(doc)  # 输入样式的大纲级别索引（强信号）'''
assert old4 in src, 'outline_map 构造点未找到'
src = src.replace(old4, new4, 1)
print('已接线 outline_map')

open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src)
print('写入完成')
