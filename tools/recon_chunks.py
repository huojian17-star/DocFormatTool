# -*- coding: utf-8 -*-
"""抓 wordformatter 的 JS chunk，分析 docx 解析路径（本地 vs 后端 API）。"""
import re
import urllib.request

PROXY = "http://127.0.0.1:7890"
BASE = "https://wordformatter.com"
CHUNKS = [
    "/_next/static/chunks/465f799faf41e6df.js",
    "/_next/static/chunks/ad0eb8f7a09fbec7.js",
    "/_next/static/chunks/a6dad97d9634a72d.js",
]


def fetch(url, timeout=30):
    proxy = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    opener = urllib.request.build_opener(proxy)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return opener.open(req, timeout=timeout).read().decode("utf-8", "ignore")


PATTERNS = {
    "docx 解析库(前端)": ["mammoth", "docx-preview", "jszip", "pizzip", "docxtemplater",
                       "html-docx", "officeparser", "word-extractor"],
    "wasm(本地解析)": ["wasm", "WebAssembly", ".wasm"],
    "后端 API 调用": ["/api/", "apiUrl", "axios", "fetch("],
    "上传/下载": ["upload", "download", "FormData", "FileReader", "createObjectURL"],
    "LibreOffice 服务": ["libreoffice", "soffice", "unoconv"],
    "Pandoc": ["pandoc"],
}

for c in CHUNKS:
    try:
        js = fetch(BASE + c)
        print("=" * 50)
        print("chunk:", c, "| 大小:", len(js))
        for label, pats in PATTERNS.items():
            hits = []
            for p in pats:
                if p.lower() in js.lower():
                    hits.append(p)
            if hits:
                print("  %s: %s" % (label, hits))
        # API 端点
        for m in set(re.findall(r'["\'](/api/[^"\']+)["\']', js)) | set(re.findall(r'["\'](https?://[^"\']+)["\']', js)):
            if "wordformatter" in m or m.startswith("/api"):
                print("    端点:", m[:80])
    except Exception as e:
        print(c, "失败:", type(e).__name__)
