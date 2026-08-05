# -*- coding: utf-8 -*-
"""吉祥物图标嵌入 main.py：resize 300px → base64 → 标题栏插入"""
import base64, io, re
from PIL import Image

P = r'app\main.py'
src = open(P, encoding='utf-8').read()

# 1) 直接嵌入抠图原图（不再预缩小——避免双重缩小导致模糊；显示时一次 subsample）
img = Image.open(r'site\mascot_raw.png').convert('RGBA')
print('嵌入原图:', img.size)
buf = io.BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()
print('base64 长度:', len(b64))

# 2) 顶部插入常量（在第一个 import 块后）
marker = 'import base64 as _b64\n_MASCOT_B64 = '  # 防重复
if '_MASCOT_B64' in src:
    src = re.sub(r'_MASCOT_B64 = "[^"]*"', '_MASCOT_B64 = "%s"' % b64, src, count=1)
else:
    anchor = 'import tkinter as tk'
    i = src.find(anchor)
    assert i > 0
    insert = '\n_MASCOT_B64 = "%s"\n' % b64
    src = src[:i] + insert + src[i:]

# 3) 标题栏插入图标（在 DocFormatTool Label 前）
old_head = '''        tk.Label(frm_head, text="DocFormatTool", bg=self.PANEL, fg="#1E293B",
                 font=("Microsoft YaHei", 14, "bold")).pack(side="left", padx=20)'''
new_head = '''        # 吉祥物图标（红圈位置：标题文字左侧）
        try:
            self._mascot_img = tk.PhotoImage(data=_MASCOT_B64).subsample(8, 8)
            tk.Label(frm_head, image=self._mascot_img, bg=self.PANEL).pack(side="left", padx=(14, 2))
        except Exception:
            pass
        tk.Label(frm_head, text="DocFormatTool", bg=self.PANEL, fg="#1E293B",
                 font=("Microsoft YaHei", 14, "bold")).pack(side="left", padx=6)'''
# 3) 标题栏已嵌入过（幂等跳过）——只保留 b64 替换逻辑
# （标题栏代码：main.py 中已含 subsample(25,25) 的吉祥物 Label，无需再改）
print('标题栏已就位，跳过（b64 已替换）')

open(P, 'w', encoding='utf-8', newline='').write(src)
print('嵌入完成：标题栏已加吉祥物图标')
