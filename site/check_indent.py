# -*- coding: utf-8 -*-
"""检查 [6][7][1] 条目的 pPr 完整结构"""
from docx import Document
import re
import lxml.etree as ET

d = Document(r'F:\论文排版工具_测试包\_render_tmp.docx')
for p in d.paragraphs:
    t = p.text.strip()
    if re.match(r'^\[(6|7|1)\]', t):
        pPr = p._p.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr')
        s = ET.tostring(pPr, pretty_print=True).decode() if pPr is not None else 'None'
        s = re.sub(r' xmlns:\w+="[^"]*"', '', s)
        print('===', t[:16], '===')
        print(s)
