# -*- coding: utf-8 -*-
"""OpenXML 显示层检查：输出 docx 的自定义样式定义（qFormat/outlineLvl/字体）+ 段落 outlineLvl"""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import infer, build_docx, config
from docx import Document
from docx.oxml.ns import qn

CFG = config.load_preset('bachelor_cn')
CONTENT = """城乡融合发展中的要素流动与资源配置优化研究
张三 李四
摘要：城乡融合发展是新时代中国式现代化的重要路径，本文从要素流动与资源配置的角度展开分析。
关键词：城乡融合；要素流动；资源配置
一、引言
城乡融合发展涉及人口、土地、资本等多维要素的自由流动。
（一）要素流动理论
要素流动是区域协调发展的核心机制。
参考文献
[1] 张伟. 城乡融合研究[J]. 经济研究, 2024.
"""
TMP = os.path.join(tempfile.gettempdir(), 'display_check')
os.makedirs(TMP, exist_ok=True)
txt = os.path.join(TMP, 'd.txt')
open(txt, 'w', encoding='utf-8').write(CONTENT)
out = os.path.join(TMP, 'd_out.docx')
structs = infer.parse_file(txt)
infer._mark_cover(structs)
build_docx.build(CFG, structs, out)

d = Document(out)
print('=== 样式定义检查 ===')
for name in ['摘要', '摘要正文', '关键词', '论文题目']:
    try:
        st = d.styles[name]
        xml = st.element.xml
        has_q = 'qFormat' in xml
        has_ol = 'outlineLvl' in xml
        ol_val = ''
        import re
        m = re.search(r'w:outlineLvl w:val="(\d+)"', xml)
        if m: ol_val = m.group(1)
        has_font = 'eastAsia' in xml
        print('  %-6s qFormat=%s outlineLvl=%s(%s) eastAsia=%s' % (name, has_q, has_ol, ol_val, has_font))
    except KeyError:
        print('  %-6s 样式不存在!' % name)

print('=== 段落 outlineLvl（导航）检查 ===')
for p in d.paragraphs[:12]:
    t = p.text.strip()
    if not t: continue
    pPr = p._p.find(qn('w:pPr'))
    ol = ''
    if pPr is not None:
        el = pPr.find(qn('w:outlineLvl'))
        if el is not None: ol = el.get(qn('w:val'))
    print('  [%s] outlineLvl=%s  %s' % (p.style.name, ol or '-', t[:22]))
