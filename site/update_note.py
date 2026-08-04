# -*- coding: utf-8 -*-
"""更新 note：加手动下载指引（老版本 v1.0.9/1.0.10 自动更新按钮无反应，需手动下载引导）"""
import json

vj = json.load(open('version.json', encoding='utf-8'))
vj['note'] = ('v1.0.14：修复自动更新——更新后无法自动重启新版（Failed to load Python DLL）已解决，更新链路加固。'
              '【重要】如果你的自动更新按钮点击无反应（老版本缺陷），请直接使用下方蓝奏云链接手动下载新版，'
              '覆盖到原程序目录即可（激活状态不受影响）。')
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('note 已更新（含手动下载指引）')
