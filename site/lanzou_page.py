# -*- coding: utf-8 -*-
"""打印蓝奏云分享页原文"""
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SHARE = "https://wwavh.lanzoul.com/iu1i640hnz6b"
req = urllib.request.Request(SHARE, headers={"User-Agent": UA})
html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="ignore")
print(html)
