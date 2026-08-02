# -*- coding: utf-8 -*-
"""模板分析器：从学校下发的 .docx 模板中提取格式规则，生成配置 JSON。

支持两类模板：
1. 规则说明型 —— 模板内用文字写明"题目（宋体，小二号字，加粗，居中）"
2. 示范排版型 —— 模板直接排好示例段落，从 run 的实际格式提取
"""
import json
import re
import os

from docx import Document

# 中文字号 → 磅值（匹配时按此顺序：长的/带"小"的优先，避免"小四"被"四号"抢）
CHINESE_SIZE_PT = {
    "初号": 42, "小初": 36, "一号": 26, "小一": 24, "二号": 22, "小二": 18,
    "三号": 16, "小三": 15, "四号": 14, "小四": 12, "五号": 10.5, "小五": 9,
    "六号": 7.5, "小六": 6.5, "七号": 5.5, "八号": 5,
}
_SIZE_RE = re.compile(r"(小初|小一|小二|小三|小四|小五|小六|小七|小八|初号|一号|二号|三号|四号|五号|六号|七号|八号)")
CN_FONTS = ["仿宋_GB2312", "宋体_GB2312", "华文中宋", "微软雅黑", "黑体", "宋体", "楷体", "仿宋", "隶书", "幼圆", "华文楷体"]

# 模板说明文字里的"锚词" → 配置角色
ROLE_ANCHORS = [
    ("title", ["封面标题", "论文题目", "题目（", "题目(", "题 目", "题目"]),
    ("abstract_heading", ["摘要"]),
    ("abstract_body", ["摘要内容"]),
    ("keywords", ["关键词"]),
    ("body_heading", ["标题行", "正文标题", "小标题"]),
    ("body", ["正文内容", "正文部分"]),
    ("ref_heading", ["参考文献（", "参考文献("]),
    ("ref_item", ["参考文献条目"]),
    ("appendix", ["附录"]),
    ("header", ["页眉"]),
    ("caption", ["图题注", "表题注", "图表标题"]),
]


def parse_rule_text(text: str):
    """解析一句规则说明，如 '题目（宋体，小二号字，加粗，居中）' 或
    '正文部分（标题行用小四号字加粗，正文内容用小四号字）'。

    返回 [(role, {"font":.., "size_pt":.., "bold":.., "align":..}), ...]
    """
    roles = []
    # 找出锚词
    role_hits = []
    for role, anchors in ROLE_ANCHORS:
        for a in anchors:
            if a in text:
                role_hits.append((role, a))
                break
    if not role_hits:
        # 无锚词但带括号规则的（如 '[1] ×××（五号字）'）
        if "（" in text and "）" in text:
            inner = text.split("（", 1)[1].split("）", 1)[0]
            rules = _parse_inner(inner)
            roles.append(("ref_item", rules[0] if rules else {}))
        return roles

    # 取第一个命中锚词，切出括号内规则文本
    role, anchor = role_hits[0]
    rest = text.split(anchor, 1)[1]
    inner = ""
    if "（" in rest and "）" in rest:
        inner = rest.split("（", 1)[1].split("）", 1)[0]
    else:
        inner = rest.strip(" ：:")
    if not inner:
        return roles

    # 括号内可能含多套规则："标题行用小四号字加粗，正文内容用小四号字"
    parts = re.split(r"[，,；;]", inner)
    sub_rules = [_parse_inner(p) for p in parts if p.strip()]
    for sr in sub_rules:
        if not sr:
            continue
        r = sr[0]
        seg = sr[1]  # 子句文本
        if "标题" in seg or "行" in seg and role in ("body", "body_heading"):
            roles.append(("body_heading", r))
        elif "内容" in seg:
            roles.append(("body", r))
        else:
            roles.append((role, r))
    return roles


def _parse_inner(seg: str):
    """解析括号内一个子句，如 '小二号字加粗居中' → ({size_pt:18, bold:True, align:center}, seg)。"""
    rule = {}
    m = _SIZE_RE.search(seg)
    if m:
        rule["size_pt"] = CHINESE_SIZE_PT[m.group(1)]
    for f in CN_FONTS:
        if f in seg:
            rule["font"] = f
            break
    if "加粗" in seg or "粗体" in seg:
        rule["bold"] = True
    if "居中" in seg:
        rule["align"] = "center"
    if "居左" in seg or "左对齐" in seg:
        rule["align"] = "left"
    if "行距" in seg:
        m = re.search(r"行距[^\d]*([\d.]+)", seg)
        if m:
            rule["line_spacing"] = float(m.group(1))
    return (rule, seg)


