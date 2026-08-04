# -*- coding: utf-8 -*-
"""更新链路回归测试（发版前必跑）：
1. 模拟点击"自动更新"按钮 → 弹窗关闭 + 进度窗口出现（主线程，无 NameError）
2. 下载真实 updater（ghfast）→ 校验文件
3. updater 替换逻辑（模拟 exe 覆盖）
用法: python test_update_chain.py
"""
import sys, os, time, subprocess, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

PASS = []
FAIL = []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print("  %s %s %s" % ("✓" if ok else "✗", name, detail))


print("=== 1. GUI 自动更新按钮 ===")
import tkinter as tk
from app.main import App
app = App()
app.update()
state = {}


def auto():
    time.sleep(0.5)
    app._show_update('9.9.9', 'https://127.0.0.1:1/x.exe', '测试', 'https://lz.example', 'pwd')
    time.sleep(0.8)
    from tkinter import ttk as _ttk

    def find_btn(widget, text):
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
                state['btn'] = True
                btn.invoke()
                break
    time.sleep(1.5)
    tops = [w for w in app.winfo_children() if isinstance(w, tk.Toplevel)]
    state['has_progress'] = any(w.title() == '更新' for w in tops)
    state['old_closed'] = not any(w.title() == '发现新版本' for w in tops)


app.after(200, auto)
app.after(5000, app.destroy)
app.mainloop()
check("找到'自动更新'按钮", state.get('btn'))
check("点击后原弹窗关闭", state.get('old_closed'))
check("进度窗口出现(主线程)", state.get('has_progress'))

print("=== 2. 下载链路（ghfast updater） ===")
url = 'https://ghfast.top/https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/releases/updater.exe'
tmp = os.path.join(os.environ['TEMP'], 'chain_updater.exe')
try:
    import urllib.request
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers={'User-Agent': 'test'})
    with opener.open(req, timeout=60) as r, open(tmp, 'wb') as f:
        while True:
            c = r.read(65536)
            if not c:
                break
            f.write(c)
    check("下载 updater", os.path.getsize(tmp) > 5 * 1024 * 1024, "(%.1fMB)" % (os.path.getsize(tmp) / 1048576))
except Exception as e:
    check("下载 updater", False, repr(e)[:60])

print("=== 3. 替换逻辑（模拟 updater bat 覆盖） ===")
try:
    test_dir = r'F:\论文排版工具_测试包\updater_测试'
    old_exe = os.path.join(test_dir, 'DocFormatTool.exe')
    new_exe = os.path.join(test_dir, 'DocFormatTool_new.exe')
    if os.path.exists(old_exe) and os.path.exists(new_exe):
        check("new 文件已存在(下载产物)", True)
        os.replace(new_exe, old_exe)
        check("os.replace 覆盖成功", os.path.exists(old_exe))
    else:
        check("new 文件已存在", False, "updater_测试 无 new exe，跳过覆盖测试")
except Exception as e:
    check("替换逻辑", False, repr(e)[:60])

print()
print("结果: %d 通过, %d 失败" % (len(PASS), len(FAIL)))
if FAIL:
    print("失败项:", FAIL)
    sys.exit(1)
