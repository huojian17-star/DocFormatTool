# -*- coding: utf-8 -*-
"""测试：点击"自动更新"→ 进度窗口在主线程正常出现（修复后）"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import tkinter as tk
from app.main import App

app = App()
app.update()

state = {}
def auto():
    time.sleep(0.8)
    # 触发下载（url 用无效的，验证窗口出现后走失败分支）
    app._start_download('https://127.0.0.1:1/nonexistent.exe', '', '')
    time.sleep(1.0)
    # 检查进度窗口是否出现
    wins = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel) and w.title() == '更新']
    state['progress_win'] = len(wins) > 0
    if wins:
        # 截图
        from PIL import ImageGrab
        x, y = wins[0].winfo_rootx(), wins[0].winfo_rooty()
        w, h = wins[0].winfo_width(), wins[0].winfo_height()
        ImageGrab.grab(bbox=(x-5, y-5, x+w+5, y+h+5)).save(
            os.path.join(os.path.dirname(__file__), '..', 'gui_update_win.png'))
    # 等失败弹窗出现
    time.sleep(3)
    state['win_count'] = len([w for w in app.winfo_children() if isinstance(w, tk.Toplevel)])

app.after(200, auto)
app.after(6000, app.destroy)
app.mainloop()
print('进度窗口出现:', state.get('progress_win'))
print('截图: gui_update_win.png')
