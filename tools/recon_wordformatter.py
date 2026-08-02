# -*- coding: utf-8 -*-
"""竞品技术侦查：抓 wordformatter.com 的 HTML/JS，识别框架与处理路径。"""
import re
import urllib.request

PROXY = "http://127.0.0.1:7890"


def fetch(url, timeout=20):
    proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    opener = urllib.request.build_opener(proxy)
    req = urllib.request.Request(url, headers={"User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")})
    return opener.open(req, timeout=timeout).read().decode("utf-8", "ignore")


html = fetch("https://wordformatter.com/")
print("=== HTML 大小:", len(html), "===")

# 框架特征
print("\n--- 框架/构建特征 ---")
for pat in ["react", "vue", "next", "nuxt", "angular", "svelte", "webpack",
            "vite", "tailwind", "bootstrap", "__NEXT_DATA__", "window.__NUXT__",
            "wasm", "webassembly", "puppeteer", "docx", "mammoth", "pandoc"]:
    if pat.lower() in html.lower():
        print("  ✓", pat)

# JS/CSS 引用
print("\n--- script/link 引用 ---")
for m in re.finditer(r'<(script|link)[^>]+(?:src|href)="([^"]+)"', html):
    tag, url = m.group(1), m.group(2)
    if not url.startswith("http"):
        url = "https://wordformatter.com" + url
    print("  [%s] %s" % (tag, url[:90]))

# 标题/元信息
print("\n--- title/desc ---")
for m in re.finditer(r"<title>(.*?)</title>", html, re.S):
    print("  title:", m.group(1)[:60])
for m in re.finditer(r'name="description" content="([^"]*)"', html):
    print("  desc:", m.group(1)[:80])
