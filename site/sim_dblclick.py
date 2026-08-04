# -*- coding: utf-8 -*-
"""用 os.startfile（=explorer 双击）精确模拟用户启动测试包 v1.0.13，工作目录=测试包目录"""
import os, time, ctypes, ctypes.wintypes as wt, subprocess

exe = r'F:\论文排版工具_测试包\DocFormatTool.exe'
print('目标:', exe, '存在:', os.path.exists(exe))
os.chdir(r'F:\论文排版工具_测试包')  # 用户双击时工作目录=文件所在目录

# explorer 方式启动（等价双击）
os.startfile(exe)
time.sleep(14)

# 检查进程
proc_found = False
for p in subprocess.check_output('tasklist /fi "imagename eq DocFormatTool.exe" /fo csv', shell=True).decode('gbk', errors='ignore').splitlines():
    if 'DocFormatTool' in p:
        proc_found = True
        break
print('进程存活:', proc_found)

titles = []
@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, l):
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetWindowTextW(h, buf, 256)
    if buf.value.strip():
        titles.append(buf.value)
    return True
ctypes.windll.user32.EnumWindows(cb, 0)
hits = [t for t in titles if '规范文档' in t or 'Error' in t]
print('窗口:', hits if hits else '（无，进程可能已崩）')

if proc_found:
    os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
