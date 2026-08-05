# -*- coding: utf-8 -*-
"""高级展开 + 滚动到底部后的截图（验证按钮贴底 + 布局干净）"""
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
    img.save(r'site\ui_adv_bottom.png')
    print('已截图', rect.right-rect.left, rect.bottom-rect.top)
    # 输出按钮位置（相对窗口）
    app.update_idletasks()
    for child in app._main.master.winfo_children():
        pass
    app.destroy()

def do_adv():
    app.var_adv.set(True)
    app._on_adv_toggle()
    app.update_idletasks()
    # 滚动到底部
    app._canvas.yview_moveto(1.0)
    app.update_idletasks()
    print('已滚动到底部, yview:', app._canvas.yview())
    app.after(800, grab)

app.after(1500, do_adv)
app.mainloop()
print('完成')
