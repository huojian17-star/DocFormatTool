# -*- coding: utf-8 -*-
import json
v = json.load(open('version.json', encoding='utf-8'))
v['note'] = ('v1.0.11：修复自动更新——点击"自动更新"无反应/进度窗口不显示/失败无提示（三个线程与闭包问题）。'
             '更新后下载进度条正常显示，失败会弹窗附手动下载链接。')
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('note:', v['note'][:60])
