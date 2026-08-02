# -*- coding: utf-8 -*-
"""首页卡片区整理：拆解/文案/工具三张全宽卡改为三列并排（与 B站/设定/小说同款），成 3x2 网格。"""
import os

SITE = r"C:\Users\28253\Desktop\portfolio-website"
idx_path = os.path.join(SITE, "index.html")

with open(idx_path, encoding="utf-8") as f:
    idx = f.read()

# 1. game-analysis 卡前插入 flex 容器开头（复用 home-triangle-bottom 样式）
container_open = '<div class="home-triangle-bottom" style="display:flex;gap:20px;max-width:960px;margin:0 auto;padding:12px 0 0;">\n  '
anchor1 = '<a href="game-analysis.html" class="nav-card card-design"'
if anchor1 in idx:
    idx = idx.replace(anchor1, container_open + anchor1, 1)
    print("容器开头已插入（game-analysis 前）")

# 2. 三张卡 style 改为三列
for old, new in [
    ('style="display:block;border-left:3px solid var(--accent);"', 'style="flex:1;min-width:0;"'),
    ('style="display:block;border-left:3px solid #7266ba;"', 'style="flex:1;min-width:0;"'),
    ('style="display:block;border-left:3px solid #3fae8a;"', 'style="flex:1;min-width:0;"'),
]:
    if old in idx:
        idx = idx.replace(old, new, 1)
        print("style 已改:", old[:45])

# 3. doc-tool 卡 </a> 后闭合容器
mark = "home-card-doc-arrow"
pos = idx.find(mark)
if pos != -1:
    end = idx.find("</a>", pos)
    if end != -1:
        insert_at = end + len("</a>")
        idx = idx[:insert_at] + "\n</div>" + idx[insert_at:]
        print("容器闭合已插入（doc-tool 卡后）")
    else:
        print("✗ 找不到 doc-tool </a>")
else:
    print("✗ 找不到 home-card-doc-arrow")

with open(idx_path, "w", encoding="utf-8") as f:
    f.write(idx)
print("完成")
