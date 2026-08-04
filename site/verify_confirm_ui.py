# -*- coding: utf-8 -*-
"""验证新弹窗：读取弹窗内所有 Label/Combobox 内容（确定性，不依赖截图）"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import tkinter as tk
from tkinter import ttk
from app.main import App

app = App()
app.update()
items = [(5, '1. 研究背景与意义', '随着人工智能技术的快速发展，教育领域正在经历深刻变革。', '本章介绍研究的背景与意义。'),
         (12, '2. 主要研究方法介绍', '研究背景正文内容。', '研究意义正文。'),
         (20, '1. 优点：效率高', '该方案具有以下优点：', '缺点是需要较高成本。')]

state = {}
def auto_action():
    time.sleep(1.0)
    for w_ in app.winfo_children():
        if isinstance(w_, tk.Toplevel):
            state['win_title'] = w_.title()
            labels, combos = [], []
            def walk(widget):
                for c in widget.winfo_children():
                    if isinstance(c, tk.Label):
                        t = c.cget('text')
                        if t:
                            labels.append(t)
                    if isinstance(c, ttk.Combobox):
                        combos.append(c.cget('values'))
                    walk(c)
            walk(w_)
            state['labels'] = labels
            state['combos'] = combos
            # 点确定关闭
            def find_btn(widget):
                for c in widget.winfo_children():
                    if isinstance(c, tk.Button) and c.cget('text') == '确定':
                        return c
                    r = find_btn(c)
                    if r:
                        return r
            b = find_btn(w_)
            if b:
                b.invoke()
            return
    state['no_win'] = True

app.after(300, auto_action)
forced = app._confirm_uncertain_docx(items)
print('窗口标题:', state.get('win_title'))
print()
print('=== Label 文本 ===')
for t in state.get('labels', []):
    print('  ', repr(t)[:80])
print()
print('=== Combobox 选项 ===')
for v in state.get('combos', []):
    print('  ', v)
app.destroy()
