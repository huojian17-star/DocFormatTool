# -*- coding: utf-8 -*-
"""完整版宣传片：真实 GUI 截图镜头 + 文字卡片 + 合成背景音乐 → mp4。"""
import ctypes
import ctypes.wintypes
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageGrab

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "video")
CARD_DIR = os.path.join(OUT_DIR, "cards")
os.makedirs(CARD_DIR, exist_ok=True)
W, H = 1080, 1920
FONT_BIG = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MID = r"C:\Windows\Fonts\msyh.ttc"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype(r"C:\Windows\Fonts\simhei.ttf", size)


# ---------- 1. 截真实 GUI ----------
def grab_gui():
    exe = os.path.join(BASE, "dist", "DocFormatTool.exe")
    p = subprocess.Popen([exe])
    time.sleep(12)
    user32 = ctypes.windll.user32
    rects = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    def cb(h, l):
        if user32.IsWindowVisible(h):
            n = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(h, n, 256)
            if "规范文档" in n.value:
                r = ctypes.wintypes.RECT()
                user32.GetWindowRect(h, ctypes.byref(r))
                rects.append((r.left, r.top, r.right, r.bottom))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    p.terminate()
    if not rects:
        return None
    l, t, r, b = rects[0]
    img = ImageGrab.grab(bbox=(l, t, r, b))
    img = img.resize((int(img.width * 1.0), int(img.height * 1.0)))
    # 放到 1080x1920 卡片中（上方标题，中间截图）
    card = Image.new("RGB", (W, H), (12, 16, 24))
    d = ImageDraw.Draw(card)
    d.text(((W - d.textlength("真实效果演示", font=_font(FONT_BIG, 72))) // 2, 260),
           "真实效果演示", font=_font(FONT_BIG, 72), fill=(255, 190, 60))
    # 截图缩放到卡片宽度 80%
    gw = int(W * 0.82)
    gh = int(img.height * gw / img.width)
    img2 = img.resize((gw, gh))
    card.paste(img2, ((W - gw) // 2, 420))
    d.rectangle([0, 0, W, 14], fill=(255, 190, 60))
    card.save(os.path.join(CARD_DIR, "c_gui.png"))
    print("GUI 截图已合成卡片")


# ---------- 2. 文字卡片 ----------
def _card(filename, lines, bg=(12, 16, 24), fg=(245, 245, 245), accent=(255, 190, 60),
          size_big=88, size_mid=52, gap=36):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=accent)
    total = 0
    for text, kind in lines:
        total += size_big if kind in ("big", "accent") else size_mid
        total += gap
    total -= gap
    y = H // 2 - total // 2
    for text, kind in lines:
        if kind == "big":
            f, c = _font(FONT_BIG, size_big), fg
        elif kind == "accent":
            f, c = _font(FONT_BIG, size_big), accent
        else:
            f, c = _font(FONT_MID, size_mid), (200, 205, 215)
        if text:
            w = d.textlength(text, font=f)
            d.text(((W - w) // 2, y), text, font=f, fill=c)
        y += size_big if kind in ("big", "accent") else size_mid
        y += gap
    img.save(os.path.join(CARD_DIR, filename))


# ---------- 3. 合成背景音乐（30s 电子节拍）----------
def make_music(path, dur=31.0, sr=44100):
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    mix = np.zeros_like(t)
    bpm = 112
    step = 60.0 / bpm
    # 四拍：kick 每拍，hihat 半拍，bass 脉动
    for start in np.arange(0, dur, step):
        i0 = int(start * sr)
        seg = min(int(0.18 * sr), len(t) - i0)
        if seg <= 0:
            continue
        tt = t[i0:i0 + seg] - start
        mix[i0:i0 + seg] += np.exp(-25 * tt) * np.sin(2 * np.pi * 52 * tt) * 0.9
        i1 = int((start + step / 2) * sr)
        seg2 = min(int(0.05 * sr), len(t) - i1)
        if seg2 > 0:
            mix[i1:i1 + seg2] += np.random.uniform(-1, 1, seg2) * np.exp(-60 * np.linspace(0, 1, seg2)) * 0.25
    # 低音脉动
    bass = 0.12 * np.sin(2 * np.pi * 110 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * (bpm / 60 / 4) * t))
    mix += bass
    # 渐入渐出 + 归一
    fade = int(0.5 * sr)
    mix[:fade] *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(mix)) or 1
    mix = mix / peak * 0.6
    import wave
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("背景音乐已生成:", path)


# ---------- 4. 合成 ----------
def build_video():
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    from moviepy.video.fx import FadeIn, FadeOut

    cards = ["c1.png", "c2.png", "c_gui.png", "c4.png", "c5.png", "c6.png", "c7.png", "c8.png"]
    clips = []
    for i, c in enumerate(cards):
        dur = 3.6 if c != "c_gui.png" else 4.0
        clip = (ImageClip(os.path.join(CARD_DIR, c))
                .with_duration(dur)
                .with_effects([FadeIn(0.35), FadeOut(0.35)]))
        clips.append(clip)
    video = concatenate_videoclips(clips, method="chain")
    music = os.path.join(OUT_DIR, "bgm.wav")
    if os.path.exists(music):
        audio = AudioFileClip(music)
        video = video.with_audio(audio.subclipped(0, video.duration))
    out = os.path.join(OUT_DIR, "宣传片_完整版.mp4")
    video.write_videofile(out, fps=24, codec="libx264", audio_codec="aac",
                          preset="medium", logger=None)
    print("完整版视频已生成:", out)
    print("时长: %.1f 秒" % video.duration)


if __name__ == "__main__":
    _card("c1.png", [("论文格式", "big"), ("改吐了？", "accent")])
    _card("c2.png", [("字体乱、行距错", "big"), ("页码对不上", "big"),
                     ("表格里字五花八门", "mid"), ("改格式比写正文还累", "accent")], bg=(24, 20, 18))
    _card("c4.png", [("图片表格", "big"), ("原样保留", "accent"),
                     ("只动格式", "mid"), ("不改你一个字", "accent")], bg=(16, 28, 22))
    _card("c5.png", [("Markdown 也能排", "big"), ("", "mid"),
                     ("表格 · 代码块 · LaTeX 公式", "mid"), ("工科生友好", "accent")], bg=(24, 20, 32))
    _card("c6.png", [("排完自动质检", "big"), ("", "mid"),
                     ("生成《改动报告》", "accent"), ("改了啥、覆盖率多少", "mid"), ("一目了然", "big")])
    _card("c7.png", [("论文不离开你的电脑", "big"), ("断网也能用", "accent"),
                     ("不上传、不采集", "mid")], bg=(16, 24, 24))
    _card("c8.png", [("开源在 GitHub", "big"), ("", "mid"),
                     ("免费测试中", "accent"), ("私信我，一人一个码", "mid")], bg=(12, 12, 20))
    grab_gui()
    make_music(os.path.join(OUT_DIR, "bgm.wav"))
    build_video()
