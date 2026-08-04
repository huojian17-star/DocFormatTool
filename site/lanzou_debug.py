# -*- coding: utf-8 -*-
"""调试蓝奏云 ajax 响应原文"""
import urllib.request, urllib.parse, re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SHARE = "https://wwavh.lanzoul.com/iu1i640hnz6b"


def get(url, headers=None, timeout=15):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=timeout)


html = get(SHARE).read().decode("utf-8", errors="ignore")
print("页面长度:", len(html))
m = re.search(r'<iframe[^>]+src="([^"]+)"', html)
page_url = m.group(1) if m else SHARE
print("iframe/页面:", page_url[:80])
if not page_url.startswith("http"):
    page_url = urllib.parse.urljoin(SHARE, page_url)
html2 = get(page_url).read().decode("utf-8", errors="ignore")
print("下载页长度:", len(html2))

def grab(key):
    for pat in [key + r'\s*[:=]\s*"([^"]+)"', r'name="%s" value="([^"]*)"' % key]:
        mm = re.search(pat, html2)
        if mm:
            return mm.group(1)
    return ""

for key in ["action", "sign", "ve", "fn", "lx", "kd"]:
    v = grab(key)
    if v:
        print("  %s = %s" % (key, v[:40]))

action = grab("action") or "downprocess"
sign = grab("sign")
ve = grab("ve")
ajax = page_url.rsplit("/", 1)[0] + "/ajax.php"
print("ajax url:", ajax)
data = urllib.parse.urlencode({"action": action, "sign": sign, "ves": ve}).encode()
resp = get(ajax, headers={"Referer": page_url}, timeout=15)
raw = resp.read().decode("utf-8", errors="ignore")
print("ajax 响应原文:", raw[:500])
