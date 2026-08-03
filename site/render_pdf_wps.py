# -*- coding: utf-8 -*-
"""WPS COM 转 PDF（单方法，带 90s 超时保护）。"""
import os, sys, time, threading

SRC = r"F:\论文排版工具_测试包\_render_tmp.docx"
OUT = r"F:\论文排版工具_测试包\_render_check.pdf"

def do_convert():
    import win32com.client
    app = win32com.client.DispatchEx("Kwps.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    doc = app.Documents.Open(os.path.abspath(SRC), ReadOnly=True)
    try:
        doc.ExportAsFixedFormat(os.path.abspath(OUT), 17)
        print("WPS 转换成功:", OUT, os.path.getsize(OUT), "字节")
    finally:
        doc.Close(False)
        app.Quit()

t = threading.Thread(target=do_convert, daemon=True)
t.start()
t.join(timeout=90)
if t.is_alive():
    print("WPS COM 超时（90s）——可能被当前打开的 WPS 实例冲突")











