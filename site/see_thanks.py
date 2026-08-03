# -*- coding: utf-8 -*-
"""视觉看致谢层级问题截图。"""
import sys, importlib.util

sys.path.insert(0, r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools")
spec = importlib.util.spec_from_file_location(
    "srv", r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\thesis-format-tool\tools\mcp_vision_server.py")
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)

p = r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\.reasonix\attachments\clipboard-20260804-021942.567004-000009.png"
q = ("这是什么软件的什么界面？左侧导航区显示什么层级？请描述：1)整体界面 2)左侧树状结构/导航的层级关系 "
     "3)'致谢'出现在哪一层级 4)和'目录'是什么关系（同级还是子级）")
r = srv._call_minimax(p, q, "high")
print(r[:700])
