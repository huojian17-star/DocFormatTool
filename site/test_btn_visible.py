# -*- coding: utf-8 -*-
"""验证展开高级选项后底部按钮完整可见"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import App

app = App()
app.update()
app.var_adv.set(True)
app._on_adv_toggle()
app.update()
time.sleep(0.6)

win_h = app.winfo_height()
print('窗口高=%d' % win_h)

# 递归找所有 Button 的文本和位置
def walk(w, depth=0):
    for c in w.winfo_children():
        try:
            if c.winfo_class() == 'TButton':
                txt = c.cget('text')
                by = c.winfo_y() + c.winfo_rooty() - app.winfo_rooty()
                bh = c.winfo_height()
                visible = (by + bh) <= win_h and by >= 0
                print('  按钮 %r y=%d 高=%d 底部=%d 窗口高=%d -> %s' % (
                    txt, by, bh, by + bh, win_h, '完整可见' if visible else '被裁掉!'))
        except Exception:
            pass
        walk(c, depth + 1)

walk(app)
app.destroy()
print('DONE')
