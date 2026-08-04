# -*- coding: utf-8 -*-
import urllib.request, re
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
url = "http://export.arxiv.org/api/query?search_query=cat:cs.CL&start=0&max_results=3&sortBy=submittedDate"
try:
    xml = opener.open(url, timeout=30).read().decode('utf-8', errors='ignore')
    print('返回长度:', len(xml))
    print(xml[:800])
    ids = re.findall(r'<id>([^<]+)</id>', xml)
    print('ids:', ids)
except Exception as e:
    print('失败:', repr(e))
