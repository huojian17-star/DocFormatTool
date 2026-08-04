# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'thesis-format-tool\tools')
import importlib.util
spec = importlib.util.spec_from_file_location('srv', r'thesis-format-tool\tools\mcp_vision_server.py')
srv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(srv)
r = srv._call_minimax(
    r'.reasonix\attachments\clipboard-20260805-001325.412922-000014.png',
    '这是论文排版工具窗口截图。请详细描述：1)窗口整体布局 2)是否能看到"使用内置通用模板"选项及其下面的模板选择控件（下拉框/列表/单选按钮/Combobox）3)窗口下部按钮（一键排版等）是否可见 4)有无控件缺失、错位、重叠。',
    'high')
print(r[:700])
