# -*- coding: utf-8 -*-
"""version.json note 加蓝奏云手动下载指引 + UPDATE_URLS raw 优先"""
import json

# 1. note 加手动下载指引（旧版本"发现新版本"弹窗直接显示）
v = json.load(open('version.json', encoding='utf-8'))
v['note'] = ('自动更新增强：下载进度窗口+60秒超时兜底。若自动下载卡住/失败，请手动下载：'
             '蓝奏云 https://wwavh.lanzoul.com/iu1i640hnz6b （提取码 8u6z），'
             '或 GitHub Releases 页面下载最新 exe 覆盖即可。')
open('version.json', 'w', encoding='utf-8', newline='').write(json.dumps(v, ensure_ascii=False, indent=2))
print('note 已更新')

# 2. version.py UPDATE_URLS raw 优先（无缓存，旧版本用户拿最新数据）
p = r'license\version.py'
s = open(p, encoding='utf-8').read()
old = '''UPDATE_URLS = [
    "https://cdn.jsdelivr.net/gh/huojian17-star/DocFormatTool@master/version.json",
    "https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json",
]'''
new = '''# raw 无缓存保证拿到最新 version.json（jsdelivr 对 master 分支缓存 ~12h，
# 若 jsdelivr 在前，缓存旧数据会让用户看不到最新 note/下载地址）。jsdelivr 作兜底。
UPDATE_URLS = [
    "https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json",
    "https://cdn.jsdelivr.net/gh/huojian17-star/DocFormatTool@master/version.json",
]'''
assert old in s, 'version.py 未找到 UPDATE_URLS'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('UPDATE_URLS 已改为 raw 优先')
