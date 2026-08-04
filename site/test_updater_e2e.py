# -*- coding: utf-8 -*-
"""端到端测试 updater 完整流程（无梯子环境）：updater → 下载完整版 → 覆盖 → 启动 v1.0.7"""
import os, sys, time, shutil, subprocess

TD = r"F:\论文排版工具_测试包\updater_测试"
if os.path.exists(TD):
    shutil.rmtree(TD)
os.makedirs(TD)

# 模拟 v1.0.4 更新后的状态：DocFormatTool.exe = updater 内容
shutil.copy(r"F:\论文排版工具_测试包\updater.exe", os.path.join(TD, "DocFormatTool.exe"))
print("测试目录就绪，DocFormatTool.exe = updater")

# 运行 updater（它读 version.json → 下载完整版 → 覆盖 → 启动 v1.0.7）
t0 = time.time()
proc = subprocess.Popen(
    [os.path.join(TD, "DocFormatTool.exe")],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore")

# 等待：下载 17MB ghfast ~27s + 覆盖 2s + 启动
time.sleep(75)
print("75s 后进程状态:", "运行中" if proc.poll() is None else "已退出")
# 检查是否已生成 v1.0.7（DocFormatTool.exe 大小应 ~17MB 且是完整版）
final = os.path.join(TD, "DocFormatTool.exe")
size = os.path.getsize(final) if os.path.exists(final) else 0
print("DocFormatTool.exe 大小: %.1fMB (应≈16.8MB 完整版)" % (size / 1048576))
try:
    out = proc.stdout.read(200)
    print("updater 输出:", out[-200:] if out else "(无)")
except Exception:
    pass

# 检查是否有 v1.0.7 窗口
import ctypes, ctypes.wintypes as wt
user32 = ctypes.windll.user32
titles = []
@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cb(h, l):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(h, buf, 256)
    if "规范文档一键排版" in buf.value:
        titles.append(buf.value)
    return True
user32.EnumWindows(cb, 0)
print("检测到窗口:", titles)
# 终止可能启动的 v1.0.7
for p in ["DocFormatTool"]:
    os.system("taskkill /f /im %s.exe >nul 2>&1" % p)
print("DONE")
