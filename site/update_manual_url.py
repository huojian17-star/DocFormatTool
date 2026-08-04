# -*- coding: utf-8 -*-
"""更新 manual_url/manual_pwd 为 v1.0.8 蓝奏云链接"""
import json

v = json.load(open('version.json', encoding='utf-8'))
v['manual_url'] = 'https://wwavh.lanzoul.com/b01euoissf'
v['manual_pwd'] = 'fup2'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('manual_url =', v['manual_url'])
print('manual_pwd =', v['manual_pwd'])
print('version    =', v['version'])
