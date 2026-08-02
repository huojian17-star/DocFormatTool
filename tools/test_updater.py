# -*- coding: utf-8 -*-
"""本地实机测试 updater：模拟旧版+下载的新版 → 跑 update.bat → 验证替换/清理/启动。"""
import os
import shutil
import subprocess
import tempfile
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(BASE, "dist", "DocFormatTool.exe")

# 模拟目录（含空格路径，复现真实环境）
sim = os.path.join(tempfile.gettempdir(), "DocFormatTool Update Test")
if os.path.exists(sim):
    shutil.rmtree(sim)
os.makedirs(sim)

old_exe = os.path.join(sim, "DocFormatTool.exe")
new_exe = os.path.join(sim, "DocFormatTool_new.exe")
shutil.copy2(EXE, old_exe)
shutil.copy2(EXE, new_exe)
print("模拟环境:", sim)
print("旧版存在:", os.path.exists(old_exe), "| 新版存在:", os.path.exists(new_exe))

# 与程序完全一致的 bat 生成逻辑
bat = os.path.join(sim, "update.bat")
with open(bat, "w", encoding="gbk") as f:
    f.write('@echo off\r\n'
            'timeout /t 1 /nobreak >nul\r\n'
            'taskkill /f /im DocFormatTool.exe >nul 2>&1\r\n'
            'copy /y "%s" "%s" >nul\r\n'
            'del "%s"\r\n'
            'start "" "%s"\r\n'
            'del "%%~f0"\r\n' % (new_exe, old_exe, new_exe, old_exe))

# 用 os.startfile 方式启动（模拟程序逻辑）
os.startfile(bat)
print("update.bat 已启动（startfile）")

# 等待执行
time.sleep(6)
print("\n--- 验证结果 ---")
print("old 被 new 覆盖:", os.path.exists(old_exe))
print("new 已删除:", not os.path.exists(new_exe))
print("bat 已自删:", not os.path.exists(bat))
# 新版应已启动（start "" 打开了 exe）
time.sleep(2)
procs = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process DocFormatTool -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"],
                       capture_output=True, text=True).stdout.strip()
print("DocFormatTool 进程数:", procs)
# 清理
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name DocFormatTool -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
shutil.rmtree(sim, ignore_errors=True)
print("模拟环境已清理")
