# -*- coding: utf-8 -*-
"""样式与段落格式应用：中英文字体、字号、行距、缩进。"""
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.text.run import Run


def iter_runs(par):
    """深度遍历段落内所有 run（含超链接 w:hyperlink、内容控件 w:sdt 内的 run）。

    p.runs 只返回直接子 run，表格/正文里嵌在超链接或内容控件中的文字
    会漏掉，导致字体没统一。这里按 XML 深度遍历。
    """
    for r in par._p.iter(qn("w:r")):
        yield Run(r, par)


def _set_run_font(run, cn_font, en_font, size_pt, bold=None, italic=None, clear_color=True, clear_italic=True):
    """同时设置中文字体（eastAsia）与西文字体，清除字符间距，默认清除颜色与斜体。

    输入文档常见"两端对齐 + 手动加宽字符间距 + 彩色强调/部分加粗/个别斜体"的排版习惯，
    保留会导致每行字数骤减、颜色花哨、加粗/斜体不统一。
    clear_color=False / clear_italic=False 时保留原文（高级选项开关）。
    """
    run.font.name = en_font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        from docx.oxml import OxmlElement
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), en_font)
    rfonts.set(qn("w:hAnsi"), en_font)
    rfonts.set(qn("w:eastAsia"), cn_font)
    sp = rpr.find(qn("w:spacing"))
    if sp is not None:
        rpr.remove(sp)
    if clear_color:
        col = rpr.find(qn("w:color"))
        if col is not None:
            rpr.remove(col)
    u = rpr.find(qn("w:u"))
    if u is not None:
        # 下划线多为从网页/富文本复制残留，参考文献与正文规范均不需要，强制清除
        rpr.remove(u)
    run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    # 斜体：默认清除（输入文档常有个别 run 斜体残留）；preserve_italics 开启或显式 italic=True 才保留
    if clear_italic:
        run.font.italic = False
    elif italic is not None:
        run.font.italic = bool(italic)


def set_paragraph_format(par, cfg_par):
    """按配置设置段落格式：行距、段前段后、对齐。"""
    pf = par.paragraph_format
    ls = cfg_par.get("line_spacing", 1.5)
    pf.line_spacing = ls
    pf.space_before = Pt(cfg_par.get("space_before_pt", 0))
    pf.space_after = Pt(cfg_par.get("space_after_pt", 0))
    align = cfg_par.get("align", "justify")
    pf.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
                    "left": WD_ALIGN_PARAGRAPH.LEFT,
                    "center": WD_ALIGN_PARAGRAPH.CENTER,
                    "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]


def set_first_line_indent(par, chars: int):
    """按字符数设置首行缩进（用 w:ind w:firstLineChars，Word 原生按字符缩进）。"""
    pPr = par._p.get_or_add_pPr()
    ind = pPr.find(qn("w:ind"))
    if ind is None:
        from docx.oxml import OxmlElement
        ind = OxmlElement("w:ind")
        pPr.append(ind)
    ind.set(qn("w:firstLineChars"), str(chars * 100))
    # 同时给个以字符宽度为单位的兜底（非中文字符场景）
    ind.set(qn("w:firstLine"), "0")


def format_heading(par, cfg, level: int):
    """套用标题格式（level 1/2/3），标题顶格（清输入参差的缩进）。"""
    f = cfg["fonts"]["heading%d" % level]
    set_paragraph_format(par, cfg["paragraph"])
    par.paragraph_format.line_spacing = cfg["paragraph"].get("line_spacing", 1.5)
    pf = par.paragraph_format
    pf.space_before = Pt(6 if level == 1 else 3)
    pf.space_after = Pt(6 if level == 1 else 3)
    pf.first_line_indent = Cm(0)  # 标题顶格，清输入缩进
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    for run in iter_runs(par):
        _set_run_font(run, f["cn"], f["en"], f["size_pt"], bold=f.get("bold", True), italic=False,
                      clear_color=not cfg.get("preserve_colors", False),
                      clear_italic=not cfg.get("preserve_italics", False))
    # 空 run（无文字）也建一个以便样式生效
    if not par.runs:
        run = par.add_run(par.text or "")
        _set_run_font(run, f["cn"], f["en"], f["size_pt"], bold=f.get("bold", True), italic=False,
                      clear_color=not cfg.get("preserve_colors", False))


def format_body(par, cfg):
    """套用正文格式：字体 + 行距 + 首行缩进 2 字符。正文统一不加粗、不加斜体、默认清除颜色。

    同时清 left/right 缩进——输入文档常把列举/分类段带左缩进，保留会缩进参差。
    """
    f = cfg["fonts"]["body"]
    set_paragraph_format(par, cfg["paragraph"])
    pf = par.paragraph_format
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    for run in iter_runs(par):
        _set_run_font(run, f["cn"], f["en"], f["size_pt"], bold=False, italic=False,
                      clear_color=not cfg.get("preserve_colors", False),
                      clear_italic=not cfg.get("preserve_italics", False))
    chars = cfg["paragraph"].get("first_line_indent_chars", 2)
    if chars:
        set_first_line_indent(par, chars)


def format_caption(par, cfg, text: str):
    """套用图/表题注格式（居中，小五/五号）。"""
    f = cfg["fonts"]["caption"]
    pf = par.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.line_spacing = 1.0
    pf.space_before = Pt(3); pf.space_after = Pt(3)
    # 重写文字，保证编号正确
    par.clear()
    run = par.add_run(text)
    _set_run_font(run, f["cn"], f["en"], f["size_pt"], bold=True)


def format_ref_item(par, cfg):
    """套用参考文献条目格式：宋体小四/五号，悬挂缩进可选。"""
    f = cfg["fonts"]["body"]
    pf = par.paragraph_format
    pf.line_spacing = cfg["paragraph"].get("line_spacing", 1.5)
    pf.space_after = Pt(0)
    for run in iter_runs(par):
        _set_run_font(run, f["cn"], f["en"], f["size_pt"])
