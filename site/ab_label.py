# -*- coding: utf-8 -*-
"""A/B 对比：qwen3.5:latest(9B) vs qwen3.5:4b 标注一致性测试"""
import json, urllib.request

OLLAMA = "http://127.0.0.1:11434/api/chat"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

SYSTEM = """你是文档结构标注助手。判断每个段落属于哪种角色，只输出 JSON 数组：[{"text":"原文","role":"角色"}]
角色：heading1(一级标题"一、xxx"/"第一章"/"1 xxx")、heading2(二级"1.1 xxx"/"（一）xxx")、
heading3(三级"1.1.1"/"1. xxx")、body(正文)、ref_item(参考文献"[1] xxx")、keywords(关键词行)、abstract_heading(摘要标题)、caption(图表题注)。
标题=短行+编号+无句号；列举=编号后短语如"1. 优点"；脚注=含数据来源/资料来源/注：/http。"""


def label(model, texts):
    prompt = ("请标注以下段落，逐条输出 JSON 数组：\n" +
              "\n".join("%d. %s" % (i + 1, t[:100]) for i, t in enumerate(texts)))
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    resp = json.loads(opener.open(req, timeout=300).read())
    c = resp["message"]["content"].split("</think>")[-1]
    start, end = c.find("["), c.rfind("]")
    if start < 0 or end < 0:
        return {}
    try:
        return {d.get("text", ""): d.get("role") for d in json.loads(c[start:end + 1])}
    except Exception:
        return {}


TESTS = [
    "一、总体要求", "（一）指导思想", "1. 坚持党的全面领导", "1. 优点：效率高",
    "2. 缺点：成本较大", "1. 这里的数据来源于国家统计局：https://data.stats.gov.cn/",
    "2. 资料来源：教育部历年报告。", "第一章 绪论", "1.1 研究背景", "1.1.1 研究目的",
    "[1] 张伟, 李明. 人工智能教育应用研究综述[J]. 电化教育研究, 2025.",
    "关键词：人工智能；教育应用；个性化学习", "随着人工智能技术的快速发展，教育领域正在经历深刻变革。",
    "第一条 为了保护民事主体的合法权益，制定本法。", "Abstract", "References",
    "1. Introduction", "2.1 Related Work", "Conclusion", "The proposed method achieves state-of-the-art results on multiple benchmarks.",
]

print("=== qwen3.5 latest(9B) vs 4b 标注对比 ===")
a = label("qwen3.5:latest", TESTS)
b = label("qwen3.5:4b", TESTS)
agree = diff = 0
for t in TESTS:
    ra, rb = a.get(t, "?"), b.get(t, "?")
    if ra == "?" and rb == "?":
        continue
    if ra == rb:
        agree += 1
    else:
        diff += 1
    print("%-24s | latest=%-10s | 4b=%-10s | %s" % (
        t[:24], ra, rb, "✓" if ra == rb else "✗差异"))
total = agree + diff
print("\n一致率: %d/%d = %.0f%%" % (agree, total, 100 * agree / total if total else 0))
