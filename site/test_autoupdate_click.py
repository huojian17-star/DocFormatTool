# -*- coding: utf-8 -*-
"""端到端验证：模拟点击"自动更新" → 弹窗关闭 + 进度窗口出现（主线程）+ 无 NameError"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import tkinter as tk
from app.main import App

app = App()
app.update()
state = {}

def auto():
    time.sleep(0.5)
    # 模拟发现新版本弹窗（用假 url 立即失败，验证流程跑通无异常）
    app._show_update('9.9.9', 'https://127.0.0.1:1/x.exe', '测试更新说明', 'https://lanzou.example', 'pwd')
    time.sleep(0.8)
    # 找到"自动更新"按钮并点击
    def find_btn(widget, text):
        from tkinter import ttk as _ttk
        for c in widget.winfo_children():
            if isinstance(c, _ttk.Button) and c.cget('text') == text:
                return c
            r = find_btn(c, text)
            if r:
                return r
    for w_ in app.winfo_children():
        if isinstance(w_, tk.Toplevel):
            btn = find_btn(w_, '自动更新')
            if btn:
                state['btn_found'] = True
                btn.invoke()  # 模拟点击
                break
    time.sleep(1.5)
    # 点击后：原弹窗应关闭，进度窗口('更新')应出现（或已进入失败流程）
    tops = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
    state['tops_after'] = [(w.title(), w.winfo_exists()) for w in tops]
    state['has_update_win'] = any(w.title() == '更新' for w in tops)

app.after(200, auto)
app.after(6000, app.destroy)
app.mainloop()
print('找到按钮:', state.get('btn_found'))
print('点击后窗口:', state.get('tops_after'))
print('进度窗口出现:', state.get('has_update_win'))
