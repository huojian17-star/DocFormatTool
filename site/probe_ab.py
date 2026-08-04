# -*- coding: utf-8 -*-
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
SYSTEM = ("你是文档结构标注助手。判断段落角色，只输出JSON数组：[{\"text\":\"原文\",\"role\":\"角色\"}]。"
          "角色：heading1(一级\"一、xxx\"/\"第一章\"/\"1 xxx\")、heading2(二级\"1.1\"/\"（一）\")、heading3(三级\"1.1.1\"/\"1. xxx\")、"
          "body(正文)、ref_item(参考文献\"[1] xxx\")、keywords(关键词行)、abstract_heading(摘要标题)、caption(题注)。"
          "标题=短行+编号+无句号；列举=编号后短语如\"1. 优点\"；脚注=含数据来源/资料来源/注：/http。")
TESTS = ["一、总体要求", "（一）指导思想", "1. 优点：效率高", "1. 数据来源于国家统计局：https://data.stats.gov.cn/"]
for model in ["qwen3.5:latest", "qwen3.5:4b"]:
    prompt = ("请标注以下段落，逐条输出 JSON 数组：\n" + "\n".join("%d. %s" % (i + 1, t) for i, t in enumerate(TESTS)))
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA := "http://127.0.0.1:11434/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        resp = json.loads(opener.open(req, timeout=300).read())
        c = resp["message"]["content"]
        print("=== %s ===" % model)
        print("content 长度:", len(c))
        print(repr(c[:400]))
    except Exception as e:
        print("=== %s 失败: %r ===" % (model, e))
