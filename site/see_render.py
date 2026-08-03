# -*- coding: utf-8 -*-
"""视觉看新版渲染的摘要页 + 目录页。"""
import sys, importlib.util

sys.path.insert(0, r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools")
spec = importlib.util.spec_from_file_location(
    "srv", r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools\mcp_vision_server.py")
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)

BASE = r"F:\论文排版工具_测试包"
for i in (3, 4, 5):
    p = BASE + r"\_page%d.png" % i
    q = ("论文排版页面截图。请检查：1)文字是否全部黑色（有没有残留彩色）"
         "2)正文/目录文字加粗是否统一（有没有该粗不粗/该不粗却粗）"
         "3)如果是目录页，目录条目格式是否整齐 4)其他问题。简短回答。")
    print("=" * 12, "第%d页" % i, "=" * 12)
    r = srv._call_minimax(p, q, "high")
    print(r[:600])
