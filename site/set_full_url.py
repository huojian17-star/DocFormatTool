# -*- coding: utf-8 -*-
"""version.json：url 指向 updater（旧版下载），full_url 指向完整版（新版/updater 用）"""
import json

v = json.load(open('version.json', encoding='utf-8'))
v['url'] = 'https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.7/updater.exe'
v['full_url'] = 'https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.7/DocFormatTool.exe'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('url      =', v['url'])
print('full_url =', v['full_url'])
