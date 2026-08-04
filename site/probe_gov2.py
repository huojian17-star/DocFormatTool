# -*- coding: utf-8 -*-
import urllib.request, re
req = urllib.request.Request('https://www.gov.cn/zhengce/zuixin/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
print('原始HTML长度:', len(html))
print('含 content_7077398:', 'content_7077398' in html)
zc = re.findall(r'[^"]*zhengce[^"]*', html)
print('zhengce 链接样本:', zc[:8])
