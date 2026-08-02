# -*- coding: utf-8 -*-
"""python-docx 底层 XML 操作辅助：域字段、分节、页码格式。

python-docx 未直接暴露：TOC 域、页脚 PAGE 域、节中间的 sectPr、
每节页码格式（罗马/阿拉伯）。这里统一用 lxml 操作。
"""
import copy

from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------- 域字段 ----------

def add_field(paragraph, code: str):
    """在段落末尾追加一个 Word 域（如 PAGE / TOC \\o "1-3" \\h \\z \\u）。"""
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = code
    fld_sep = OxmlElement("w:fldChar"); fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
    for el in (fld_begin, instr, fld_sep, fld_end):
        run._r.append(el)
    return run


def add_toc(paragraph, levels: int = 3):
    """插入目录域（Word 打开后需 Ctrl+A → F9 刷新）。"""
    return add_field(paragraph, 'TOC \\o "1-%d" \\h \\z \\u' % levels)


def add_page_number(paragraph):
    """页脚页码：<页码>（前后不加字）。"""
    add_field(paragraph, "PAGE")


# ---------- 分节 ----------

def insert_section_break_before(paragraph):
    """在指定段落之前插入分节符（新节从该段落开始）。

    原理：在该段落前插入一个带 sectPr 的空段落；该 sectPr 描述"上一节"，
    原 body 末尾的 sectPr 继续作为最后一节（正文节）的配置。
    返回新插入的空段落（它属于上一节）。
    """
    body = paragraph._p.getparent()
    old_sect = body.find(qn("w:sectPr"))
    if old_sect is None:
        # 文档无 body 级 sectPr（罕见）：补一个作为新节配置
        old_sect = OxmlElement("w:sectPr")
        body.append(old_sect)
    new_sect = copy.deepcopy(old_sect)
    new_p = OxmlElement("w:p")
    pPr = OxmlElement("w:pPr")
    pPr.append(new_sect)
    new_p.append(pPr)
    paragraph._p.addprevious(new_p)
    return new_p


def set_section_pgnum(sectPr, fmt: str, start: int = None):
    """设置节的页码格式 fmt: decimal | upperRoman | lowerRoman | none。
    start: 起始页码（None 表示连续）。"""
    pgnum = sectPr.find(qn("w:pgNumType"))
    if pgnum is None:
        pgnum = OxmlElement("w:pgNumType")
        sectPr.append(pgnum)
    if fmt:
        pgnum.set(qn("w:fmt"), fmt)
    if start is not None:
        pgnum.set(qn("w:start"), str(start))
    else:
        pgnum.attrib.pop(qn("w:start"), None)


def section_sectPr(section) -> "lxml element":
    """拿到 python-docx Section 对象对应的 sectPr 元素。"""
    return section._sectPr
