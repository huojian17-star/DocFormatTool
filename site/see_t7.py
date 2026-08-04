# -*- coding: utf-8 -*-
import fitz, sys, os, importlib.util
sys.path.insert(0, r'thesis-format-tool\tools')
spec = importlib.util.spec_from_file_location('srv', r'thesis-format-tool\tools\mcp_vision_server.py')
srv = importlib.util.module_from_spec(spec); spec.loader.exec_module(srv)
doc = fitz.open(r'F:\论文排版工具_测试包\测试套件\T7_样式与脚注_排版后.pdf')
for i in range(doc.page_count):
    pix = doc[i].get_pixmap(dpi=150)
    png = r'F:\论文排版工具_测试包\测试套件\T7_p%d.png' % (i + 1)
    pix.save(png)
print('已渲染 %d 页' % doc.page_count)
q = ('这是论文排版结果的第一页。请检查：'
     '1) 第一行大标题（论文题目）是否居中醒目 2) 摘要段落和关键词行的排版 3) 有无文字错乱。'
     '另外请特别注意：文中是否有"1. 数据来源于国家统计局：https://..."这类脚注行，它们看起来像正文小字还是像章节标题？简要回答。')
r = srv._call_minimax(r'F:\论文排版工具_测试包\测试套件\T7_p1.png', q, 'high')
print(r[:600])
