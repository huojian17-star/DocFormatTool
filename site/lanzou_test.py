# -*- coding: utf-8 -*-
"""蓝奏云解析 v3：CookieJar 管理会话 + 密码 + downprocess"""
import urllib.request, urllib.parse, urllib.error, re, json, gzip, http.cookiejar, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SHARE = "https://wwavh.lanzoul.com/iu1i640hnz6b"
PWD = "8u6z"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch(url, data=None, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*",
         "Accept-Language": "zh-CN,zh;q=0.9",
         "Accept-Encoding": "gzip"}
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        h["Content-Type"] = "application/x-www-form-urlencoded"
        h["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(url, data=body, headers=h)
    r = opener.open(req, timeout=timeout)
    raw = r.read()
    if r.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    return r, raw.decode("utf-8", errors="ignore")


def grab(html, key):
    for pat in [key + r'\s*[:=]\s*"([^"]+)"', r'name="%s" value="([^"]*)"' % key]:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return ""


def resolve(share_url, pwd):
    base = share_url.rsplit("/", 1)[0]
    ajax = base + "/ajax.php"
    # 1. 分享页
    _, html = fetch(share_url)
    sign = grab(html, "sign")
    print("分享页 sign:", sign[:30] if sign else "(无)")
    # 2. 密码验证
    _, js = fetch(ajax, {"action": "passwd", "p": pwd, "sign": sign or ""},
                 headers={"Referer": share_url, "Origin": base})
    print("passwd 响应:", js[:150])
    try:
        info = json.loads(js)
    except Exception:
        raise RuntimeError("passwd 非JSON")
    if info.get("zt") != 1:
        raise RuntimeError("密码错误或风控: %s" % info)
    # 3. downprocess
    _, js2 = fetch(ajax, {"action": "downprocess", "sign": sign or "", "ves": "2"},
                   headers={"Referer": share_url, "Origin": base})
    print("downprocess 响应:", js2[:150])
    try:
        dl = json.loads(js2)
    except Exception:
        raise RuntimeError("downprocess 非JSON")
    if dl.get("zt") != 1:
        raise RuntimeError("直链失败: %s" % dl)
    dom = dl.get("dom") or ""
    u = dl.get("url") or ""
    direct = (dom + "/file/" + u) if not u.startswith("http") else u
    return direct, dl.get("inf", "download.bin")


if __name__ == "__main__":
    t0 = time.time()
    try:
        direct, fn = resolve(SHARE, PWD)
        print("直链: %s" % direct[:100])
        print("文件名: %s (%.1fs)" % (fn, time.time() - t0))
        _, head = fetch(direct, headers={"Referer": SHARE}, timeout=30)
    except Exception as e:
        print("失败: %r" % e)