def analyze(template_path: str) -> dict:
    """分析模板 docx，产出符合 engine/config.py DEFAULT 结构的配置 dict。"""
    doc = Document(template_path)
    cfg = {}

    # ---- 页面 ----
    sec0 = doc.sections[0]
    margins = {
        "top": round(sec0.top_margin.cm, 2),
        "bottom": round(sec0.bottom_margin.cm, 2),
        "left": round(sec0.left_margin.cm, 2),
        "right": round(sec0.right_margin.cm, 2),
    }
    w = round(sec0.page_width.cm, 1)
    h = round(sec0.page_height.cm, 1)
    paper = "A4" if (w, h) == (21.0, 29.7) else "%.1fx%.1fcm" % (w, h)
    cfg["page"] = {"paper": paper, "margins_cm": margins}

    # ---- 规则说明型：逐段解析说明文字 ----
    rules = {}   # role -> rule
    example = {} # role -> 示例 run 格式（示范排版型兜底）
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        # 蓝色说明文字通常在 run 上带颜色；有格式术语的段优先当说明
        if ("（" in t or "(" in t) and any(k in t for k in ("号", "字体", "加粗", "居中", "行距", "粗体")):
            for role, r in parse_rule_text(t):
                if role:
                    rules.setdefault(role, {}).update(r)
        # 示范排版型：有实际文字且带格式的段，记录特征
        elif p.runs and t and not re.match(r"^[\[（(【]", t) and len(t) < 80:
            _collect_example(example, p, t)

    # 示范兜底：如果某角色没从文字拿到规则，用示例段格式
    _apply_examples(rules, example)

    # ---- 组装成 config ----
    cfg["fonts"] = _fonts_from_rules(rules)
    t_rule = rules.get("title") or rules.get("封面标题") or {}
    cfg["cover"] = {"enabled": True, "title_size_pt": t_rule.get("size_pt", 26)}
    if rules.get("abstract_heading"):
        cfg["abstract"] = {"heading_text": "摘  要", "keywords_label": "关键词：", "keywords_sep": "；"}
    if rules.get("ref_heading"):
        cfg["references"] = {"heading_text": "参考文献"}
    if rules.get("caption"):
        cfg["captions"] = {"figure": "图{chapter}-{num}", "table": "表{chapter}-{num}"}
    cfg["headings"] = {"numbering": False}
    cfg["header_footer"] = {"header_text": "", "footer_style": "center"}
    return cfg


def _collect_example(example, p, text):
    """记录示范排版型段落：按文本特征归角色。"""
    size = None
    fonts = set()
    bold = None
    align = p.alignment
    for r in p.runs[:3]:
        if r.font.size:
            size = r.font.size.pt
        if r.font.bold is not None:
            bold = bold or r.font.bold
        en = r.font.name
        if en:
            fonts.add(en)
    feat = {"size_pt": size, "bold": bold, "align": align}
    if text in ("摘 要", "摘要") or text.startswith("摘 要"):
        example.setdefault("abstract_heading", {}).update(feat)
    elif text.startswith("关键词"):
        example.setdefault("keywords", {}).update(feat)
    elif text in ("参考文献", "参考文献："):
        example.setdefault("ref_heading", {}).update(feat)
    elif text in ("附录",):
        example.setdefault("appendix", {}).update(feat)
    elif re.match(r"^\[?\d+[\]\]]", text) or re.match(r"^\d+\.\s", text):
        example.setdefault("ref_item", {}).update(feat)
    elif text.startswith("目  录") or text.startswith("目录"):
        example.setdefault("toc", {}).update(feat)
    elif align is not None and str(align) == "CENTER (1)" and size and size >= 14 and bold:
        example.setdefault("title", {}).update(feat)


def _apply_examples(rules, example):
    for role, feat in example.items():
        if role not in rules:
            rules[role] = {}
        if "size_pt" not in rules[role] and feat.get("size_pt"):
            rules[role]["size_pt"] = feat["size_pt"]
        if "bold" not in rules[role] and feat.get("bold") is not None:
            rules[role]["bold"] = feat["bold"]


def _fonts_from_rules(rules):
    """角色规则 → fonts 配置节。"""
    body = rules.get("body", {})
    body_h = rules.get("body_heading", {}) or rules.get("title", {})
    ref = rules.get("ref_item", {})
    fonts = {
        "body": {"cn": body.get("font", "宋体"), "en": "Times New Roman",
                 "size_pt": body.get("size_pt", 12)},
        "heading1": {"cn": (body_h.get("font") or rules.get("title", {}).get("font") or "黑体"),
                     "en": "Times New Roman",
                     "size_pt": body_h.get("size_pt") or rules.get("title", {}).get("size_pt") or 14,
                     "bold": body_h.get("bold", True)},
        "heading2": {"cn": "黑体", "en": "Times New Roman", "size_pt": 12, "bold": True},
        "heading3": {"cn": "黑体", "en": "Times New Roman", "size_pt": 12, "bold": True},
        "caption": {"cn": "宋体", "en": "Times New Roman", "size_pt": 10.5},
        "header": {"cn": "宋体", "en": "Times New Roman", "size_pt": 9},
        "ref": {"cn": ref.get("font", "宋体"), "en": "Times New Roman",
                "size_pt": ref.get("size_pt", 12)},
    }
    return fonts


def _pick(rules, role, key, default):
    return rules.get(role, {}).get(key, default)


# ---------------- CLI ----------------

def main():
    import argparse
    ap = argparse.ArgumentParser(description="分析学校论文模板，输出格式配置 JSON")
    ap.add_argument("template", help="模板 .docx 路径")
    ap.add_argument("-o", "--out", default=None, help="输出 JSON 路径")
    args = ap.parse_args()

    cfg = analyze(args.template)
    out = args.out or (os.path.splitext(args.template)[0] + "_format.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print("配置已生成 ->", out)
    print(json.dumps(cfg, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
