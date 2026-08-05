# -*- coding: utf-8 -*-
"""内部验证：frm_foot 底部固定区是否真的显示"""
import sys, os
sys.path.insert(0, r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
os.chdir(r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
from app.main import App

app = App()

def check():
    app.update_idletasks()
    frm_main = app._canvas.master
    print('frm_main 子控件布局:')
    for c in frm_main.winfo_children():
        print('  %-16s y=%-4d h=%-4d w=%-4d viewable=%s' % (
            c.winfo_class(), c.winfo_y(), c.winfo_height(), c.winfo_width(), c.winfo_viewable()))
    # 找按钮（一键排版）
    def find_btn(w, path=''):
        for c in w.winfo_children():
            try:
                if c.winfo_class() == 'TButton' and '一键排版' in str(c.cget('text')):
                    print('找到一键排版按钮:', path, 'y=%d h=%d viewable=%s' % (c.winfo_rooty(), c.winfo_height(), c.winfo_viewable()))
                find_btn(c, path + '/')
            except Exception:
                pass
    find_btn(app)
    app.destroy()

app.after(1500, check)
app.mainloop()
print('完成')
