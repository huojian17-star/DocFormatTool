# -*- coding: utf-8 -*-
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
SYSTEM = ("你是文档结构标注助手。判断每个段落属于哪种角色，只输出 JSON 数组：[{\"text\": \"原文\", \"role\": \"角色\"}]。"
          "可选角色：heading1(一级标题)、heading2(二级标题)、heading3(三级标题)、body(正文)、ref_item(参考文献条目)、keywords(关键词行)、abstract_heading(摘要标题)、caption(图表题注)。")
tests = ["一、总体要求", "（一）指导思想", "1. 优点：效率高", "1. 数据来源于国家统计局：https://data.stats.gov.cn/",
         "第一章 绪论", "1.1 研究背景", "[1] 张伟. 教育研究[J]. 2025.", "关键词：人工智能；教育"]
prompt = ("请标注以下 %d 个段落，逐条输出 JSON 数组：\n" % len(tests) +
          "\n".join("%d. %s" % (i + 1, t[:100]) for i, t in enumerate(tests)))
for think_flag in [False, True]:
    body = json.dumps({"model": "qwen3.5:latest", "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "think": think_flag, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        resp = json.loads(opener.open(req, timeout=300).read())
        c = resp["message"]["content"]
        print("think=%s → content 长度 %d" % (think_flag, len(c)))
        print(repr(c[:300]))
        print()
    except Exception as e:
        print("think=%s 失败 %r" % (think_flag, e))
