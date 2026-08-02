# -*- coding: utf-8 -*-
"""识别平衡基准：正例集（该识别的）+ 负例集（不该识别的），量化 识别率/误判率。"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import infer

# 正例：期望识别为 标题/摘要/关键词/参考文献/题注/附录
POSITIVE = [
    # 标题
    ("1 引言", "heading1"),
    ("1. 引言", "heading1"),          # 非 md 场景（txt）
    ("1、引言", "heading1"),
    ("1．引言", "heading1"),
    ("1 引言：研究背景", "heading1"),
    ("第一章 引言", "heading1"),
    ("第1章 引言", "heading1"),        # 阿拉伯数字章（新修）
    ("第3章 数据挖掘设计", "heading1"),
    ("一、引言", "heading1"),
    ("（一）引言", "heading1"),        # 括号标题（新修）
    ("（1）引言", "heading1"),
    ("5 结论与政策建议", "heading1"),
    ("1.1 背景", "heading2"),
    ("1.1 背景：文献综述", "heading2"),
    ("1.1.1 小节", "heading3"),
    ("4.2.1 变量定义", "heading3"),
    ("2.1 股权集中度与企业绩效：激励效应与隧道效应", "heading2"),
    ("第二章 文献综述", "heading1"),
    ("四、实验与结果", "heading1"),
    # 摘要/关键词（含英文，新修）
    ("摘要", "abstract_heading"),
    ("摘 要", "abstract_heading"),
    ("摘要：", "abstract_heading"),
    ("ABSTRACT", "abstract_heading"),
    ("Abstract:", "abstract_heading"),
    ("关键词", "keywords"),
    ("关键词：数据挖掘；机器学习", "keywords"),
    ("KEY WORDS", "keywords"),
    ("Keywords:", "keywords"),
    # 参考文献
    ("参考文献", "ref_heading"),
    ("参考文献：", "ref_heading"),
    ("[1] 张三. 论文标题[J]. 期刊, 2024.", "ref_item"),
    ("张三. 论文标题[J]. 期刊, 2024.", "ref_item"),   # 无编号（新修）
    ("王五. 书名[M]. 北京: 出版社, 2023.", "ref_item"),
    ("[2] Smith J. A paper title[C]. 2024.", "ref_item"),
    # 图表题注/附录
    ("图 1 系统架构图", "caption"),
    ("图1-1 系统架构图", "caption"),
    ("表 2 变量说明", "caption"),
    ("附录", "appendix"),
]

# 负例：不应该识别为 标题/摘要/文献 等（普通正文/列表/数据）
NEGATIVE = [
    "1. 优点：效率高、成本低、易维护",        # 列举
    "1. 第一点建议",                         # 短列表
    "1. 引言部分主要介绍了本文的研究背景和意义",  # 长句（超60？数一下约24字，短——但句意是正文）
    "3 个样本的测试结果显示性能显著提升",        # 数字+单位开头
    "2.5 元的价格差值得关注",                 # 价格
    "0.05 显著性水平下结论成立",               # 统计数字
    "第一章 我们讨论了数据预处理的方法和步骤",     # 第X章+代词开头
    "1.1 节回顾了相关工作",                   # "1.1 节"不是标题
    "图 1 展示的是系统整体架构图的效果示意",      # 叙述句非题注
    "表 2 给出的是各变量的描述性统计",          # 叙述句非题注
    "参考文献 是论文的重要组成部分",            # 非标题用法
    "目录 页列出了所有章节",                  # 非标题用法
    "研究背景 本文从数据挖掘的角度出发……",       # 无编号长句
    "网络爬虫技术 在数据采集中应用广泛",          # 名词短语开头（无编号）
    "1 个样本量为三十的实验验证了假设",          # 数字+量词长句
    "5 种方法的效果对比如下表所示",            # 数字+量词
    "摘要 部分 本文首先介绍了研究背景和方法论",    # 摘要非标题用法
]

H1_TYPES = ("heading1", "heading2", "heading3")
ABS_TYPES = ("abstract_heading", "keywords", "ref_heading", "ref_item", "caption", "appendix")


def run(label, cases, md_mode=False):
    ok = 0
    fails = []
    for text, expect in cases:
        t, _ = infer._classify(text, md_mode=md_mode)
        if t == expect:
            ok += 1
        else:
            fails.append((text, expect, t))
    rate = ok / len(cases) * 100
    print("%s: %d/%d (%.0f%%)" % (label, ok, len(cases), rate))
    for text, exp, act in fails:
        print("  ✗ %r 期望=%s 实际=%s" % (text[:40], exp, act))
    return rate


print("=" * 60)
print("识别平衡基准（txt 模式 md_mode=False）")
print("=" * 60)
pos = run("识别率（正例 40 项）", POSITIVE)
neg = run("误判率（负例 17 项）", [ (t, "body") for t in NEGATIVE ])

# md 模式负例（"1. xxx" 应为列表正文）
print("-" * 60)
print("md 模式（md_mode=True）：'1. xxx' 应为正文（有序列表）")
md_ok = 0
for text in ["1. 优点：效率高、成本低", "1. 第一点建议", "1. 引言部分主要介绍了本文的研究背景和意义"]:
    t, _ = infer._classify(text, md_mode=True)
    match = t == "body"
    md_ok += 1 if match else 0
    print("  %s %r -> %s" % ("✓" if match else "✗", text[:30], t))
print("md 模式列表识别: %d/3" % md_ok)
print("=" * 60)
print("结论：识别率 %.0f%% / 误判率 %.0f%%" % (pos, 100 - neg))
