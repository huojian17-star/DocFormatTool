# -*- coding: utf-8 -*-
"""中文路径测试：v1.0.12 和 v1.0.13 复制到中文目录分别启动，看哪个 LoadLibrary 失败"""
import os, shutil, subprocess, time, ctypes, ctypes.wintypes as wt

cn_dir = r'F:\论文排版工具_测试包\cn_path_test'
shutil.rmtree(cn_dir, ignore_errors=True)
os.makedirs(cn_dir)

def start_test(label, src, name):
    dst = os.path.join(cn_dir, name)
    shutil.copy2(src, dst)
    p = subprocess.Popen([dst], cwd=cn_dir)
    time.sleep(13)
    ret = p.poll()
    if ret is not None:
        print('%s: 启动失败 退出码=%s ← 中文路径问题' % (label, ret))
    else:
        titles = []
        @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
        def cb(h, l):
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetWindowTextW(h, buf, 256)
            if '规范文档一键排版' in buf.value:
                titles.append(buf.value)
            return True
        ctypes.windll.user32.EnumWindows(cb, 0)
        print('%s: 启动成功 窗口=%s' % (label, titles))
        os.system('taskkill /f /im DocFormatTool.exe >nul 2>&1')
        time.sleep(1)

# v1.0.12（bash-131 打包）
start_test('v1.0.12', r'dist\DocFormatTool.exe', 'v12.exe')
# v1.0.13（bash-122 打包）
start_test('v1.0.13', r'releases\DocFormatTool.exe', 'v13.exe')

shutil.rmtree(cn_dir, ignore_errors=True)
print('清理完成')
