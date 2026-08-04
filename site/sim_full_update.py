# -*- coding: utf-8 -*-
"""完整模拟用户更新：主程序 v1.0.12 运行中（隔离目录副本）→ bat 强杀 → 替换 → 启动 v1.0.13"""
import sys, os, shutil, subprocess, time, hashlib
sys.path.insert(0, '.')
import license.version as v

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1048576), b''):
            h.update(c)
    return h.hexdigest()

# 隔离目录：主程序 = v1.0.12 副本，新版 = v1.0.13
tdir = os.path.join(os.environ['TEMP'], 'update_sim')
shutil.rmtree(tdir, ignore_errors=True)
os.makedirs(tdir)
old = os.path.join(tdir, 'DocFormatTool.exe')   # 主程序（v1.0.12）
new = os.path.join(tdir, 'DocFormatTool_new.exe')  # 新版（v1.0.13）
shutil.copy2(r'dist\DocFormatTool.exe', old)
shutil.copy2(r'releases\DocFormatTool.exe', new)
print('主程序 exe:', old, 'md5:', md5(old)[:10], '(v1.0.12)')
print('新版 exe:', new, 'md5:', md5(new)[:10], '(v1.0.13)')

# 1) 启动主程序（真实 GUI 运行中）
p = subprocess.Popen([old], cwd=tdir)
print('主程序启动，PID:', p.pid)
time.sleep(12)
if p.poll() is not None:
    print('主程序启动失败! 退出码', p.poll())
    sys.exit(1)
print('主程序运行中 ✓')

# 2) 生成 bat 并执行（强杀主程序 → copy → _MEI 清理 → start 新版）
bat = v.build_updater_bat(old, new)
bat_path = os.path.join(tdir, 'update.bat')
open(bat_path, 'w', encoding='gbk', newline='').write(bat)
print('执行 update.bat ...')
os.startfile(bat_path)

# 3) 等待 bat + 新版启动
time.sleep(16)

# 4) 检查
replaced = md5(old) == md5(new)
print('替换完成:', replaced)
out = subprocess.check_output('tasklist /fi "imagename eq DocFormatTool.exe" /fo csv', shell=True).decode('gbk', errors='ignore')
running = 'DocFormatTool' in out
print('新版进程运行中:', running)
if not running:
    print('→ 复现 LoadLibrary 失败（新版启动失败）')

# 5) 清理
os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
time.sleep(1)
shutil.rmtree(tdir, ignore_errors=True)
print('清理完成')
