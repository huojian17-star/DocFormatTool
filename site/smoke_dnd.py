# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
os.chdir(r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool')
from app.main import App

app = App()
print('窗口创建 OK')
print('拖拽注入可用:', hasattr(app, 'drop_target_register') and hasattr(app, 'dnd_bind'))

def done():
    # 模拟拖放事件解析（构造 Tcl list 格式）
    try:
        files = app.tk.splitlist('{C:/test dir/论文.txt} {D:/other.docx}')
        print('多文件解析:', files)
        app.var_input.set(files[0])
        print('输入框已填:', app.var_input.get())
    except Exception as e:
        print('解析失败:', e)
    app.destroy()

app.after(1200, done)
app.mainloop()
print('冒烟完成')
