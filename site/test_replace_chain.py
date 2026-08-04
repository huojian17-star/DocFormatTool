# -*- coding: utf-8 -*-
"""隔离目录完整替换测试：模拟用户更新流程（taskkill→等待→copy→校验→start）"""
import sys, os, shutil, subprocess, time, hashlib
sys.path.insert(0, '.')
import license.version as v

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1048576), b''):
            h.update(c)
    return h.hexdigest()

# 准备隔离目录
tdir = os.path.join(os.environ['TEMP'], 'replace_test')
shutil.rmtree(tdir, ignore_errors=True)
os.makedirs(tdir)
old = os.path.join(tdir, 'DocFormatTool.exe')   # 被替换方（模拟当前 v1.0.12）
new = os.path.join(tdir, 'DocFormatTool_new.exe')  # 新版（v1.0.13）
shutil.copy2(r'dist\DocFormatTool.exe', old)
shutil.copy2(r'releases\DocFormatTool.exe', new)
print('old md5:', md5(old)[:10], '(v1.0.12)')
print('new md5:', md5(new)[:10], '(v1.0.13)')

# 生成 bat（含等待+errorlevel+大小检查）
bat = v.build_updater_bat(old, new)
bat_path = os.path.join(tdir, 'update.bat')
open(bat_path, 'w', encoding='gbk', newline='').write(bat)
print('bat 已写（长度 %d）' % len(bat))

# 执行 bat（模拟用户更新）
print('执行 update.bat ...')
os.startfile(bat_path)
time.sleep(10)

# 验证替换
if md5(old) == md5(new):
    print('替换成功: old 已被覆盖为 new 的内容 ✓')
else:
    print('替换失败: old md5 未变化 ✗')

# 验证新进程启动（bat 里 start 启动了 tmp 的 exe）
found = False
out = subprocess.check_output('tasklist /fi "imagename eq DocFormatTool.exe" /fo csv', shell=True).decode('gbk', errors='ignore')
found = 'DocFormatTool' in out
print('新进程启动:', found)

# 清理
os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
time.sleep(1)
shutil.rmtree(tdir, ignore_errors=True)
print('清理完成')
