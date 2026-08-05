# -*- coding: utf-8 -*-
"""v1.0.16 最终发布准备：version.json 最新 note + 最新 exe sha256"""
import json, hashlib

VER = "1.0.16"
exe = r'dist\DocFormatTool.exe'
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
print('exe sha256:', sha[:16], '...')

vj = {
    "version": VER,
    "note": "v1.0.16：全新界面（AiNiee 风格侧边栏+卡片+吉祥物）+ 拖拽文件选入 + 鼠标滚轮滚动 + 窗口可最大化 + 一键排版固定底部 + 更新链路加固",
    "full_url": "https://ghfast.top/https://github.com/huojian17-star/DocFormatTool/releases/download/v" + VER + "/DocFormatTool.exe",
    "full_sha256": sha,
    "manual_url": "https://wwavh.lanzoul.com/iu1i640hnz6b",
    "min_version": "1.0.0"
}
open(r'site\version.json', 'w', encoding='utf-8').write(json.dumps(vj, ensure_ascii=False, indent=2))
print('version.json 已更新:', VER)
