# -*- coding: utf-8 -*-
"""从吉祥物截图中抠出角色（去白底→透明 PNG）"""
from PIL import Image
import sys, os

SRC = r'C:\Users\28253\AppData\Roaming\reasonix\global-workspace\.reasonix\attachments\clipboard-20260805-191711.022420-000032.png'
OUT = r'site\mascot_raw.png'

img = Image.open(SRC).convert('RGBA')
w, h = img.size
print('原图:', w, h)

# 1) 找角色边界（非纯白像素的 bbox）
px = img.load()
min_x, min_y, max_x, max_y = w, h, 0, 0
for y in range(0, h, 1):
    for x in range(0, w, 1):
        r, g, b, a = px[x, y]
        if a > 10 and (r < 245 or g < 245 or b < 245):
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
print('角色 bbox:', min_x, min_y, max_x, max_y)
pad = 2
min_x, min_y = max(0, min_x-pad), max(0, min_y-pad)
max_x, max_y = min(w-1, max_x+pad), min(h-1, max_y+pad)
img = img.crop((min_x, min_y, max_x+1, max_y+1))
w, h = img.size

# 2) 去白底：flood fill 从四角扩散背景连通域 → 透明
px = img.load()
visited = [[False]*h for _ in range(w)]
stack = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
from collections import deque
dq = deque()
for sx, sy in stack:
    if not visited[sx][sy] and px[sx, sy][0] >= 245 and px[sx, sy][1] >= 245 and px[sx, sy][2] >= 245 and px[sx, sy][3] > 10:
        dq.append((sx, sy)); visited[sx][sy] = True
while dq:
    x, y = dq.popleft()
    px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
            visited[nx][ny] = True
            r, g, b, a = px[nx, ny]
            if a > 10 and r >= 245 and g >= 245 and b >= 245:
                dq.append((nx, ny))

img.save(OUT)
print('已保存:', OUT, img.size)
