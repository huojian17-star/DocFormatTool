# -*- coding: utf-8 -*-
import urllib.request, re
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.paper.edu.cn/releasepaper/content/202607-43'
req = urllib.request.Request(url, headers=UA)
html = opener.open(req, timeout=25).read().decode('utf-8', errors='ignore')
body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
body = re.sub(r'<[^>]+>', '\n', body)
body = re.sub(r'&nbsp;', ' ', body)
lines = [l.strip() for l in body.split('\n') if l.strip()]
# 找"摘要"出现的位置，从那打印
for i, l in enumerate(lines):
    if '摘要' in l or '关键词' in l or '引言' in l or '参考文献' in l:
        print('>>> L%d: %s' % (i, l[:50]))
