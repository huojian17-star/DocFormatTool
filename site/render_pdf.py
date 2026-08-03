# -*- coding: utf-8 -*-
"""docx → PDF 渲染（优先 Word COM，其次 WPS COM），用于视觉自查排版效果。"""
import os, sys

SRC = r"F:\论文排版工具_测试包\毕业论文_人工智能技术在教育领域的应用与影响研究_已排版.docx"
OUT = r"F:\论文排版工具_测试包\_render_check.pdf"

def via_word():
    import win32com.client
    app = win32com.client.DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    doc = app.Documents.Open(os.path.abspath(SRC), ReadOnly=True)
    doc.ExportAsFixedFormat(os.path.abspath(OUT), 17)  # 17 = wdExportFormatPDF
    doc.Close(False)
    app.Quit()
    return True

def via_wps():
    import win32com.client
    app = win32com.client.DispatchEx("Kwps.Application")
    app.Visible = False
    doc = app.Documents.Open(os.path.abspath(SRC), ReadOnly=True)
    doc.ExportAsFixedFormat(os.path.abspath(OUT), 17)
    doc.Close(False)
    app.Quit()
    return True

for fn in (via_word, via_wps):
    try:
        fn()
        print("转换成功 ->", OUT, os.path.getsize(OUT), "字节")
        break
    except Exception as e:
        print(fn.__name__, "失败:", str(e)[:120])
