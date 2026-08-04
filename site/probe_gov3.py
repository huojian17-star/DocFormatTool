# -*- coding: utf-8 -*-
import urllib.request
UA = {'User-Agent': 'Mozilla/5.0'}
tests = [
    ('详情页', 'https://www.gov.cn/zhengce/content/202608/content_7077398.htm'),
    ('国务院公报', 'https://www.gov.cn/gongbao/currentissue.htm'),
    ('国务院文件', 'https://www.gov.cn/zhengce/xxgk/'),
    ('政策库', 'https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary'),
]
for name, url in tests:
    try:
        req = urllib.request.Request(url, headers=UA)
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        import re
        links = len(re.findall(r'content_\d+\.htm', html))
        print('%s: OK (%d 字节, %d 个 content 链接)' % (name, len(html), links))
    except Exception as e:
        print('%s: 失败 %r' % (name, e))
