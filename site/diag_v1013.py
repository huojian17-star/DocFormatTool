# -*- coding: utf-8 -*-
"""诊断：releases 的 v1.0.13 exe 能否启动（LoadLibrary 问题定位）"""
import subprocess, time, os, ctypes, ctypes.wintypes as wt

exe = r'releases\DocFormatTool.exe'
print('测试 exe:', exe, '%.1fMB' % (os.path.getsize(exe) / 1048576))

proc = subprocess.Popen([exe], cwd=os.path.dirname(exe))
time.sleep(12)
ret = proc.poll()
if ret is not None:
    print('启动失败，退出码:', ret, '← LoadLibrary 问题复现')
else:
    # 找窗口标题
    titles = []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(h, l):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(h, buf, 256)
        if '规范文档一键排版' in buf.value:
            titles.append(buf.value)
        return True
    ctypes.windll.user32.EnumWindows(cb, 0)
    print('启动成功，窗口:', titles)
    os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
