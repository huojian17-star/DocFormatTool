# -*- coding: utf-8 -*-
"""version.py：按版本区分下载地址——旧版(<1.0.7)拿 updater.exe，新版(>=1.0.7)拿完整版"""
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = 'return new_ver, data.get("full_url") or data.get("url", ""), data.get("note", ""), data.get("manual_url", ""), data.get("manual_pwd", "")'
new = ('            # 下载地址按版本区分：v1.0.7 起支持 updater 机制——\n'
       '            # 旧版(<1.0.7)下载小体积 updater.exe（秒下不卡），新版直接下载完整版。\n'
       '            if _cmp_version(VERSION, "1.0.7") >= 0:\n'
       '                dl = data.get("full_url") or data.get("url", "")\n'
       '            else:\n'
       '                dl = data.get("url", "")\n'
       '            return new_ver, dl, data.get("note", ""), data.get("manual_url", ""), data.get("manual_pwd", "")')
if old in s:
    s = s.replace(old, new)
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('已按版本区分下载地址 ✓')
else:
    print('未找到目标行')
    for line in s.splitlines():
        if 'return new_ver' in line:
            print('实际:', line)
