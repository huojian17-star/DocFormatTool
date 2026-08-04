# -*- coding: utf-8 -*-
"""文本结构识别器：把任意格式的论文文本转成结构化段落列表。

输入：.txt / .md / .docx（docx 仅提取文字）
输出：[{"type": <type>, "text": str, "meta": {...}}, ...]

type: cover_title | heading1 | heading2 | heading3 | abstract_heading |
      abstract_body | keywords | ref_heading | ref_item | appendix |
      caption | body | blank
"""
import os
import re

CN_NUM_RE = re.compile(r"^第\s*[\d一二三四五六七八九十百千零〇]+\s*[章节篇卷]")
NUM_H1_RE = re.compile(r"^\d{1,2}\s*[、.．](?!\d)")  # 点/顿号后不能跟数字（"4.22" 是日期非标题）
# Word 自动编号标题："1 引言"（数字+空格+文字）
NUM_H1_SPACE_RE = re.compile(r"^\d{1,2}\s{1,3}[^\d.．、，,；;:]")
NUM_H2_RE = re.compile(r"^\d{1,2}[.．]\d{1,2}\s*[、\s]")
NUM_H3_RE = re.compile(r"^\d{1,2}[.．]\d{1,2}[.．]\d{1,2}\s*[、\s]")
CN_LIST_RE = re.compile(r"^[一二三四五六七八九十]{1,3}\s*[、.．]")
PAREN_H1_RE = re.compile(r"^[（(]\s*[\d一二三四五六七八九十]{1,3}\s*[）)]")
ABSTRACT_RE = re.compile(r"^\s*(摘\s*要)\s*$")
ABSTRACT_EN_RE = re.compile(r"^\s*(Abstract|ABSTRACT)\s*$")
ABSTRACT_EN_INLINE_RE = re.compile(r"^\s*(Abstract|ABSTRACT)\s*[:：]")
KEYWORDS_RE = re.compile(r"^\s*(关键词|KEY\s*WORDS|Keywords)\s*[:：]?\s*")
REF_HEAD_RE = re.compile(r"^\s*参考文献\s*[:：]?\s*$")
REF_ITEM_RE = re.compile(r"^\s*\[\d+\]\s*")
REF_TYPE_RE = re.compile(r"\[\s*[JMCADPNRT]\s*\]")
APPENDIX_RE = re.compile(r"^\s*附\s*录\s*$")
THANKS_RE = re.compile(r"^\s*致\s*谢\s*$")
CAPTION_RE = re.compile(r"^\s*[图表]\s*\d{1,2}([-.．]\d{1,2}){0,2}\s*[^\n]{0,60}$")
IMAGE_MD_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")


def parse_text(text: str, md_mode: bool = False):
    """解析纯文本 → 结构列表（支持 md 代码块、md 表格、图片、标题等）。
    md_mode=True 时按 Markdown 语义识别（"1. xxx" 为有序列表）。"""
    out = []
    lines = text.splitlines()
    pending_blank = 0
    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        # ---- LaTeX 块级公式：$$...$$（单行或跨行）----
        if "$$" in s:
            if s.count("$$") >= 2:
                latex = s.split("$$")[1].strip()
                _flush_blank(out, pending_blank)
                pending_blank = 0
                out.append({"type": "latex_block", "text": latex})
                i += 1
                continue
            if s.startswith("$$"):
                acc = [s[2:]]
                i += 1
                while i < len(lines) and "$$" not in lines[i]:
                    acc.append(lines[i])
                    i += 1
                if i < len(lines):
                    acc.append(lines[i].split("$$")[0])
                i += 1
                _flush_blank(out, pending_blank)
                pending_blank = 0
                out.append({"type": "latex_block", "text": "\n".join(acc).strip()})
                continue
        # ---- 代码块：``` 开头到下一个 ``` ----
        if s.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            _flush_blank(out, pending_blank)
            pending_blank = 0
            out.append({"type": "code_block", "text": "\n".join(code_lines)})
            continue
        # ---- md 表格：含 | 且下一行是分隔行（|---|）----
        if s.count("|") >= 2 and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            rows = []
            while i < len(lines) and lines[i].strip().count("|") >= 2:
                rows.append(_split_table_row(lines[i]))
                i += 1
            _flush_blank(out, pending_blank)
            pending_blank = 0
            out.append({"type": "md_table", "rows": rows})
            continue
        # ---- 普通行 ----
        if not s:
            pending_blank += 1
            i += 1
            continue
        t, text_out = _classify(s, md_mode=md_mode)
        # "摘要：xxx" 拆成 摘要标题 + 摘要正文
        if t == "abstract_heading" and text_out.startswith("摘") and "：" in s[:6]:
            inner = re.sub(r"^摘\s*要\s*[:：]\s*", "", s)
            _flush_blank(out, pending_blank)
            pending_blank = 0
            out.append({"type": "abstract_heading", "text": "摘  要"})
            out.append({"type": "abstract_body", "text": inner})
            i += 1
            continue
        _flush_blank(out, pending_blank)
        pending_blank = 0
        out.append({"type": t, "text": text_out})
        i += 1
    return _mark_cover(out)


