# -*- coding: utf-8 -*-
import urllib.request, re
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://www.paper.edu.cn/releasepaper/content/202607-43'
try:
    req = urllib.request.Request(url, headers=UA)
    html = opener.open(req, timeout=25).read().decode('utf-8', errors='ignore')
    print('详情页长度:', len(html))
    # 是否要登录
    print('含登录提示:', '登录' in html and '全文' in html)
    # 标题
    m = re.search(r'<title>([^<]+)</title>', html)
    print('标题:', m.group(1) if m else '?')
    # 正文容器
    for pat in ['abstract', 'keywords', 'content', 'paper_content', 'article']:
        print(pat, '出现:', html.count(pat))
    # 找段落结构样本
    body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', '\n', body)
    body = re.sub(r'&nbsp;', ' ', body)
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    print('\n正文前 30 行:')
    for l in lines[:30]:
        print('  ', l[:60])
except Exception as e:
    print('失败:', repr(e))
