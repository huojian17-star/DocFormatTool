# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'thesis-format-tool\tools')
import importlib.util
spec = importlib.util.spec_from_file_location('srv', r'thesis-format-tool\tools\mcp_vision_server.py')
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)
r = srv._call_minimax(
    r'.reasonix\attachments\clipboard-20260805-004149.032808-000017.png',
    '这是 WPS 打开的排版结果文档截图。请描述正文区域（标题栏下方）：1)正文内容是什么（列举几行）2)格式是否正常（段落、缩进、标题层级）3)有没有明显问题：内容错乱、每行都变段落、标题丢失、字号异常、空行爆炸等。请具体描述你看到的正文样子。',
    'high')
print(r[:900])
