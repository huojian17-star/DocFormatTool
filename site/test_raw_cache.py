# -*- coding: utf-8 -*-
"""测试 raw 边缘缓存：加 query 参数是否返回新内容"""
import urllib.request, json, time, sys

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
base = "https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json"
for suffix in ["", "?x=%d" % int(time.time()), "?t=%d" % int(time.time())]:
    t0 = time.time()
    try:
        req = urllib.request.Request(base + suffix, headers={"User-Agent": "DocFormatTool/1.0.12"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
        print("%.1fs  %-12s → version=%s" % (time.time() - t0, suffix or "(无参数)", d.get('version')))
    except Exception as e:
        print("FAIL", suffix, repr(e)[:60])

# ghfast 代理加 query
for suffix in ["", "?x=%d" % int(time.time())]:
    t0 = time.time()
    u = "https://ghfast.top/" + base + suffix
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "DocFormatTool/1.0.12"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
        print("ghfast %.1fs %-12s → version=%s" % (time.time() - t0, suffix or "(无参数)", d.get('version')))
    except Exception as e:
        print("ghfast FAIL", repr(e)[:60])
