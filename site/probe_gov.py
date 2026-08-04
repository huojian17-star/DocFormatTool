# -*- coding: utf-8 -*-
import urllib.request, re
req = urllib.request.Request('https://www.gov.cn/zhengce/zuixin/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
links = re.findall(r'href="([^"]*content_\d+\.htm[^"]*)"', html)
print('共', len(links), '个链接')
for l in links[:14]:
    print(repr(l))
