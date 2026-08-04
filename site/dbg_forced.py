# -*- coding: utf-8 -*-
"""调试：打印每个段落的 para_idx/forced_type/分类结果"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ['DFT_DEBUG'] = '1'
# 在 _reformat_paragraph 注入 debug 打印（读环境变量）
import engine.build_docx as B
import inspect

src_code = open(r'engine\build_docx.py', encoding='utf-8').read()
marker = '    # 用户确认覆盖（最高优先级）：低置信段落的角色由用户指定'
dbg = '''    import os as _os
    if _os.environ.get('DFT_DEBUG'):
        print('DBG idx_para=%r forced=%r text=%r' % (_os.environ.get('DFT_IDX','?'), forced_type, para_text(p_el).strip()[:16]))
'''
if marker not in src_code:
    print('marker 未找到')
    sys.exit(1)
if 'DFT_DEBUG' not in src_code:
    src_code = src_code.replace(marker, marker + '\n' + dbg)
    open(r'engine\build_docx.py', 'w', encoding='utf-8', newline='').write(src_code)
    print('已注入 debug')
    # 重新加载
    import importlib
    importlib.reload(B)
else:
    print('debug 已存在')

# 跑 T9，模拟 forced_map，但要同步 para_idx——直接内联调用
from docx import Document
from docx.shared import Pt
from engine.config import load_preset
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
OUT = r'F:\论文排版工具_测试包\测试套件'
src = os.path.join(OUT, 'T9_低置信_排版前.docx')
B.reformat_existing(load_preset('bachelor_cn'), src, os.path.join(OUT, '_dbg_out.docx'),
                    {"2": "body", "4": "heading2"})
