# -*- coding: utf-8 -*-
"""首页 nav-cards 加"论文工具"卡片 + i18n + 搜索索引。"""
import os

SITE = r"C:\Users\28253\Desktop\portfolio-website"
idx_path = os.path.join(SITE, "index.html")
i18n_path = os.path.join(SITE, "i18n.js")

# 新卡片 HTML（复用 card-about 配色 + 绿色边）
card = """
  <a href="doc-tool.html" class="nav-card card-about" style="display:block;border-left:3px solid #3fae8a;">
    <span class="card-badge badge-lore" data-i18n="xdoc-badge">&#9679; 工具</span>
    <span class="card-icon">&#9998;</span>
    <h3 data-i18n="home-card-doc">论文排版工具</h3>
    <p data-i18n="xdoc-p"><span data-i18n="home-card-doc-p-full">论文格式一键排版：自动识别学校模板、图片表格零丢失、Markdown 与 LaTeX 公式支持、排完自动质检出改动报告。完全本地运行，断网可用。</span></p>
    <span class="card-tease" data-i18n="xdoc-tease">排版 · 质检报告 · 本地运行 · 开源</span>
    <span class="card-arrow" data-i18n="home-card-doc-arrow">查看工具 →</span>
  </a>
"""

with open(idx_path, encoding="utf-8") as f:
    idx = f.read()

# 插入：script-analysis 卡片结束后
anchor = '<span class="card-arrow" data-i18n="home-card-script-arrow">阅读拆解 →</span>\n    </a>'
if 'href="doc-tool.html" class="nav-card' in idx:
    print("index.html 已有论文工具卡片")
else:
    if anchor in idx:
        idx = idx.replace(anchor, anchor + "\n" + card, 1)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(idx)
        print("index.html 卡片已插入")
    else:
        print("✗ 锚点未找到")

# 搜索索引加一条
if "{ sel: 'a[href=\"doc-tool.html\"].nav-card'" not in idx:
    idx2 = open(idx_path, encoding="utf-8").read()
    idx_anchor = "{ sel: 'a[href=\"script-analysis.html\"].nav-card', key: 'scriptanalysis', page: 'script-analysis.html' }"
    new_idx = idx_anchor + ",\n      { sel: 'a[href=\"doc-tool.html\"].nav-card',    key: 'doctool',       page: 'doc-tool.html' }"
    if idx_anchor in idx2:
        idx2 = idx2.replace(idx_anchor, new_idx, 1)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(idx2)
        print("搜索索引已加")
    else:
        print("✗ 索引锚点未找到")

# i18n 键
keys = [
    ("xdoc-badge", "&#9679; 工具", "&#9679; Tool"),
    ("home-card-doc", "论文排版工具", "Paper Format Tool"),
    ("xdoc-p", "论文格式一键排版：自动识别学校模板、图片表格零丢失、Markdown 与 LaTeX 公式支持、排完自动质检出改动报告。完全本地运行，断网可用。", "One-click paper formatting: auto school-template parsing, zero content loss, Markdown & LaTeX support, auto quality report. Fully local."),
    ("home-card-doc-p-full", "论文格式一键排版：自动识别学校模板、图片表格零丢失、Markdown 与 LaTeX 公式支持、排完自动质检出改动报告。完全本地运行，断网可用。", "One-click paper formatting: auto school-template parsing, zero content loss, Markdown & LaTeX support, auto quality report. Fully local."),
    ("xdoc-tease", "排版 · 质检报告 · 本地运行 · 开源", "Format · Report · Local · Open Source"),
    ("home-card-doc-arrow", "查看工具 →", "View Tool →"),
]
with open(i18n_path, encoding="utf-8") as f:
    i18n = f.read()
added = 0
for k, zh, en in keys:
    if ("M['%s']" % k) not in i18n:
        i18n += "\nM['%s']={zh:'%s',en:'%s'};" % (k, zh, en)
        added += 1
with open(i18n_path, "w", encoding="utf-8") as f:
    f.write(i18n)
print("i18n.js 新增 %d 个键" % added)
