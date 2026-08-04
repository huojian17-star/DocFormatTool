# -*- coding: utf-8 -*-
import urllib.request, re
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
req = urllib.request.Request('https://www.paper.edu.cn/releasepaper/index.shtml', headers=UA)
html = opener.open(req, timeout=20).read().decode('utf-8', errors='ignore')
# 所有 href 统计
hrefs = re.findall(r'href="([^"]+)"', html)
from collections import Counter
print('href 类型:', Counter(h.split('/')[3] if len(h.split('/')) > 3 else h for h in hrefs if h.startswith('http')).most_common(10))
# 论文详情可能格式：releasepaper/content/xxx 或 displayJournalArticle
for h in hrefs:
    if any(k in h for k in ['content', 'article', 'view', 'display', 'paperid', 'id=']):
        print(repr(h))
# 找正文条目（可能是 a 标签带论文标题）
titles = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]{10,60})</a>', html)
print('\n带标题的链接:')
for h, t in titles[:12]:
    if not any(x in h for x in ['css', 'js', 'login', 'register', 'index', 'subject']):
        print(' ', repr(h)[:60], '→', t.strip()[:30])
