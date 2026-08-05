# -*- coding: utf-8 -*-
"""截新界面两张：默认视图 + 滚动到排版卡视图（含可拖拽标签/输入框/一键排版）"""
import sys, os, time
sys.path.insert(0, r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
os.chdir(r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
import ctypes, ctypes.wintypes as wt
from app.main import App

app = App()

def grab(name, scroll_frac=None):
    app.update_idletasks()
    if scroll_frac is not None:
        app._canvas.yview_moveto(scroll_frac)
        app.update_idletasks()
    hwnd = app.winfo_id()
    rect = wt.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    # 强制置前：TOPMOST + ALT 键模拟（绕过 Windows 前台锁定）
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0010)
    ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # ALT 按下
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # ALT 释放
    time.sleep(1.5)
    import PIL.ImageGrab as IG
    img = IG.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(r'site\%s.png' % name)
    print('已截图', name, img.size)

def run():
    grab('ui_shot_top')
    app.after(300, lambda: grab('ui_shot_pt', 0.42))
    app.after(600, app.destroy)

app.after(1500, run)
app.mainloop()
print('完成')
