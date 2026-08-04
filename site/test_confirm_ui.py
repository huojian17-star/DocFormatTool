# -*- coding: utf-8 -*-
"""测试低置信确认弹窗 UI（主线程 + after 自动点击）"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import ImageGrab
import tkinter as tk
from app.main import App

app = App()
app.update()
items = [(0, '1. 研究背景与意义'), (1, '2. 主要研究方法'), (2, '3. 论文组织结构')]

state = {}
def auto_action():
    time.sleep(1.2)
    # 截图弹窗
    img = ImageGrab.grab()
    img.save(os.path.join(os.path.dirname(__file__), '..', 'gui_confirm.png'))
    # 找确定按钮点击
    def find_btn(widget):
        for c in widget.winfo_children():
            if isinstance(c, tk.Button) and c.cget('text') == '确定':
                return c
            r = find_btn(c)
            if r:
                return r
    for w_ in app.winfo_children():
        if isinstance(w_, tk.Toplevel):
            btn = find_btn(w_)
            if btn:
                btn.invoke()
                return
    state['no_btn'] = True

app.after(300, auto_action)
forced = app._confirm_uncertain(items)
print('弹窗关闭，确认结果:', forced or '（空：未做选择）')
print('截图: gui_confirm.png')
app.destroy()
