# -*- coding: utf-8 -*-
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
SYSTEM = "你是文档结构标注助手。判断段落角色，只输出JSON数组。"
prompt = ("请标注以下段落，逐条输出 JSON 数组：\n"
          "1. 一、总体要求\n2. （一）指导思想\n3. 1. 优点：效率高\n4. 1. 数据来源于国家统计局：https://data.stats.gov.cn/")
body = json.dumps({"model": "qwen3.5:4b", "messages": [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": prompt}],
    "stream": False, "options": {"temperature": 0}}).encode()
req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=body,
                             headers={"Content-Type": "application/json"})
resp = json.loads(opener.open(req, timeout=300).read())
print("keys:", list(resp.keys()))
print("done_reason:", resp.get("done_reason"))
msg = resp.get("message", {})
print("message keys:", list(msg.keys()))
print("content:", repr(msg.get("content", ""))[:300])
print("thinking 长度:", len(msg.get("thinking", "") or ""))
if msg.get("thinking"):
    print("thinking 前 300:", repr(msg["thinking"][:300]))
