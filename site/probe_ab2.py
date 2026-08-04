# -*- coding: utf-8 -*-
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
SYSTEM = ("你是文档结构标注助手。判断每个段落属于哪种角色，只输出 JSON 数组：[{\"text\": \"原文\", \"role\": \"角色\"}]。"
          "可选角色：heading1(一级标题)、heading2(二级标题)、heading3(三级标题)、body(正文)、ref_item(参考文献条目)、"
          "keywords(关键词行)、abstract_heading(摘要标题)、caption(图表题注)。"
          "标题=短行+编号+不以句号结尾；列举=编号后是短语(如\"1. 优点：效率高\")；脚注/注释=含\"数据来源\"\"资料来源\"\"注：\"\"http\"。")
TESTS = [
    "一、总体要求", "（一）指导思想", "1. 坚持党的全面领导", "1. 优点：效率高",
    "2. 缺点：成本较大", "1. 这里的数据来源于国家统计局：https://data.stats.gov.cn/",
    "2. 资料来源：教育部历年报告。", "第一章 绪论", "1.1 研究背景", "1.1.1 研究目的",
    "[1] 张伟, 李明. 人工智能教育应用研究综述[J]. 电化教育研究, 2025.",
    "关键词：人工智能；教育应用；个性化学习", "随着人工智能技术的快速发展，教育领域正在经历深刻变革。",
    "第一条 为了保护民事主体的合法权益，制定本法。",
]
for model in ["qwen3.5:latest", "qwen3.5:4b"]:
    prompt = ("请标注以下 %d 个段落，逐条输出 JSON 数组：\n" % len(TESTS) +
              "\n".join("%d. %s" % (i + 1, t[:100]) for i, t in enumerate(TESTS)))
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        resp = json.loads(opener.open(req, timeout=300).read())
        c = resp["message"]["content"]
        print("=== %s content 长度 %d ===" % (model, len(c)))
        print(repr(c[:500]))
        print()
    except Exception as e:
        print("=== %s 失败: %r ===" % (model, e))
