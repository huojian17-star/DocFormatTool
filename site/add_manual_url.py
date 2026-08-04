# -*- coding: utf-8 -*-
"""version.json 加 manual_url（蓝奏云手动下载备用链接）"""
import json

v = json.load(open('version.json', encoding='utf-8'))
v['manual_url'] = 'https://wwavh.lanzoul.com/iu1i640hnz6b'
v['manual_pwd'] = '8u6z'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('version.json:', json.dumps(v, ensure_ascii=False, indent=1)[:400])
