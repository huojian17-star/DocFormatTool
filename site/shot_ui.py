# -*- coding: utf-8 -*-
"""启动新版 UI 并截图自查（找到窗口 → 前台 → 截图）"""
import subprocess, time, ctypes, ctypes.wintypes as wt, sys

# 启动
proc = subprocess.Popen([sys.executable, r'app\main.py'], cwd=r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
time.sleep(14)

# 找窗口矩形
hwnd = None
@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, l):
    global hwnd
    buf = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetWindowTextW(h, buf, 256)
    if '规范文档一键排版' in buf.value:
        hwnd = h
        return False
    return True
ctypes.windll.user32.EnumWindows(cb, 0)
if not hwnd:
    print('窗口未找到')
    sys.exit(1)

rect = wt.RECT()
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
print('窗口矩形:', rect.left, rect.top, rect.right, rect.bottom, '尺寸', rect.right-rect.left, rect.bottom-rect.top)

# 移到屏幕左上角 + 置前（避免被其他窗口遮挡）
ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0040)
ctypes.windll.user32.SetForegroundWindow(hwnd)
time.sleep(2)
ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
print('移动后:', rect.left, rect.top, rect.right, rect.bottom)
import PIL.ImageGrab as IG
img = IG.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
out = r'site\ui_v2_shot.png'
img.save(out)
print('已截图:', out)
proc.terminate()
