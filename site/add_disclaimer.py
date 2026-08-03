# -*- coding: utf-8 -*-
"""网站 doc-tool.html 加免责声明段。"""
p = r"C:\Users\28253\Desktop\portfolio-website\doc-tool.html"
with open(p, encoding="utf-8") as f:
    s = f.read()

block = (
    "\n  <h2 data-i18n=\"doc-disclaimer-h2\">免责声明</h2>\n"
    "  <p data-i18n=\"doc-disclaimer-p\">本工具仅提供<b>格式排版</b>功能"
    "（字体、字号、标题层级、页码、参考文献格式等），不修改论文任何内容；"
    "<b>不提供</b>代写、降重、降低 AIGC 检测、保证通过审核等服务。"
    "论文的内容与学术诚信由作者本人负责，请遵守学校与期刊的学术规范。</p>\n"
)

if "doc-disclaimer" in s:
    print("doc-tool.html 已有免责声明")
else:
    anchor = "doc-contact-p"
    pos = s.find(anchor)
    assert pos != -1, "找不到 doc-contact-p 锚点"
    end = s.find("</p>", pos)
    assert end != -1, "找不到段落结束"
    insert_at = s.find("\n", end)
    s = s[:insert_at] + block + s[insert_at:]
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    print("doc-tool.html 已加免责声明段")
