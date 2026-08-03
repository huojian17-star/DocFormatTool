# -*- coding: utf-8 -*-
"""WPS COM 转 PDF（参数化，带 90s 超时保护）。用法: python render_any.py <src.docx> <out.pdf>"""
import os, sys, threading

def do_convert(src, out):
    import win32com.client
    app = win32com.client.DispatchEx("Kwps.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    doc = app.Documents.Open(os.path.abspath(src), ReadOnly=True)
    try:
        doc.ExportAsFixedFormat(os.path.abspath(out), 17)
        print("WPS 转换成功:", out, os.path.getsize(out), "字节")
    finally:
        doc.Close(False)
        app.Quit()

src, out = sys.argv[1], sys.argv[2]
t = threading.Thread(target=do_convert, args=(src, out), daemon=True)
t.start()
t.join(timeout=90)
if t.is_alive():
    print("WPS COM 超时（90s）——可能被当前打开的 WPS 实例冲突")
