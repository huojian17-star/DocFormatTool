# -*- coding: utf-8 -*-
"""恢复 version.json 到正式版 v1.0.11（测试版 1.0.13 下线，真实用户不收到错误更新提示）"""
import json

vj = json.load(open('version.json', encoding='utf-8'))
vj['version'] = '1.0.11'
vj.pop('sha256', None)  # 测试版 sha256（指向 v1.0.13），删除
vj['full_url'] = 'https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v1.0.11/DocFormatTool.exe'
vj['note'] = 'v1.0.11：修复自动更新——点击"自动更新"无反应/进度窗口不显示/失败无提示（三个线程与闭包问题）。更新后下载进度条正常显示，失败会弹窗附手动下载链接。'
vj['url'] = 'https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/updater.exe'
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json 已恢复 v1.0.11:')
for k in ['version', 'full_url', 'note']:
    print(' ', k, '=', str(vj.get(k, ''))[:70])
