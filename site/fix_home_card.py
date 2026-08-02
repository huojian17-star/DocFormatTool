# -*- coding: utf-8 -*-
"""修正：首页卡片按闭合 </a> 定位插入。"""
import os

SITE = r"C:\Users\28253\Desktop\portfolio-website"
idx_path = os.path.join(SITE, "index.html")

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

if 'href="doc-tool.html" class="nav-card' in idx:
    print("已存在，跳过")
else:
    # 定位 script-analysis 卡片箭头，找其后第一个 </a>（卡片闭合）
    mark = "home-card-script-arrow"
    pos = idx.find(mark)
    if pos == -1:
        print("✗ 找不到 home-card-script-arrow")
        raise SystemExit
    end = idx.find("</a>", pos)
    if end == -1:
        print("✗ 找不到闭合 </a>")
        raise SystemExit
    insert_at = end + len("</a>")
    idx = idx[:insert_at] + card + idx[insert_at:]
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(idx)
    print("卡片已插入（script-analysis 卡片后）")
