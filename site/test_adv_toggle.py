# -*- coding: utf-8 -*-
"""验证高级选项展开后底部按钮完整可见（自动截图 + 坐标检查）"""
import sys, time, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from PIL import ImageGrab

from app.main import App

app = App()
app.update()
time.sleep(1.0)

# 截图1：初始状态（高级选项收起）
x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()
img1 = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img1.save(os.path.join(os.path.dirname(__file__), '..', 'gui_collapsed.png'))
print('收起状态: 窗口 %dx%d 请求高度 %d' % (w, h, app.winfo_reqheight()))

# 展开高级选项
app.var_adv.set(True)
app._on_adv_toggle()
app.update()
time.sleep(1.0)

# 截图2：展开状态
x, y = app.winfo_rootx(), app.winfo_rooty()
w, h = app.winfo_width(), app.winfo_height()
img2 = ImageGrab.grab(bbox=(x, y, x + w, y + h))
img2.save(os.path.join(os.path.dirname(__file__), '..', 'gui_expanded.png'))
print('展开状态: 窗口 %dx%d 请求高度 %d 屏幕高 %d' % (w, h, app.winfo_reqheight(), app.winfo_screenheight()))

# 收起恢复
app.var_adv.set(False)
app._on_adv_toggle()
app.update()
print('收起后高度: %d (应回到 ~760)' % app.winfo_height())

app.destroy()
print('DONE')
