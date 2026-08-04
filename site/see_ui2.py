# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'thesis-format-tool\tools')
import importlib.util
spec = importlib.util.spec_from_file_location('srv', r'thesis-format-tool\tools\mcp_vision_server.py')
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)
r = srv._call_minimax(
    r'thesis-format-tool\gui_confirm.png',
    '这是"请确认以下段落格式"弹窗截图。请描述：1)顶部说明文字是否清晰易懂 2)表格表头（段落内容/程序认为/请选择）是否显示 3)每行的段落文本是否完整可见 4)"程序认为"列的猜测文字是否显示 5)下拉框选项是否可读。',
    'high')
print(r[:700])
