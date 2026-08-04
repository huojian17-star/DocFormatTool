# -*- coding: utf-8 -*-
"""打印生成的 bat 内容，检查语法"""
import sys, os
sys.path.insert(0, '.')
import license.version as v
bat = v.build_updater_bat(r'C:\test dir\DocFormatTool.exe', r'C:\test dir\DocFormatTool_new.exe')
print(bat)
print('---')
# 检查 for /d 行转义是否正确
import re
for line in bat.split('\r\n'):
    if 'MEI' in line:
        print('MEI 行:', repr(line))
