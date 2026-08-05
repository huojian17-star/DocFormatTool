# -*- coding: utf-8 -*-
"""v1.0.15 发布准备：version.json 改 1.0.15 + full_url + sha256 + note（先不 push，用户 publish 后 push）"""
import json, hashlib

h = hashlib.sha256()
with open(r'dist\DocFormatTool.exe', 'rb') as f:
    for c in iter(lambda: f.read(1048576), b''):
        h.update(c)
sha = h.hexdigest()

vj = json.load(open('version.json', encoding='utf-8'))
vj['version'] = '1.0.15'
vj['sha256'] = sha
vj['full_url'] = 'https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.15/DocFormatTool.exe'
vj['note'] = ('v1.0.15：论文样式修复——题目显示为"论文题目"样式、摘要标签与摘要正文分开（"摘要"+"摘要正文"两个样式）、'
              '关键词独立样式；样式集/导航窗格显示完善（摘要进导航，论文题目/关键词/摘要正文不进）。')
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json → 1.0.15（待 publish 后 push）')
print('sha256:', sha[:16], '...')
print('full_url:', vj['full_url'])
