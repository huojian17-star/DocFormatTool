# -*- coding: utf-8 -*-
"""深挖 wordformatter chunk：fetch 端点与 FormData 字段。"""
import re
import urllib.request

PROXY = "http://127.0.0.1:7890"
proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
op = urllib.request.build_opener(proxy)
js = op.open(urllib.request.Request(
    "https://wordformatter.com/_next/static/chunks/ad0eb8f7a09fbec7.js",
    headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "ignore")

urls = set()
for m in re.finditer(r"fetch\(\s*[\"']([^\"']+)[\"']", js):
    urls.add(m.group(1))
print("fetch 直接 URL:", urls if urls else "无字面量（变量拼接）")

fds = set(re.findall(r"\.append\(\s*[\"']([^\"']+)[\"']", js))
print("FormData 字段:", fds)

apis = set(re.findall(r"[\"'](/[a-zA-Z][a-zA-Z0-9/_.-]{2,50})[\"']", js))
cand = [a for a in apis if any(k in a.lower() for k in ("api", "upload", "parse",
                                                        "format", "process", "convert", "export", "download"))]
print("疑似 API 路径:", cand[:20])

# fetch 上下文找端点和 method
for m in re.finditer(r"fetch\(", js):
    s = max(0, m.start() - 100)
    ctx = js[s:m.end() + 200]
    if any(k in ctx.lower() for k in ("formdata", "/api", "upload", "convert", "method")):
        print("--- 上下文 ---")
        print(re.sub(r"\s+", " ", ctx)[:200])
        print()
