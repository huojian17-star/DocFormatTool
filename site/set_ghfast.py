# -*- coding: utf-8 -*-
"""version.json 下载地址改 ghfast.top 代理（无梯子国内可下）"""
import json

GH = 'https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.7/'
v = json.load(open('version.json', encoding='utf-8'))
v['url'] = GH + 'updater.exe'
v['full_url'] = GH + 'DocFormatTool.exe'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('url      =', v['url'])
print('full_url =', v['full_url'])
