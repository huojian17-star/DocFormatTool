# -*- coding: utf-8 -*-
"""修复：把拆解/文案/工具三张卡归入同一 flex 容器（清理残留包装层）。"""
import os

SITE = r"C:\Users\28253\Desktop\portfolio-website"
idx_path = os.path.join(SITE, "index.html")

with open(idx_path, encoding="utf-8") as f:
    idx = f.read()

# 删掉 game-analysis 卡 </a> 与 script-analysis 卡 <a> 之间的残留（</div>、注释、全宽包装 div）
pos_arrow = idx.find("home-card-analysis-arrow")
pos_a_end = idx.find("</a>", pos_arrow) + len("</a>") if pos_arrow != -1 else -1
pos_script = idx.find('<a href="script-analysis.html"', pos_a_end) if pos_a_end != -1 else -1

if pos_arrow != -1 and pos_script != -1 and pos_script > pos_a_end:
    removed = idx[pos_a_end:pos_script]
    idx = idx[:pos_a_end] + idx[pos_script:]
    print("已删除残留段（%d 字符）: %s" % (len(removed), removed.strip()[:60].replace("\n", " | ")))
else:
    print("✗ 定位失败: arrow=%d a_end=%d script=%d" % (pos_arrow, pos_a_end, pos_script))

with open(idx_path, "w", encoding="utf-8") as f:
    f.write(idx)
print("修复完成")
