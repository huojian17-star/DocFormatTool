# -*- coding: utf-8 -*-
"""模拟用户场景：刚 copy 覆盖的 exe 立即启动，看是否被 Defender/系统拦截"""
import subprocess, time, os, shutil, ctypes, ctypes.wintypes as wt

src = r'releases\DocFormatTool.exe'
testdir = os.path.join(os.environ['TEMP'], 'def_test')
os.makedirs(testdir, exist_ok=True)
dst = os.path.join(testdir, 'DocFormatTool.exe')

# 模拟"刚覆盖"：复制后立即启动（Defender 扫描窗口期）
shutil.copy2(src, dst)
t0 = time.time()
proc = subprocess.Popen([dst])
time.sleep(10)
ret = proc.poll()
if ret is not None:
    print('刚覆盖立即启动: 失败 退出码=%s (%.0fs) ← Defender 拦截疑点' % (ret, time.time() - t0))
else:
    titles = []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(h, l):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(h, buf, 256)
        if '规范文档一键排版' in buf.value:
            titles.append(buf.value)
        return True
    ctypes.windll.user32.EnumWindows(cb, 0)
    print('刚覆盖立即启动: 成功 (%.0fs) 窗口=%s' % (time.time() - t0, titles))
    os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')

# 等 30 秒再启动同一文件（模拟 Defender 扫描完成）
print('等待 35 秒（Defender 扫描窗口）...')
time.sleep(35)
proc2 = subprocess.Popen([dst])
time.sleep(10)
ret2 = proc2.poll()
if ret2 is not None:
    print('等待后启动: 失败 退出码=%s' % ret2)
else:
    titles2 = []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb2(h, l):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(h, buf, 256)
        if '规范文档一键排版' in buf.value:
            titles2.append(buf.value)
        return True
    ctypes.windll.user32.EnumWindows(cb2, 0)
    print('等待后启动: 成功 窗口=%s' % titles2)
    os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')

# 清理
shutil.rmtree(testdir, ignore_errors=True)
