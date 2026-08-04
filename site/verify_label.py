# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
import llm_label as L

tests = ["一、总体要求", "（一）指导思想", "1. 优点：效率高", "1. 数据来源于国家统计局：https://data.stats.gov.cn/",
         "第一章 绪论", "1.1 研究背景", "[1] 张伟. 教育研究[J]. 2025.", "关键词：人工智能；教育"]
labels = L.call_llm(tests)
norm = L.normalize_labels(labels)
print("MODEL:", L.MODEL, "| 归一化 %d 条" % len(norm))
for d in norm:
    print("  %-20s → %s" % (d["text"][:20], d["role"]))