def _flush_blank(out, n):
    if n and out and out[-1]["type"] != "blank":
        out.append({"type": "blank", "text": ""})


def _is_table_sep(line: str) -> bool:
    """md 表格分隔行：|:---:||---| 等。"""
    s = line.strip()
    if "|" not in s:
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return bool(cells) and all(re.match(r"^:?-{2,}:?$", c) for c in cells)


def _split_table_row(line: str) -> list:
    """md 表格行 → 单元格列表。"""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _mark_cover(structs):
    """把文档开头（摘要/关键词/首个标题之前）的连续非空段标记为封面行。"""
    for i, st in enumerate(structs):
        if st["type"] == "blank":
            continue
        if st["type"] in ("abstract_heading", "keywords", "md_table", "code_block") \
                or is_heading(st["type"]):
            break
        st["type"] = "cover"
    return structs


def parse_file(path: str):
    """按扩展名解析文件 → 结构列表。"""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        with open(path, encoding="utf-8", errors="replace") as f:
            return parse_text(f.read(), md_mode=(ext == ".md"))
    if ext == ".docx":
        from docx import Document
        doc = Document(path)
        lines = []
        for p in doc.paragraphs:
            if p.style.name.startswith("Heading"):
                level = p.style.name.split()[-1]
                lines.append("#" * min(int(level), 3) + " " + p.text)
            elif p.text.strip():
                lines.append(p.text)
            else:
                lines.append("")
        return parse_text("\n".join(lines))
    raise ValueError("不支持的输入格式: %s（支持 .txt / .md / .docx）" % ext)


# 标题最大长度（超过视为正文——防"1. 被解释变量：xxx长句"列举误判为章节标题）
_HEADING_MAX_LEN = 60
# 以句读结尾的句子不判标题（正文句子的特征，宁可漏判不可误判）
_TERMINAL_PUNCT = "。．.，,；;！？!?、"
# 标题内容首字若为量词/虚词/动词开头 → 正文（"3 个样本""2.5 元""1.1 节回顾"都是量词/虚词开头）
_NOT_HEADING_FIRST = set(
    "个种元次张份名岁倍条段类台套件位项斤公里第节显mz"
    "了的是在和对从把被将看有进进行为与及或都"
    "我们你们他们它们这那"
)
_HEADING_PREFIX_RE = re.compile(r"^[第\d.．一二三四五六七八九十百千零〇（(]+[章篇卷、:：\s]*")
# 脚注/注释特征：编号后接长句内容（非标题短句）——"1. 数据来源于国家统计局：https://..." 
# 是脚注/资料来源，不是三级标题
_NOTE_CONTENT_RE = re.compile(
    r"来源于|数据来源[:：]|资料来源[:：]|注[:：]|注释|脚注|尾注|参见|https?://|www\.",
    re.IGNORECASE)


