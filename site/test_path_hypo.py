# -*- coding: utf-8 -*-
"""验证论坛假说：conda DLL 依赖 + PATH 差异
干净 PATH（无 conda Library\\bin）启动 v1.0.13 → 应失败（LoadLibrary）
完整 PATH（当前环境）启动 → 应成功
"""
import os, subprocess, time, sys

exe = r'releases\DocFormatTool.exe'
print('测试 exe:', exe)

def launch(label, env):
    p = subprocess.Popen([exe], env=env, cwd=os.path.dirname(exe))
    time.sleep(12)
    ret = p.poll()
    if ret is not None:
        print('%s: 启动失败 退出码=%s' % (label, ret))
        return False
    else:
        print('%s: 启动成功（进程存活）' % label)
        os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
        time.sleep(1)
        return True

# 1) 干净 PATH（只有系统目录——模拟 Explorer 双击的干净会话）
env_clean = os.environ.copy()
env_clean['PATH'] = r'C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem'
print('--- 干净 PATH（模拟双击）---')
r1 = launch('干净PATH', env_clean)

# 2) 完整 PATH（当前环境，含 conda）
print('--- 完整 PATH（当前环境，含 conda）---')
r2 = launch('完整PATH', os.environ.copy())

print('\n=== 结论 ===')
if not r1 and r2:
    print('✅ 论坛假说实锤：干净 PATH 失败、完整 PATH 成功 → conda DLL 依赖缺失（PATH 差异）')
elif r1 and r2:
    print('❌ 假说不成立：干净 PATH 也能启动')
else:
    print('⚠️ 两种都%s，需进一步排查' % ('失败' if not r2 else '成功'))
