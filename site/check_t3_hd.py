# -*- coding: utf-8 -*-
import fitz, sys, os, importlib.util
sys.path.insert(0, r'thesis-format-tool\tools')
spec = importlib.util.spec_from_file_location('srv', r'thesis-format-tool\tools\mcp_vision_server.py')
srv = importlib.util.module_from_spec(spec); spec.loader.exec_module(srv)
doc = fitz.open(r'F:\论文排版工具_测试包\测试套件\T3_混合体系.pdf')
pix = doc[0].get_pixmap(dpi=170)
png = r'F:\论文排版工具_测试包\测试套件\T3_p1_hd.png'
pix.save(png)
print('已存高清单页')
q = ('论文渲染图第一页。请精确比较这几行文字的字号大小顺序（从大到小）：'
     '【第一章 绪论】【一、研究背景】【（一）国内现状】【（二）国外现状】'
     '以及正文【绪论正文内容。】。'
     '用 > 或 < 列出它们的大小关系，例如：A>B>C>正文。只回答大小关系。')
r = srv._call_minimax(png, q, 'high')
print(r[:500])
