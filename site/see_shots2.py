# -*- coding: utf-8 -*-
"""视觉看用户新截图（颜色/加粗/目录问题）。"""
import sys, importlib.util

sys.path.insert(0, r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools")
spec = importlib.util.spec_from_file_location(
    "srv", r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools\mcp_vision_server.py")
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)

BASE = r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\.reasonix\attachments"
imgs = [
    "clipboard-20260804-015224.017413-000005.png",
    "clipboard-20260804-015225.445895-000006.png",
]
for i, im in enumerate(imgs, 1):
    p = BASE + "\\" + im
    print("=" * 15, "图%d" % i, "=" * 15)
    if i == 2:
        q = ("论文页面截图。请具体指出：1)文字是否有彩色（哪些地方什么颜色）"
             "2)是否有部分文字加粗而部分不加粗 3)如果是目录页，目录有什么问题（层级/格式/页码/对齐）"
             "4)其他排版问题。逐条简短回答。")
    else:
        q = ("论文页面截图。请具体指出：1)文字是否有彩色（哪些文字什么颜色）"
             "2)是否有部分文字加粗而部分不加粗（指出位置）3)其他排版问题。")
    r = srv._call_minimax(p, q, "high")
    print(r[:900])
