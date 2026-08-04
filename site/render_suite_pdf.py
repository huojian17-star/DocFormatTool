# -*- coding: utf-8 -*-
"""六场景测试文档 → PDF 渲染，供视觉模型检查实际排版效果"""
import os, sys, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SRC_DIR = r'F:\论文排版工具_测试包\测试套件'
import subprocess

files = [f for f in os.listdir(SRC_DIR) if f.endswith('.docx')]
print('待转 PDF:', files)

for f in sorted(files):
    src = os.path.join(SRC_DIR, f)
    out = os.path.join(SRC_DIR, f.replace('.docx', '.pdf'))
    if os.path.exists(out):
        print('跳过(已存在):', f)
        continue
    r = subprocess.run([sys.executable, '-X', 'utf8',
                        os.path.join(os.path.dirname(__file__), 'render_any.py'),
                        src, out],
                       capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=120)
    print(f, '→', 'OK' if r.returncode == 0 else ('FAIL: ' + (r.stdout or r.stderr)[-80:]))
