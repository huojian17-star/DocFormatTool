# -*- coding: utf-8 -*-
"""LLM 机器标注（qwen3.5 本地）：批量标注低置信/小类段落 → llm_labels.jsonl。
用法: python llm_label.py [起始批号] [批数]
"""
import json, os, sys, time, urllib.request

OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:latest"  # 9B：A/B 实测准确率明显优于 4b（4b 把"1. 优点：效率高"错判三级标题）
TRAIN_DIR = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data")

SYSTEM = """你是文档结构标注助手。判断每个段落属于哪种角色，只输出 JSON 数组，不要任何解释：
[{"text": "原文", "role": "角色"}]
可选角色：heading1(一级标题 如"一、xxx"/"第一章 xxx")、heading2(二级标题 如"1.1 xxx"/"（一）xxx")、
heading3(三级标题 如"1.1.1 xxx"/"1. xxx")、body(正文段落)、ref_item(参考文献条目"[1] xxx")、
keywords(关键词行"关键词：xxx")、abstract_heading(摘要标题)、caption(图表题注)。
判断要点：标题=短行+编号+不以句号结尾；列举=编号后是短语如"1. 优点：效率高"（不是标题）；
脚注/注释=含"数据来源""资料来源""注：""http"（不是标题）；正文=长句以句号结尾。"""


def call_llm(texts):
    prompt = ("请标注以下 %d 个段落，逐条输出 JSON 数组：\n" % len(texts) +
              "\n".join("%d. %s" % (i + 1, t[:120]) for i, t in enumerate(texts)))
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "think": False,  # 关键：qwen3.5 开 think 会把输出吞进 thinking、content 清空
        "options": {"temperature": 0}}).encode()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    resp = json.loads(opener.open(req, timeout=300).read())
    c = resp["message"]["content"]
    # 剥离 <think> 块和代码围栏
    c = c.split("</think>")[-1]
    if "```" in c:
        c = c.split("```")[1] if c.count("```") >= 2 else c
    start, end = c.find("["), c.rfind("]")
    if start < 0 or end < 0:
        return []
    try:
        return json.loads(c[start:end + 1])
    except Exception:
        return []


# 兼容模型输出的中文角色名 / 键名漂移（{"role":"一级标题","content":..} 或 {"text":..,"role":"heading1"}）
_ROLE_ALIAS = {
    "heading1": "heading1", "一级标题": "heading1", "一": "heading1", "标题1": "heading1", "1": "heading1",
    "heading2": "heading2", "二级标题": "heading2", "二": "heading2", "标题2": "heading2", "2": "heading2",
    "heading3": "heading3", "三级标题": "heading3", "三": "heading3", "标题3": "heading3", "3": "heading3",
    "heading4": "heading3", "四级标题": "heading3", "标题4": "heading3", "4": "heading3",
    "body": "body", "正文": "body", "正文段落": "body", "paragraph": "body", "normal": "body",
    "ref_item": "ref_item", "参考文献条目": "ref_item", "参考文献": "ref_item", "reference": "ref_item", "引用条目": "ref_item",
    "keywords": "keywords", "关键词": "keywords", "关键词行": "keywords",
    "abstract_heading": "abstract_heading", "摘要标题": "abstract_heading", "摘要": "abstract_heading",
    "caption": "caption", "图表题注": "caption", "题注": "caption", "表格题注": "caption", "figure caption": "caption",
}


def normalize_labels(labels):
    """把模型输出归一化为 [{text, role}]（兼容键名/中文角色名漂移）"""
    out = []
    for d in labels:
        text = d.get("text") or d.get("content") or ""
        role = str(d.get("role", "")).strip().lower()
        role = _ROLE_ALIAS.get(role) or (role if role in _ROLE_ALIAS.values() else None)
        if text and role:
            out.append({"text": text, "role": role})
    return out


def collect_targets():
    """低置信段 + 小类（paren_cn/关键词/摘要/ref_item）→ 需 LLM 标注的段落。"""
    targets = []
    seen = set()
    for fp in ["samples.jsonl", "samples_gov.jsonl"]:
        p = os.path.join(TRAIN_DIR, fp)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("text", "")
            role = d.get("role", "")
            if not t or t in seen:
                continue
            # 重点：规则拿不准的段（is_uncertain 数字.短行）、（一）类、小类
            if (role in ("keywords", "abstract_heading", "ref_heading", "caption")
                    or (d.get("digit_dot") and len(t) <= 40)
                    or d.get("paren_cn") or d.get("paren_digit")
                    or d.get("has_note_word") or d.get("has_ref_type")):
                targets.append(t)
                seen.add(t)
    return targets


def main():
    targets = collect_targets()
    print("待 LLM 标注: %d 段" % len(targets))
    out_path = os.path.join(TRAIN_DIR, "llm_labels.jsonl")
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding="utf-8"):
            try:
                done.add(json.loads(line)["text"])
            except Exception:
                pass
    pending = [t for t in targets if t not in done]
    print("已完成 %d，待标 %d" % (len(done), len(pending)))

    BATCH = 25
    with open(out_path, "a", encoding="utf-8") as f:
        for i in range(0, len(pending), BATCH):
            batch = pending[i:i + BATCH]
            try:
                labels = call_llm(batch)
                ok = 0
                for d in normalize_labels(labels):
                    text, role = d.get("text", ""), d.get("role", "")
                    if text and role in ("heading1", "heading2", "heading3", "body",
                                         "ref_item", "keywords", "abstract_heading", "caption"):
                        f.write(json.dumps({"text": text, "role": role}, ensure_ascii=False) + "\n")
                        ok += 1
                print("[%d/%d] 批标注 %d 段，有效 %d" % (i + len(batch), len(pending), len(batch), ok))
            except Exception as e:
                print("[%d] 批失败: %r" % (i, e))
            time.sleep(1.0)


if __name__ == "__main__":
    main()
