# -*- coding: utf-8 -*-
"""查看题目段落的 XML 结构（找 run 之间的隐藏换行元素）。"""
from docx import Document
from docx.oxml.ns import qn
import re

src = r"F:\论文排版工具_测试包\_验证2_已排版.docx"
d = Document(src)
for p in d.paragraphs:
    t = p.text.strip()
    if "人工智能技术在教育" in t:
        xml = p._p.xml
        xml = re.sub(r" xmlns:\w+=\"[^\"]*\"", "", xml)
        xml = re.sub(r"<w:(\w+)[^>]*/>", r"<\1/>", xml)
        xml = re.sub(r"<w:(\w+)[^>]*>", r"<\1>", xml)
        xml = re.sub(r"</w:(\w+)>", r"</\1>", xml)
        # 标记 run 和特殊元素
        xml = xml.replace("<r>", "\n  <r>").replace("</r>", "</r>")
        # 删掉 rPr 细节
        xml = re.sub(r"<rPr>.*?</rPr>", "<rPr/>", xml, flags=re.S)
        print(xml[:2000])
        break
