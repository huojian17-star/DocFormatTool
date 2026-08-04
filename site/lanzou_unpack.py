# -*- coding: utf-8 -*-
"""解压蓝奏云分享页 gzip 并提取下载参数"""
import gzip, os, re

p = os.path.join(os.environ['TEMP'], 'lz_page.html')
raw = open(p, 'rb').read()
html = gzip.decompress(raw).decode('utf-8', errors='ignore')
print('解压后长度:', len(html))

patterns = [
    (r'<iframe[^>]+src="([^"]+)"', 'iframe'),
    (r'sign[^"]*"([^"]{10,})"', 'sign'),
    (r'action[^"]*"([^"]+)"', 'action'),
    (r'class="filename"[^>]*>([^<]+)<', 'filename'),
    (r'"url":"([^"]+)"', 'url'),
    (r'data\.js', 'data.js 引用'),
]
for pat, tag in patterns:
    ms = re.findall(pat, html)
    if ms:
        print(tag, '→', [m[:70] for m in ms[:3]])

# 无 script 的 body 片段
body = re.sub(r'<script[\s\S]*?</script>', '', html)
body = re.sub(r'<style[\s\S]*?</style>', '', body)
print('--- body 片段 ---')
print(body[:500])
