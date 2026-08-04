# -*- coding: utf-8 -*-
"""ONNX 分类器训练数据采集：遍历 docx 文档，提取段落特征 + 引擎角色标签 → JSONL。
特征与角色都由确定性规则产生（弱监督），量靠现有文档积累，质靠弹窗人工确认补充。

用法: python collect_samples.py <目录或文件> [-o samples.jsonl]
"""
import os, sys, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from docx import Document
from docx.oxml.ns import qn
import engine.infer as infer
from engine.build_docx import para_text

# ---- 特征提取（与 ONNX 分类器训练对齐，纯文本特征，推理时无需 docx 结构） ----
def features(s: str) -> dict:
    s = (s or "").strip()
    f = {
        "len": len(s),
        "ends_punct": 1 if s and s[-1] in "。．.，,；;！？!?、：:" else 0,
        "has_url": 1 if re.search(r"https?://|www\.", s) else 0,
        "has_ref_type": 1 if re.search(r"\[[JMCNDPS]\](?:\.|$)", s) else 0,  # [J]/[M] 文献类型
        "has_note_word": 1 if re.search(r"来源于|数据来源[:：]|资料来源[:：]|注[:：]|注释|脚注|尾注|参见", s) else 0,
        "num_h3": 1 if re.match(r"^\d{1,2}[.．]\d{1,2}[.．]\d{1,2}", s) else 0,
        "num_h2": 1 if re.match(r"^\d{1,2}[.．]\d{1,2}\s", s) else 0,
        "num_h1": 1 if re.match(r"^第[一二三四五六七八九十百]+章", s) else 0,
        "cn_num": 1 if re.match(r"^[一二三四五六七八九十]+、", s) else 0,
        "paren_cn": 1 if re.match(r"^（[一二三四五六七八九十]+）", s) else 0,
        "paren_digit": 1 if re.match(r"^（\d+）|^\(\d+\)", s) else 0,
        "digit_space": 1 if re.match(r"^\d{1,2}\s+\S", s) else 0,
        "digit_dot": 1 if re.match(r"^\d{1,2}[.．]\s*\S", s) else 0,
        "md_hash": 1 if re.match(r"^#{1,3}\s", s) else 0,
        "abstract": 1 if re.match(r"^摘\s*要\s*[:：]?", s) or re.match(r"^Abstract\b", s) else 0,
        "keywords": 1 if re.match(r"^关键词[:：]", s) or re.match(r"^Keywords?\b", s) else 0,
        "ref_head": 1 if re.match(r"^参考文献$|^参\s*考\s*文\s*献\s*$", s) else 0,
        "appendix": 1 if re.match(r"^致\s*谢|^附\s*录|^Abstract$", s) else 0,
        "first_char_verb": 1 if s and s[0] in "了的是在和对从把被将看有进进行为与及或都我们你们他们它们这那" else 0,
    }
    return f


def collect(path, out_path):
    rows = 0
    with open(out_path, "a", encoding="utf-8") as f:
        if os.path.isdir(path):
            files = [os.path.join(path, x) for x in os.listdir(path)
                     if (x.endswith(".docx") or x.endswith(".txt") or x.endswith(".md"))
                     and not x.startswith("~$")]
        else:
            files = [path] if (path.endswith(".docx") or path.endswith(".txt") or path.endswith(".md")) else []
        for fp in files:
            if fp.endswith(".docx"):
                rows += _collect_docx(fp, f)
            else:
                rows += _collect_txt(fp, f)
    print("累计样本: %d 条 → %s" % (rows, out_path))


def _collect_txt(fp, f):
    """txt/md 按行当段落采集"""
    rows = 0
    try:
        for line in open(fp, encoding="utf-8", errors="ignore"):
            t = line.strip()
            if not t or len(t) < 2:
                continue
            typ, _ = infer._classify(t)
            if typ in ("heading1", "heading2", "heading3", "body", "ref_item",
                       "keywords", "abstract_heading", "ref_heading", "caption", "appendix"):
                rec = {"text": t, "role": typ}
                rec.update(features(t))
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                rows += 1
        print("  %s → %d 段" % (os.path.basename(fp), rows))
    except Exception as e:
        print("  跳过 %s: %s" % (os.path.basename(fp), e))
    return rows


def _collect_docx(fp, f):
    rows = 0
    try:
        doc = Document(fp)
    except Exception as e:
        print("跳过 %s: %s" % (os.path.basename(fp), e))
        return 0
    for p_el in doc.element.body.iter(qn("w:p")):
        t = para_text(p_el).strip()
        if not t:
            continue
        typ, _ = infer._classify(t)
        if typ in ("heading1", "heading2", "heading3", "body", "ref_item",
                   "keywords", "abstract_heading", "ref_heading", "caption", "appendix"):
            rec = {"text": t, "role": typ}
            rec.update(features(t))
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            rows += 1
    print("  %s → %d 段" % (os.path.basename(fp), rows))
    return rows


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="docx 文件或目录")
    ap.add_argument("-o", default=os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data", "samples.jsonl"))
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.o), exist_ok=True)
    collect(a.path, a.o)
