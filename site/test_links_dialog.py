# -*- coding: utf-8 -*-
"""测试自定义链接弹窗（修正版：置顶 + 正确截图）"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import ImageGrab
from app.main import App

app = App()
app.update()
win = app._show_links_window(
    "发现新版本",
    "发现新版本 v1.0.7（当前 v1.0.4）\n更新内容：自动更新增强\n\n点击\"自动更新\"开始下载（激活状态不受影响）。",
    [("蓝奏云（提取码 8u6z）", "https://wwavh.lanzoul.com/iu1i640hnz6b"),
     ("GitHub Releases 页面", "https://github.com/huojian17-star/DocFormatTool/releases")],
    extra_btns=[("自动更新", lambda: print("自动更新点击"))])
win.lift()
win.attributes("-topmost", True)
app.update()
time.sleep(1.2)
x, y = win.winfo_rootx(), win.winfo_rooty()
w, h = win.winfo_width(), win.winfo_height()
print("弹窗: (%d,%d) %dx%d" % (x, y, w, h))
img = ImageGrab.grab(bbox=(x - 8, y - 8, x + w + 8, y + h + 8))
img.save(os.path.join(os.path.dirname(__file__), "..", "gui_links2.png"))
win.destroy()
app.destroy()
print("DONE")