def _is_heading_like(s: str, matched: bool, dotted: bool = False) -> bool:
    """标题判定：命中编号模式 + 长度上限 + 不以句读结尾 + 内容首字非量词/虚词。

    dotted=True（点式编号 x.y / x.y.z）：跳过首字量词检查——
    避免误伤"2.1.4 个性化学习"（"个"是量词字，误判为列举）。
    """
    if not matched:
        return False
    if len(s) > _HEADING_MAX_LEN:
        return False
    if s[-1] in _TERMINAL_PUNCT:
        return False
    # 编号后的内容首字：量词/虚词/代词开头 → 不是标题（如"3 个样本""2.5 元""1.1 节回顾"）
    body = _HEADING_PREFIX_RE.sub("", s, count=1).lstrip(" ")
    if body and body[0] in _NOT_HEADING_FIRST and not dotted:
        return False
    # 脚注/注释特征（URL/资料来源/注：等）→ 非标题
    if _NOTE_CONTENT_RE.search(s):
        return False
    # 数字 0 开头 → 小数/统计值，非标题编号（"0.05 显著性""0 个样本"）
    m = re.match(r"^\s*0", s)
    if m:
        return False
    # "4.22，" 日期+逗号 → 时间轴/叙述，非标题
    if re.match(r"^\d{1,2}[.．]\d{1,2}[，,]", s):
        return False
    return True


def _classify(s: str, md_mode: bool = False):
    """单行分类 → (type, text)。md_mode=True 时按 Markdown 语义（"1. xxx" 是有序列表非标题）。"""
    # Markdown 图片
    m = IMAGE_MD_RE.match(s)
    if m:
        return ("image", s)

    # 摘要 / 关键词 / 参考文献 / 附录
    if ABSTRACT_RE.match(s) or re.match(r"^摘\s*要\s*[:：]", s) \
            or ABSTRACT_EN_RE.match(s) or ABSTRACT_EN_INLINE_RE.match(s):
        return ("abstract_heading", s)
    if KEYWORDS_RE.match(s):
        return ("keywords", s)
    if REF_HEAD_RE.match(s):
        return ("ref_heading", s)
    if REF_ITEM_RE.match(s):
        return ("ref_item", s)
    if REF_TYPE_RE.search(s) and len(s) <= 100 and re.search(r"[.．]\s*$", s):
        # 含 [J]/[M] 文献类型标识且以句号结尾 → 参考文献条目（无论有无编号）
        return ("ref_item", s)
    if APPENDIX_RE.match(s) or THANKS_RE.match(s):
        return ("appendix", s)

    # 标题层级：先三级再二级再一级（保守判定：编号 + 短行 + 不以句读结尾）
    if _is_heading_like(s, NUM_H3_RE.match(s), dotted=True):
        return ("heading3", s)
    if _is_heading_like(s, NUM_H2_RE.match(s), dotted=True):
        return ("heading2", s)
    # H1：md 模式排除"数字. "句点式（有序列表）；"数字 空格"式仍判标题
    if md_mode:
        h1_matched = (CN_NUM_RE.match(s) or CN_LIST_RE.match(s)
                      or PAREN_H1_RE.match(s) or NUM_H1_SPACE_RE.match(s))
    else:
        h1_matched = (CN_NUM_RE.match(s) or NUM_H1_RE.match(s) or NUM_H1_SPACE_RE.match(s)
                      or CN_LIST_RE.match(s) or PAREN_H1_RE.match(s))
    if _is_heading_like(s, h1_matched):
        return ("heading1", s)

    # Markdown 标题标记
    md = re.match(r"^(#{1,3})\s+(.*)$", s)
    if md:
        lvl = len(md.group(1))
        return ("heading%d" % lvl, md.group(2))

    # 图/表题注（内容首字为动词/虚词 → 叙述句非题注："图 1 展示的是…"）
    if CAPTION_RE.match(s) and len(s) <= 70:
        body = re.sub(r"^[图表]\s*\d{1,2}([-.．]\d{1,2}){0,2}\s*", "", s)
        if body and body[0] not in "展示显示给出表明是的那为见如列出如下":
            return ("caption", s)

    # 封面大标题：整个文档的第一个非空段，且很短
    return ("body", s)


def is_heading(t: str) -> bool:
    return t in ("heading1", "heading2", "heading3")


_UNCERTAIN_RE = re.compile(r"^\d{1,2}[.．]\s+\S")


def is_uncertain(s: str, md_mode: bool = False) -> bool:
    """低置信度判定：引擎拿不准的段落（排版前让用户批量确认）。

    当前场景：非 md 模式下"数字. 内容"短行——既可能是标题（"1. 引言"）
    也可能是列举（"1. 优点：效率高"），引擎默认判标题，但存在误判风险。
    md 模式下已按有序列表处理，无需确认。
    """
    s = (s or "").strip()
    if md_mode:
        return False
    if _UNCERTAIN_RE.match(s) and len(s) <= 40:
        return True
    return False
