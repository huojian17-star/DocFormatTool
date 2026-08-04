# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
import license.version as v
bat = v.build_updater_bat(r'C:\test dir\DocFormatTool.exe', r'C:\test dir\DocFormatTool_new.exe')
print('bat 长度:', len(bat))
print('含 taskkill:', 'taskkill /f /im DocFormatTool.exe' in bat)
print('含 copy:', 'copy /y' in bat)
print('含自删:', 'del "%%~f0"' in bat)
print('含 start:', 'start ""' in bat)
print('--- bat 前 4 行 ---')
for line in bat.split('\r\n')[:4]:
    print(repr(line))
