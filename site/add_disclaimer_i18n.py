# -*- coding: utf-8 -*-
"""网站 i18n.js 补免责声明双语键（M['key']={zh:...,en:...}; 格式）。"""
p = r"C:\Users\28253\Desktop\portfolio-website\i18n.js"
with open(p, encoding="utf-8") as f:
    s = f.read()

if "doc-disclaimer" in s:
    print("i18n.js 已有免责声明键")
else:
    add = (
        "M['doc-disclaimer-h2']={zh:'免责声明',en:'Disclaimer'};\n"
        "M['doc-disclaimer-p']={zh:'本工具仅提供格式排版功能（字体、字号、标题层级、页码、参考文献格式等），不修改论文任何内容；不提供代写、降重、降低 AIGC 检测、保证通过审核等服务。论文的内容与学术诚信由作者本人负责，请遵守学校与期刊的学术规范。',en:'This tool only formats layout (fonts, sizes, heading levels, page numbers, reference styles) and never modifies your content. It does NOT provide ghostwriting, paraphrasing, AI-detection evasion, or any guarantee of passing review. Authors are solely responsible for academic integrity.'};\n"
    )
    pos = s.find("M['doc-contact-p']")
    assert pos != -1, "找不到 doc-contact-p 键"
    s = s[:pos] + add + s[pos:]
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    print("i18n.js 已补免责声明双语键")
