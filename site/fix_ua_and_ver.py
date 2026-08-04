# -*- coding: utf-8 -*-
"""修复：download 的 UA 不用模块全局变量 APP_NAME（PyInstaller 打包后失效），改字面量。
并支持 set_version 参数切换打包版本。"""
import re, sys, json

p = r'license\version.py'
s = open(p, encoding='utf-8').read()

# UA 字面量（两处）
n = s.count('"User-Agent": APP_NAME + "/" + VERSION')
s = s.replace('"User-Agent": APP_NAME + "/" + VERSION',
              '"User-Agent": "DocFormatTool/" + VERSION')
print('UA 字面量替换:', n, '处')

# 可选版本切换
ver = sys.argv[1] if len(sys.argv) > 1 else None
if ver:
    s = re.sub(r'VERSION\s*=\s*"[^"]+"', 'VERSION = "%s"' % ver, s)
    print('VERSION →', ver)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('version.py 已写')
