# -*- coding: utf-8 -*-
"""决定性测试：bat 的 start 启动 v1.0.13 + 中文路径（用户重启的真实组合）"""
import os, shutil, subprocess, time, sys
sys.path.insert(0, '.')
import license.version as v

cn_dir = r'F:\论文排版工具_测试包\bat_cn_test'
shutil.rmtree(cn_dir, ignore_errors=True)
os.makedirs(cn_dir)
old = os.path.join(cn_dir, 'DocFormatTool.exe')   # v1.0.12（主程序）
new = os.path.join(cn_dir, 'DocFormatTool_new.exe')  # v1.0.13
shutil.copy2(r'dist\DocFormatTool.exe', old)
shutil.copy2(r'releases\DocFormatTool.exe', new)

# 1) 启动主程序（中文路径）
p = subprocess.Popen([old], cwd=cn_dir)
print('主程序（中文路径）启动 PID:', p.pid)
time.sleep(12)
if p.poll() is not None:
    print('主程序启动失败!', p.poll()); sys.exit(1)
print('主程序运行中 ✓')

# 2) bat（在中文路径执行）
bat = v.build_updater_bat(old, new)
bat_path = os.path.join(cn_dir, 'update.bat')
open(bat_path, 'w', encoding='gbk', newline='').write(bat)
print('执行 update.bat（中文路径 start v1.0.13）...')
os.startfile(bat_path)

time.sleep(16)
out = subprocess.check_output('tasklist /fi "imagename eq DocFormatTool.exe" /fo csv', shell=True).decode('gbk', errors='ignore')
running = 'DocFormatTool' in out
print('重启后进程运行中:', running)
if not running:
    print('→ 复现！bat start + 中文路径 = LoadLibrary 失败')

os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
time.sleep(1)
shutil.rmtree(cn_dir, ignore_errors=True)
print('清理完成')
