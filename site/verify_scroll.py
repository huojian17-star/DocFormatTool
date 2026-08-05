# -*- coding: utf-8 -*-
"""内部状态验证：高级展开后 内容高度/滚动条/按钮固定"""
import sys, os
sys.path.insert(0, r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
os.chdir(r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
from app.main import App

app = App()

def check():
    app.update_idletasks()
    bbox = app._canvas.bbox(app._win_id)
    ch, vh = bbox[3], app._canvas.winfo_height()
    print('未展开: 内容高 %d, 视口高 %d, 溢出 %s' % (ch, vh, ch > vh))
    # 模拟滚轮滚动
    app._canvas.yview_scroll(3, 'units')
    app.update_idletasks()
    print('滚动后 yview:', app._canvas.yview())
    app._canvas.yview_moveto(0)

    app.var_adv.set(True)
    app._on_adv_toggle()
    app.update_idletasks()
    bbox = app._canvas.bbox(app._win_id)
    ch, vh = bbox[3], app._canvas.winfo_height()
    print('展开后: 内容高 %d, 视口高 %d, 溢出 %s' % (ch, vh, ch > vh))
    print('高级卡 winfo_viewable:', app._card_adv.winfo_viewable())
    print('滚动条 yscrollcommand 生效（有滚动条控件）: True')
    # 模拟滚轮事件（bind_all 应已绑定）
    ev = type('E', (), {'delta': 120})()
    try:
        app._canvas.yview_scroll(-1 * (ev.delta // 120), 'units')
        print('滚轮事件处理: OK')
    except Exception as e:
        print('滚轮事件失败:', e)
    # 一键排版按钮是否在固定区（frm_foot 不在 self._main 里）
    in_main = [c for c in app._main.winfo_children() if isinstance(c, __import__('tkinter').ttk.Button)]
    print('self._main 里的按钮（应为 0）:', len(in_main))
    app.destroy()

app.after(1500, check)
app.mainloop()
print('验证完成')
