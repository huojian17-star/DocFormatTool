# -*- coding: utf-8 -*-
"""给所有板块页导航统一加"论文工具"链接。"""
import glob
import os

SITE = r"C:\Users\28253\Desktop\portfolio-website"
anchor = '<a href="gaming.html" data-i18n="nav-gaming">游戏经历</a>'
new = anchor + '\n      <a href="doc-tool.html" data-i18n="nav-doc-tool">论文工具</a>'
count = 0
for f in glob.glob(os.path.join(SITE, "*.html")):
    base = os.path.basename(f)
    if base in ("index.html", "doc-tool.html"):
        continue
    with open(f, encoding="utf-8") as fh:
        c = fh.read()
    if 'href="doc-tool.html"' in c:
        continue
    if anchor in c:
        c = c.replace(anchor, new, 1)
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(c)
        count += 1
        print("已加链接:", base)
print("共 %d 个页面" % count)
