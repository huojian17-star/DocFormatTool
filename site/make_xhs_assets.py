# -*- coding: utf-8 -*-
"""小红书宣传素材 v2：统一 3:4 画布 + 翡翠绿主色 + 圆角卡片弥散阴影 + 字体层级 + Pill Badge"""
import fitz
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

BEFORE = r"F:\论文排版工具_测试包\_before_check.pdf"
AFTER = r"F:\论文排版工具_测试包\排版结果_毕业论文_人工智能技术在教育领域的应用与影响研究.pdf"
OUT_DIR = r"F:\论文排版工具_测试包\宣传素材"
os.makedirs(OUT_DIR, exist_ok=True)

# ---- 设计规范（用户 4 维度微调）----
BG = "#0F172A"          # 高级深蓝背景
CARD_DARK = "#1E272E"   # 排版前 卡片灰（带蓝调）
GREEN = "#00B894"       # 翡翠绿（排版后/亮点，替代荧光绿）
BLUE = "#0984E3"        # 电光蓝（强调/Word 高亮）
TEXT_MAIN = "#F1F5F9"   # 主文字
TEXT_SUB = "#94A3B8"    # 次级文字

CANVAS = (1080, 1440)   # 小红书 3:4
PAD = 48                # 两侧留白
RADIUS = 14             # 圆角


def font(size, bold=False):
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    p = os.path.join(r"C:\Windows\Fonts", name)
    return ImageFont.truetype(p, size)


def rrect(draw, box, radius, fill):
    """圆角矩形（PIL 9-slice 近似）"""
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def card_with_shadow(base, card_img, cx, cy, cw, ch, radius=RADIUS, shadow_alpha=70):
    """在 base 上画带弥散阴影的圆角卡片，卡片内容为 card_img（缩放铺满 cw x ch）"""
    # 阴影层：偏移 + 高斯模糊
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([cx + 6, cy + 12, cx + cw + 6, cy + ch + 12], radius=radius, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(shadow)
    # 圆角遮罩贴卡片
    mask = Image.new("L", (cw, ch), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, cw, ch], radius=radius, fill=255)
    resized = card_img.resize((cw, ch), Image.LANCZOS).convert("RGB")
    base.paste(resized, (cx, cy), mask)


def find_page(doc, keywords):
    for i in range(doc.page_count):
        t = doc[i].get_text()
        if all(k in t for k in keywords):
            return i
    return 0


def render_page(doc, idx, dpi=80):
    pix = doc[idx].get_pixmap(dpi=dpi)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def make_compare(name, kb, ka, title, desc):
    """对比页：3:4 深色画布 + 圆角卡片内嵌左右对比 + 顶部标签"""
    b = fitz.open(BEFORE)
    a = fitz.open(AFTER)
    ib = render_page(b, find_page(b, kb))
    ia = render_page(a, find_page(a, ka))
    # 左右拼接
    h = max(ib.height, ia.height)
    w = ib.width + ia.width + 4
    joined = Image.new("RGB", (w, h), "white")
    joined.paste(ib, (0, 0))
    joined.paste(ia, (ib.width + 4, 0))

    base = Image.new("RGBA", CANVAS, BG)
    # 顶部标题
    d = ImageDraw.Draw(base)
    d.text((PAD, 46), title, font=font(40, bold=True), fill=TEXT_MAIN)
    # 顶部标签：排版前 / 排版后（对称 Pill 结构，中间转化箭头）
    lw = int(d.textlength("排版前", font=font(26, bold=True))) + 36
    rrect(d, [PAD, 120, PAD + lw, 168], 24, "#1E272E")
    d.rounded_rectangle([PAD, 120, PAD + lw, 168], radius=24, outline="#3B4A5C", width=2)
    d.text((PAD + 18, 127), "排版前", font=font(26, bold=True), fill="#CBD5E1")
    # 转化箭头
    ax = PAD + lw + 24
    d.text((ax, 123), "一键排版 →", font=font(24), fill=GREEN)
    # 右侧标签
    rtxt = "排版后  v1.0.5"
    rw = int(d.textlength(rtxt, font=font(26, bold=True))) + 36
    rx = CANVAS[0] - PAD - rw
    rrect(d, [rx, 120, rx + rw, 168], 24, GREEN)
    d.text((rx + 18, 127), rtxt, font=font(26, bold=True), fill="#0F172A")
    # 分割微线
    d.line([PAD, 196, CANVAS[0] - PAD, 196], fill="#1E3A5F", width=2)
    # 卡片
    cw = CANVAS[0] - PAD * 2
    ch = int(cw * h / w * 1.06)
    max_ch = 1010
    if ch > max_ch:
        ch = max_ch
        cw = int(ch * w / h)
    cx = (CANVAS[0] - cw) // 2
    cy = 210
    card_with_shadow(base, joined, cx, cy, cw, ch)
    # 底部说明
    d = ImageDraw.Draw(base)
    d.text((PAD, 1330), desc, font=font(27), fill=TEXT_SUB)
    base.convert("RGB").save(os.path.join(OUT_DIR, name))
    print("生成:", name, "(前p%d 后p%d)" % (find_page(b, kb) + 1, find_page(a, ka) + 1))
    b.close(); a.close()


