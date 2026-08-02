# -*- coding: utf-8 -*-
"""生成 30 秒竖屏宣传片（1080x1920）：PIL 文字卡 + moviepy 淡入淡出合成。

素材：8 张卡片（痛点/产品/功能/信任/引流），每张 3.5s + 0.5s 交叉淡化 ≈ 30s。
"""
import os
import sys

import PIL
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "video")
CARD_DIR = os.path.join(OUT_DIR, "cards")
os.makedirs(CARD_DIR, exist_ok=True)

W, H = 1080, 1920
FONT_BIG = r"C:\Windows\Fonts\msyhbd.ttc"   # 微软雅黑粗
FONT_MID = r"C:\Windows\Fonts\msyh.ttc"     # 微软雅黑
FONT_FALLBACK = r"C:\Windows\Fonts\simhei.ttf"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(FONT_FALLBACK, size)


def _card(filename, lines, bg=(12, 16, 24), fg=(245, 245, 245),
          accent=(255, 190, 60), center=True, size_big=88, size_mid=52, gap=36):
    """画一张竖屏卡片：lines = [(text, kind)] kind: big|mid|accent"""
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # 顶部细装饰条
    d.rectangle([0, 0, W, 14], fill=accent)
    y = H // 2 - (len(lines) * (size_big if size_big else size_mid) + (len(lines) - 1) * gap) // 2
    for text, kind in lines:
        if kind == "big":
            f = _font(FONT_BIG, size_big)
            c = fg
        elif kind == "accent":
            f = _font(FONT_BIG, size_big)
            c = accent
        else:
            f = _font(FONT_MID, size_mid)
            c = (200, 205, 215)
        w = d.textlength(text, font=f)
        d.text(((W - w) // 2, y), text, font=f, fill=c)
        y += size_big if kind in ("big", "accent") else size_mid
        y += gap
    img.save(os.path.join(CARD_DIR, filename))


# 8 张卡片：30 秒节奏
_card("c1.png", [("论文格式", "big"), ("改吐了？", "accent")], bg=(12, 16, 24))
_card("c2.png", [("字体乱、行距错", "big"), ("页码对不上", "big"),
                 ("表格里字五花八门", "mid"), ("改格式比写正文还累", "accent")], bg=(24, 20, 18))
_card("c3.png", [("规范文档一键排版工具", "accent"), ("", "mid"),
                 ("论文丢进去", "big"), ("选个模板", "big"), ("一键排版", "big")], bg=(16, 24, 32))
_card("c4.png", [("图片表格", "big"), ("原样保留", "accent"),
                 ("只动格式", "mid"), ("不改你一个字", "accent")], bg=(16, 28, 22))
_card("c5.png", [("Markdown 也能排", "big"), ("", "mid"),
                 ("表格 · 代码块 · LaTeX 公式", "mid"), ("工科生友好", "accent")], bg=(24, 20, 32))
_card("c6.png", [("排完自动质检", "big"), ("", "mid"),
                 ("生成《改动报告》", "accent"), ("改了啥、覆盖率多少", "mid"), ("一目了然", "big")], bg=(20, 24, 28))
_card("c7.png", [("论文不离开你的电脑", "big"), ("断网也能用", "accent"),
                 ("不上传、不采集", "mid")], bg=(16, 24, 24))
_card("c8.png", [("开源在 GitHub", "big"), ("", "mid"),
                 ("免费测试中", "accent"), ("私信我，一人一个码", "mid")], bg=(12, 12, 20))

print("8 张卡片已生成 ->", CARD_DIR)
