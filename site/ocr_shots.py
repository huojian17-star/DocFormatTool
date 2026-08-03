# -*- coding: utf-8 -*-
"""OCR 用户发来的 4 张排版效果截图，输出页面内容区（跳过工具栏）。"""
import subprocess, sys, os

BASE = r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace"
imgs = [
    "clipboard-20260804-010545.429474-000023.png",
    "clipboard-20260804-010546.965398-000024.png",
    "clipboard-20260804-010655.674961-000025.png",
    "clipboard-20260804-010657.872737-000026.png",
]
for im in imgs:
    p = os.path.join(BASE, ".reasonix", "attachments", im)
    print("=" * 20, im, "=" * 20)
    out = subprocess.run(
        [sys.executable, "-X", "utf8", os.path.join(BASE, "tools", "ocr.py"), p],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("["):
            continue
        try:
            # 格式 [x,y wxh] text —— 取 y 坐标判断是否页面内容区（>200）
            coord = line[1:line.index("]")]
            x, y = coord.split(",")[0], coord.split(",")[1].split()[0]
            if int(y) > 210:
                print(line)
        except Exception:
            continue