def make_cover():
    """封面：主标题加粗 + Word 高亮 + 副标题层级 + 底部 Pill Badge（卡片展示排版后成品）"""
    a = fitz.open(AFTER)
    ia = render_page(a, find_page(a, ["1.1 研究背景"]))
    joined = ia

    base = Image.new("RGBA", CANVAS, BG)
    d = ImageDraw.Draw(base)
    # 主标题（粗体，Word 高亮电光蓝）
    d.text((PAD, 70), "论文排版", font=font(64, bold=True), fill=TEXT_MAIN)
    d.text((PAD, 160), "还在被", font=font(64, bold=True), fill=TEXT_MAIN)
    d.text((PAD + 190, 160), "Word", font=font(64, bold=True), fill=BLUE)
    d.text((PAD + 420, 160), "折磨？", font=font(64, bold=True), fill=TEXT_MAIN)
    # 副标题（浅灰，与主标题区分）
    d.text((PAD, 262), "一键搞定格式规范", font=font(36), fill=TEXT_SUB)
    # 对比卡片（排版后成品展示）
    cw = CANVAS[0] - PAD * 2
    h = joined.height
    ch = int(cw * h / joined.width * 1.05)
    if ch > 700:
        ch = 700
        cw = int(ch * joined.width / h)
    cx = (CANVAS[0] - cw) // 2
    card_with_shadow(base, joined, cx, 340, cw, ch)
    # 底部 Pill Badge
    d = ImageDraw.Draw(base)
    badges = ["txt / md / docx → 规范 Word", "学校 / 期刊模板自动识别", "完全本地运行 · 免费"]
    y = 1240
    for txt in badges:
        w = int(d.textlength(txt, font=font(27))) + 36
        rrect(d, [PAD, y, PAD + w, y + 52], 26, "#1E3A5F")
        d.text((PAD + 18, y + 10), txt, font=font(27), fill=TEXT_MAIN)
        y += 66
    base.convert("RGB").save(os.path.join(OUT_DIR, "封面图.png"))
    print("生成: 封面图.png")
    a.close()


jobs = [
    ("对比_正文.png", ["第一章"], ["第一章"], "排版前后对比", "同一篇论文：乱格式 505 页 → 规范排版 54 页"),
    ("对比_英文摘要.png", ["A", "b", "s", "t", "r"], ["Abstract"], "英文摘要：逐字母乱排 → 规范排版", "标题黑体居中 · 正文 Times New Roman · 关键词规范"),
    ("对比_参考文献.png", ["[ 1 ]"], ["[1] 国务院"], "参考文献：对齐缩进全自动", "悬挂缩进 · 左对齐 · 下划线/加粗残留自动清理"),
    ("对比_摘要.png", ["摘", "要"], ["摘", "要"], "中文摘要：格式统一", "标题层级 · 正文字号行距 · 关键词标签统一"),
    ("对比_封面.png", ["本科毕业论文"], ["本科毕业论文"], "封面：字号排版规范", "超大字号自动降为模板字号 · 居中 · 填空下划线保留"),
]

for name, kb, ka, title, desc in jobs:
    make_compare(name, kb, ka, title, desc)

make_cover()
print("全部完成 →", OUT_DIR)
