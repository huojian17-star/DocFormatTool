# -*- coding: utf-8 -*-
"""打开高级选项后的 UI 截图（验证：一键排版按钮固定在底部 + 滚动条可见）"""
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
    img.save(r'site\ui_adv_shot.png')
    print('已截图 ui_adv_shot.png', rect.right-rect.left, rect.bottom-rect.top)
    # 断言：滚动条存在
    print('滚动条存在:', hasattr(app, '_canvas'))

def do_adv():
    app.var_adv.set(True)
    app._on_adv_toggle()
    print('高级选项已展开')
    app.after(800, grab)
    app.after(4000, app.destroy)

app.after(1500, do_adv)
app.mainloop()
print('完成')
