# -*- coding: utf-8 -*-
"""逐通道测试 UPDATE_URLS"""
import sys, urllib.request, json, time
sys.path.insert(0, '.')

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # 不走系统代理

urls = [
    "https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json",
    "https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json",
    "https://cdn.jsdelivr.net/gh/huojian17-star/DocFormatTool@master/version.json",
]
for u in urls:
    t0 = time.time()
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "DocFormatTool/1.0.12"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
        print("OK  %.1fs  %s  → version=%s" % (time.time() - t0, u.split('/')[2], d.get('version')))
    except Exception as e:
        print("FAIL %.1fs  %s  → %s" % (time.time() - t0, u.split('/')[2], repr(e)[:70]))

# 也测带系统代理的（check_update 默认 urllib 会走环境代理）
print('\n--- 走系统代理 ---')
for u in urls[:1]:
    t0 = time.time()
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "DocFormatTool/1.0.12"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
        print("OK  %.1fs  %s → version=%s" % (time.time() - t0, u.split('/')[2], d.get('version')))
    except Exception as e:
        print("FAIL %.1fs  %s → %s" % (time.time() - t0, u.split('/')[2], repr(e)[:70]))
