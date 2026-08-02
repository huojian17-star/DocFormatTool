# -*- coding: utf-8 -*-
"""穷举识别测试：各种标题/摘要/关键词/参考文献格式变体 → 识别矩阵，找出识别盲区。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import infer

CASES = [
    # ---- 一级标题变体 ----
    ("1 引言", "H1"),
    ("1. 引言", "H1"),          # 数字+句点
    ("1、引言", "H1"),
    ("1．引言", "H1"),          # 全角点
    ("1 引言：研究背景", "H1"),  # 冒号
    ("第一章 引言", "H1"),
    ("第1章 引言", "H1"),
    ("一、引言", "H1"),
    ("（一）引言", "H1"),
    ("（1）引言", "H1"),
    ("5 结论与政策建议", "H1"),
    ("1 引言。", "正文"),        # 句读结尾 → 非标题
    ("1 这是一个超级长的标题用来测试超过六十个字符的标题是否会被正确识别为正文而不是标题因为标题不可能有这么长的一段话而且还超过了七十个字符", "正文"),
    # ---- 二级/三级 ----
    ("1.1 背景", "H2"),
    ("1.1 背景：文献综述", "H2"),
    ("1.1.1 小节", "H3"),
    ("4.2.1 变量定义", "H3"),
    ("2.1 股权集中度与企业绩效：激励效应与隧道效应", "H2"),
    # ---- 摘要/关键词 ----
    ("摘要", "ABS"),
    ("摘 要", "ABS"),
    ("摘要：", "ABS"),
    ("摘要：随着短视频平台的快速发展……", "ABS"),  # 摘要+内容混合：infer 标 abstract_heading（消费方按长度转正文）
    ("ABSTRACT", "ABS"),        # 英文摘要（已支持）
    ("Abstract:", "ABS"),
    ("关键词", "KW"),
    ("关键词：数据挖掘；机器学习", "KW"),
    ("KEY WORDS", "KW"),        # 英文关键词（已支持）
    # ---- 参考文献 ----
    ("参考文献", "REF"),
    ("参考文献：", "REF"),
    ("[1] 张三. 论文标题[J]. 期刊, 2024.", "REFITEM"),
    ("1. 张三. 论文标题[M]. 北京: 出版社, 2023.", "REFITEM"),  # 数字列表式文献
    ("张三. 论文标题[J]. 期刊, 2024.", "REFITEM"),  # 无编号文献
    # ---- 图表题注 ----
    ("图 1 系统架构图", "CAP"),
    ("图1 系统架构图", "CAP"),
    ("图1-1 系统架构图", "CAP"),
    ("表 2 变量说明", "CAP"),
    # ---- 其他 ----
    ("附录", "APP"),
    ("致谢", "正文"),
    ("目录", "正文"),
    ("目 录", "正文"),
]

EXPECT_MAP = {
    "H1": "heading1", "H2": "heading2", "H3": "heading3",
    "ABS": "abstract_heading", "KW": "keywords", "REF": "ref_heading",
    "REFITEM": "ref_item", "CAP": "caption", "APP": "appendix", "正文": "body",
}

ok = 0
bad = []
print("%-46s %-10s %-12s" % ("输入", "期望", "实际"))
print("-" * 72)
for text, expect in CASES:
    t, _ = infer._classify(text, md_mode=False)
    target = EXPECT_MAP.get(expect, expect)
    match = "✓" if t == target else "✗"
    if match == "✗":
        bad.append((text, expect, t))
    else:
        ok += 1
    print("%-46s %-10s %-12s %s" % (text[:44], expect, t, match))
print("-" * 72)
print("通过 %d/%d" % (ok, len(CASES)))
print("失败项:")
for text, exp, act in bad:
    print("  ✗ %r 期望=%s 实际=%s" % (text, exp, act))
