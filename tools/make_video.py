# -*- coding: utf-8 -*-
"""合成 30 秒竖屏宣传片：8 张卡片 + 淡入淡出 → mp4。"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "video")
CARD_DIR = os.path.join(OUT_DIR, "cards")

from moviepy import ImageClip, concatenate_videoclips
from moviepy.video.fx import FadeIn, FadeOut

cards = sorted(f for f in os.listdir(CARD_DIR) if f.endswith(".png"))
clips = []
for c in cards:
    clip = (ImageClip(os.path.join(CARD_DIR, c))
            .with_duration(3.5)
            .with_effects([FadeIn(0.4), FadeOut(0.4)]))
    clips.append(clip)

video = concatenate_videoclips(clips, method="chain")
out = os.path.join(OUT_DIR, "宣传片_30s.mp4")
video.write_videofile(out, fps=24, codec="libx264", audio=False,
                      preset="medium", logger=None)
print("视频已生成:", out)
print("时长: %.1f 秒" % video.duration)
