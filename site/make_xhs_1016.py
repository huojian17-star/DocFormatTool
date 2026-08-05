# -*- coding: utf-8 -*-
"""v1.0.16 小红书宣传图：3:4 画布 + 深蓝底 + 圆角卡片 + 吉祥物 + 新界面截图"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = r'site\xhs_out'
os.makedirs(OUT, exist_ok=True)

BG = "#0F172A"
CARD_DARK = "#1E272E"
GREEN = "#00B894"
BLUE = "#0984E3"
ORANGE = "#F5A623"
TEXT_MAIN = "#F1F5F9"
TEXT_SUB = "#94A3B8"
ACCENT = "#60A5FA"  # 新界面品牌蓝

CANVAS = (1080, 1440)
PAD = 48
RADIUS = 16


def font(size, bold=False):
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", name), size)


def rrect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def card_with_shadow(base, card_img, cx, cy, cw, ch, radius=RADIUS, shadow_alpha=70):
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([cx + 6, cy + 12, cx + cw + 6, cy + ch + 12], radius=radius, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(shadow)
    mask = Image.new("L", (cw, ch), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, cw, ch], radius=radius, fill=255)
    resized = card_img.resize((cw, ch), Image.LANCZOS).convert("RGB")
    base.paste(resized, (cx, cy), mask)
    # 细边框（精致感）
    outline = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(outline)
    od.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=radius, outline=(255, 255, 255, 70), width=2)
    base.alpha_composite(outline)


def text_center(draw, y, s, f, fill, cx=CANVAS[0] // 2):
    w = draw.textlength(s, font=f)
    draw.text((cx - w / 2, y), s, font=f, fill=fill)


def badge(draw, x, y, s, bg, fg, size=34):
    f = font(size, True)
    w = draw.textlength(s, font=f)
    rrect(draw, [x, y, x + w + 28, y + size + 18], 14, bg)
    draw.text((x + 14, y + 8), s, font=f, fill=fg)


def shot_card(path, width, crop_box=None):
    """读截图 → 可选裁切 → resize 到指定宽度（保持比例），返回 (img, 高度)。"""
    img = Image.open(path)
    if crop_box:
        img = img.crop(crop_box)
    img = img.convert('RGB')
    h = int(img.height * width / img.width)
    return img.resize((width, h), Image.LANCZOS), h


def new_base():
    img = Image.new("RGBA", CANVAS, BG)
    return img, ImageDraw.Draw(img)


# ============ 图1 封面 ============
img, d = new_base()
# 吉祥物（主标题右侧，缩小不拥挤）
mascot = Image.open(r'site\mascot_raw.png').convert('RGBA')
mw, mh = 200, 174
mascot_s = mascot.resize((mw, mh), Image.LANCZOS)
img.paste(mascot_s, (CANVAS[0] - mw - 16, 70), mascot_s)
# 顶部标签
badge(d, PAD, 70, "v1.0.16 大更新", GREEN, "#0F172A")
# 主标题
text_center(d, 150, "论文排版工具", font(78, True), TEXT_MAIN)
# 副标题（左对齐，避开右侧吉祥物）
d.text((210, 255), "全新 v1.0.16｜界面 交互 吉祥物 全面焕新", font=font(36, True), fill=ACCENT)
# 副标题
# （去重：主标题下方已有更新信息，此处不再重复）
# 新界面截图（卡片）——用户手截干净原图（裁窗口区域 + 自适应缩放）
shot, sh = shot_card(r'site\xhs_src\top.png', 800, (0, 0, 2460, 1529))
card_with_shadow(img, shot, (CANVAS[0] - 800) // 2, 430, 800, sh)
# 底部卖点标签
badge(d, PAD, 1040, "全新界面", BLUE, "#FFFFFF")
badge(d, PAD + 220, 1040, "拖拽选文件", BLUE, "#FFFFFF")
badge(d, PAD + 470, 1040, "滚轮滚动", BLUE, "#FFFFFF")
badge(d, 150, 1110, "专属吉祥物", BLUE, "#FFFFFF")
badge(d, 380, 1110, "窗口可最大化", BLUE, "#FFFFFF")
text_center(d, 1230, "完全本地运行 · 论文不离开你的电脑", font(32), TEXT_SUB)
text_center(d, 1310, "免费 · 免安装 · 开箱即用", font(32, True), GREEN)
img.convert('RGB').save(os.path.join(OUT, 'xhs_1_cover.png'))
print('图1 封面 OK')

# ============ 图2 卖点页 ============
img, d = new_base()
text_center(d, 90, "这次更新了什么？", font(72, True), TEXT_MAIN)
features = [
    ("全新界面", "AiNiee 风格：侧边栏导航 + 卡片化布局 + 莫兰迪配色", "#60A5FA"),
    ("拖拽选文件", "把论文直接拖进窗口，自动填路径，不用再点来点去", "#34D399"),
    ("鼠标滚轮滚动", "高级选项再多内容也能滚着看，一键排版永远钉在底部", "#FBBF24"),
    ("专属吉祥物", "排排陪你写论文，侧边栏常驻，萌到想多写两页", "#A78BFA"),
    ("更新链路加固", "自动更新更稳，旧版一键升级到新界面", "#F472B6"),
]
y = 250
for title, desc, color in features:
    # 卡片
    card_y = y
    rrect(d, [PAD, card_y, CANVAS[0] - PAD, card_y + 200], RADIUS, CARD_DARK)
    # 左侧强调色条（代替 emoji——PIL 雅黑不渲染彩色 emoji）
    rrect(d, [PAD + 18, card_y + 55, PAD + 22, card_y + 155], 3, color)
    d.text((PAD + 50, card_y + 62), title, font=font(42, True), fill=TEXT_MAIN)
    d.text((PAD + 50, card_y + 130), desc, font=font(30), fill=TEXT_SUB)
    y += 224
# 底部 CTA 胶囊
cta = "免费下载：搜「规范文档一键排版工具」"
cf = font(34, True)
cw = d.textlength(cta, font=cf)
rrect(d, [CANVAS[0] // 2 - cw // 2 - 40, 1318, CANVAS[0] // 2 + cw // 2 + 40, 1378], 30, GREEN)
text_center(d, 1330, cta, cf, "#0F172A")
text_center(d, 1400, "v1.0.16 · 2026-08 更新", font(26), TEXT_SUB)
img.convert('RGB').save(os.path.join(OUT, 'xhs_2_features.png'))
print('图2 卖点 OK')

# ============ 图3 界面展示 ============
img, d = new_base()
text_center(d, 70, "新界面长这样", font(64, True), TEXT_MAIN)
text_center(d, 150, "左边有排排，右边是功能卡片", font(34), TEXT_SUB)
shot_top, sh_top = shot_card(r'site\xhs_src\top.png', 700, (0, 0, 2460, 1529))
card_with_shadow(img, shot_top, (CANVAS[0] - 700) // 2, 200, 700, sh_top)
text_center(d, 660, "拖拽文件到窗口任意位置 → 自动填路径", font(32, True), ACCENT)
shot_pt, sh_pt = shot_card(r'site\xhs_src\pt.png', 850, (0, 0, 2303, 819))
card_with_shadow(img, shot_pt, (CANVAS[0] - 850) // 2, 720, 850, sh_pt)
text_center(d, 1060, "「可拖拽」提示 + 拖拽时输入框变蓝", font(32, True), GREEN)
text_center(d, 1140, "一键排版固定在底部，随时可点", font(30), TEXT_SUB)
img.convert('RGB').save(os.path.join(OUT, 'xhs_3_ui.png'))
print('图3 界面 OK')

# ============ 图4 价值/下载 ============
img, d = new_base()
text_center(d, 80, "这工具到底解决什么？", font(64, True), TEXT_MAIN)
# 核心价值卡
rrect(d, [PAD, 170, CANVAS[0] - PAD, 420], RADIUS, CARD_DARK)
d.text((PAD + 40, 210), "任意格式 → 规范 Word", font=font(50, True), fill=TEXT_MAIN)
d.text((PAD + 40, 300), "txt / md / docx 都能排", font=font(36), fill=TEXT_SUB)
d.text((PAD + 40, 350), "标题层级自动识别 · 摘要关键词参考文献自动处理", font=font(32), fill=ACCENT)
# 下载方式
rrect(d, [PAD, 470, CANVAS[0] - PAD, 720], RADIUS, CARD_DARK)
d.text((PAD + 40, 510), "怎么拿到？", font=font(44, True), fill=TEXT_MAIN)
d.text((PAD + 40, 590), "① 老用户：打开软件 → 自动更新到 v1.0.16", font=font(34), fill=TEXT_SUB)
d.text((PAD + 40, 650), "② 新用户：小红书/蓝奏云下载，免安装开箱即用", font=font(34), fill=TEXT_SUB)
# 吉祥物大图
mascot2 = Image.open(r'site\mascot_raw.png').convert('RGBA')
mw2, mh2 = 380, 330
m2 = mascot2.resize((mw2, mh2), Image.LANCZOS)
img.paste(m2, (CANVAS[0] // 2 - mw2 // 2, 780), m2)
text_center(d, 1150, "排排说：论文排版不焦虑", font(40, True), ACCENT)
text_center(d, 1240, "完全本地运行 · 免费 · 不修改你的内容", font(32), TEXT_SUB)
badge(d, CANVAS[0] // 2 - 150, 1330, "点个关注不迷路", GREEN, "#0F172A")
img.convert('RGB').save(os.path.join(OUT, 'xhs_4_value.png'))
print('图4 价值 OK')
print('全部完成 →', OUT)
