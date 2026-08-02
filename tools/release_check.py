# -*- coding: utf-8 -*-
"""发布前检查：确认 VERSION 与 version.json 一致，避免版本号错位（历史事故：打包后忘改版本号）。

用法：python tools/release_check.py
不通过则打印原因并退出码 1（阻止继续打包）。
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 读取 exe 内置 VERSION
sys.path.insert(0, BASE)
from license import version as V

# 读取 version.json（若存在）
vj_path = os.path.join(BASE, "version.json")
vj_version = None
if os.path.exists(vj_path):
    try:
        with open(vj_path, encoding="utf-8") as f:
            vj_version = json.load(f).get("version")
    except Exception:
        pass

print("exe 内置 VERSION :", V.VERSION)
print("version.json     :", vj_version)

ok = True
if vj_version and V.VERSION != vj_version:
    print("✗ 不一致：exe 是 %s，version.json 是 %s —— 学生更新后版本号会对不上！" % (V.VERSION, vj_version))
    ok = False
if not vj_version:
    print("⚠ version.json 不存在（无自动更新场景可忽略；有则必须同步）")

print("✓ 版本号一致，可以打包" if ok else "✗ 请先统一版本号再打包")
sys.exit(0 if ok else 1)
