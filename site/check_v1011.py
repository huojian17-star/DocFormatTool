# -*- coding: utf-8 -*-
"""验证 v1.0.11 release + 检查 version.json 结构"""
import urllib.request, json, os, hashlib

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

# 1) v1.0.11 release
url = 'https://api.github.com/repos/huojian17-star/DocFormatTool/releases/tags/v1.0.11'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    r = json.loads(opener.open(req, timeout=30).read())
    print('release:', r['name'], '| 创建:', r['published_at'])
    for a in r.get('assets', []):
        print('  附件:', a['name'], '%.1fMB' % (a['size'] / 1048576))
except Exception as e:
    print('release API 失败:', repr(e)[:80])

# 2) version.json 结构
v = json.load(open('version.json', encoding='utf-8'))
print('\nversion.json 字段:', list(v.keys()))
for k in ['version', 'url', 'full_url', 'note']:
    print('  %s: %s' % (k, str(v.get(k, ''))[:80]))
