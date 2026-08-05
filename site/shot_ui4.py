# -*- coding: utf-8 -*-
"""默认状态截图（winfo_id 精确定位，不被遮挡）"""
import sys, os, time
sys.path.insert(0, r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
os.chdir(r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
import ctypes, ctypes.wintypes as wt
from app.main import App

app = App()

def grab():
    hwnd = app.winfo_id()
    rect = wt.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0040)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    time.sleep(1.5)
    import PIL.ImageGrab as IG
    img = IG.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
    img.save(r'site\ui_default.png')
    print('已截图 ui_default.png', rect.right-rect.left, rect.bottom-rect.top)
    app.destroy()

app.after(1500, grab)
app.mainloop()
print('完成')
