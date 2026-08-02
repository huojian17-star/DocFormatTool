# -*- coding: utf-8 -*-
"""加新版 doc-tool 页的 i18n 键 + 复制 + 构建 + 提交。"""
import os
import shutil
import subprocess
import sys

SITE = r"C:\Users\28253\Desktop\portfolio-website"
SRC = r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\site\doc-tool.html"

# 1. 复制新版页面
shutil.copy2(SRC, os.path.join(SITE, "doc-tool.html"))
print("doc-tool.html 已复制（新版布局）")

# 2. i18n 新键
i18n_path = os.path.join(SITE, "i18n.js")
keys = [
    ("doc-c1t", "模板自适应", "Template Auto-Adapt"),
    ("doc-c2t", "内容零丢失", "Zero Content Loss"),
    ("doc-c3t", "Markdown 增强", "Markdown Enhanced"),
    ("doc-c4t", "自动质检报告", "Auto Quality Report"),
    ("doc-c5t", "本地 · 隐私", "Local & Private"),
    ("doc-c6t", "开源", "Open Source"),
    ("doc-gallery-h2", "界面一览", "Screenshots"),
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
