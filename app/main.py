# -*- coding: utf-8 -*-
"""学生端图形界面（tkinter，打包成 exe 后双击即用）。

流程：激活（输入密钥绑定本机）→ 选论文文件 → 选学校模板 → 一键排版。
"""
import json
import os
import shutil
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from engine import infer, build_docx
from engine import config as config_mod
from tools import analyze as analyzer
from tools import validate as V
from engine import qc_log
from license import fingerprint as fpmod
from license import keys as keymod
from license import version as version_mod


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # 单实例锁：防止多开。PyInstaller onefile 每实例解压独立 _MEI 临时目录，
        # 多开竞争清理时偶发 "Failed to load Python DLL"（LoadLibrary 失败）。
        try:
            import ctypes
            self._mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "DocFormatTool_SingleInstance_Mutex")
            if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                ctypes.windll.user32.MessageBoxW(None, "程序已在运行，请勿重复打开。", "提示", 0x40)
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass  # 锁失败不阻塞（非 Windows 或权限问题）
        self._cleanup_stale_mei()
        self.title("规范文档一键排版工具 v%s" % version_mod.VERSION)
        self.geometry("980x760")
        self.minsize(880, 660)  # 防止被拖小导致按钮消失
        # 允许拉伸/最大化（窗口化全屏）；底部按钮用 grid 固定，拉大也不会被挤走
        self._apply_theme()
        self._fp = fpmod.fingerprint()
        self._build_ui()
        self._refresh_status()
        self._center_window()
        self._async_check_update()
        self._build_menu()

    def _build_menu(self):
        """菜单栏：帮助 → 关于（GitHub 引流入口）。"""
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.config(menu=menubar)

    def _show_about(self):
        """关于窗口：版本信息 + GitHub 引流。"""
        import webbrowser
        win = tk.Toplevel(self)
        win.title("关于")
        win.resizable(False, False)
        frm = ttk.Frame(win, padding=18)
        frm.pack()
        ttk.Label(frm, text="规范文档一键排版工具", font=("", 15, "bold")).pack(pady=(0, 2))
        ttk.Label(frm, text="版本 v%s" % version_mod.VERSION).pack()
        ttk.Label(frm, text="论文格式一键排版：任意格式文档 → 规范 Word", foreground="#6b7280").pack(pady=(6, 2))
        ttk.Label(frm, text="支持 Word / Markdown / 文本，自动识别学校模板格式。",
                  foreground="#6b7280").pack(pady=(0, 8))
        ttk.Button(frm, text="⭐ GitHub 开源项目（欢迎 Star / 提建议 / 交流）",
                   command=lambda: webbrowser.open("https://github.com/huojian17-star/DocFormatTool")).pack(pady=4)
        ttk.Label(frm, text="本软件完全本地运行，断网也能正常排版。",
                  foreground="#6b7280").pack(pady=(8, 0))
        ttk.Button(frm, text="关闭", command=win.destroy).pack(pady=(10, 0))
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        win.geometry("+%d+%d" % (max(0, win.winfo_screenwidth() // 2 - w // 2),
                                  max(0, win.winfo_screenheight() // 2 - h // 2)))

    def _async_check_update(self):
        """后台检查更新（失败静默），有新版本弹窗提示。"""
        import threading

        def _work():
            result = version_mod.check_update()
            if result:
                new_ver, url, note, manual_url, manual_pwd = result
                self.after(0, lambda: self._show_update(new_ver, url, note, manual_url, manual_pwd))

        threading.Thread(target=_work, daemon=True).start()

    def _show_update(self, new_ver, url, note, manual_url="", manual_pwd=""):
        msg = "发现新版本 v%s（当前 v%s）" % (new_ver, version_mod.VERSION)
        if note:
            msg += "\n更新内容：%s" % note
        msg += "\n\n点击\"是\"开始下载并自动更新（激活状态不受影响）。"
        # 换成可复制链接的自定义弹窗（messagebox 文本无法选中复制，链接等于白给）
        import webbrowser
        links = []
        if manual_url:
            links.append(("蓝奏云（提取码 %s）" % (manual_pwd or "无"), manual_url))
        links.append(("GitHub Releases 页面", "https://github.com/huojian17-star/DocFormatTool/releases"))
        self._show_links_window(
            "发现新版本", msg, links,
            # 回调接收 win（_show_links_window 把自身窗口传给回调；直接引用 win 会 NameError）
            extra_btns=[("自动更新", lambda w: (w.destroy(), self._start_download(url, manual_url, manual_pwd)))])

    def _start_download(self, url, manual_url, manual_pwd):
        import threading
        # 进度窗口必须在主线程创建（tkinter 控件不能在子线程创建，否则静默失败=点了没反应）
        win = tk.Toplevel(self)
        win.title("更新")
        win.geometry("340x120")
        win.resizable(False, False)
        ttk.Label(win, text="正在下载新版本（约 17MB）…").pack(pady=(16, 8))
        bar = ttk.Progressbar(win, length=290, mode="determinate")
        bar.pack(padx=20)
        ttk.Label(win, text="下载完成后程序会自动重启", foreground="#6b7280").pack(pady=(8, 0))
        threading.Thread(target=self._download_and_update,
                         args=(url, manual_url, manual_pwd, win, bar), daemon=True).start()

    def _copy_text(self, text):
        """复制文本到剪贴板"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _show_links_window(self, title, msg, links, extra_btns=None):
        """自定义弹窗：可读消息 + 可复制/一键打开的链接列表 + 按钮。

        links: [(标签, URL), ...]；extra_btns: [("按钮文字", 回调), ...]
        """
        import webbrowser
        win = tk.Toplevel(self)
        win.title(title)
        win.resizable(False, False)
        # 消息区（可复制）
        lbl = ttk.Label(win, text=msg, wraplength=520, justify="left")
        lbl.pack(padx=20, pady=(16, 6))
        # 链接区
        for label, u in links:
            row = ttk.Frame(win)
            row.pack(fill="x", padx=20, pady=3)
            ttk.Label(row, text=label, width=22).pack(side="left")
            ent = ttk.Entry(row, width=30)
            ent.insert(0, u)
            ent.configure(state="readonly")
            ent.pack(side="left", padx=4)
            ttk.Button(row, text="复制", width=5,
                       command=lambda u=u: self._copy_text(u)).pack(side="left", padx=2)
            ttk.Button(row, text="打开", width=5,
                       command=lambda u=u: webbrowser.open(u)).pack(side="left", padx=2)
        # 按钮区
        btns = ttk.Frame(win)
        btns.pack(pady=12)
        for text, cb in (extra_btns or []):
            # 回调签名接收 win（如"自动更新"需关闭弹窗）；lambda 默认参数防闭包失效
            ttk.Button(btns, text=text, style="Accent.TButton",
                       command=lambda cb=cb, w=win: cb(w)).pack(side="left", padx=6)
        ttk.Button(btns, text="关闭", command=win.destroy).pack(side="left", padx=6)
        # 居中于主窗口
        win.update_idletasks()
        w, h = win.winfo_width(), win.winfo_height()
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        win.geometry("+%d+%d" % (max(0, x), max(0, y)))
        return win

    def _download_and_update(self, url, manual_url="", manual_pwd="", win=None, bar=None):
        """后台下载新版 exe（进度窗口在主线程已建好）→ 写 updater 批处理 → 自动替换重启。"""
        import subprocess
        try:
            exe_path = version_mod.get_exe_path()
            exe_dir = os.path.dirname(exe_path)
            new_exe = os.path.join(exe_dir, "DocFormatTool_new.exe")
            _last = [0]

            def _prog(done, total):
                # 跨线程节流更新（每 ~0.3% 一次）；bar 已存在（主线程创建）
                if total and done - _last[0] >= total * 0.003:
                    _last[0] = done
                    if bar is not None:
                        self.after(0, lambda: (bar.configure(maximum=total or 1, value=done),
                                                win.title("更新 %d%%" % (done * 100 // total if total else 0))))

            version_mod.download(url, new_exe, total_limit=60, progress=_prog)
            if win is not None:
                self.after(0, win.destroy)
            # updater：等主程序退出 → 覆盖 exe → 启动新版 → 自删
            bat = os.path.join(exe_dir, "update.bat")
            with open(bat, "w", encoding="gbk") as f:
                f.write(version_mod.build_updater_bat(exe_path, new_exe))
            self.after(0, lambda: messagebox.showinfo("更新", "新版本已下载，程序将自动更新并重启。"))
            # 用 os.startfile 启动 bat（cmd /c + 空格路径会解析失败，startfile 用关联程序运行）
            self.after(0, lambda: os.startfile(bat))
            self.after(1500, self.destroy)
        except Exception as e:
            try:
                self.after(0, win.destroy)
            except Exception:
                pass
            manual = ""
            if manual_url:
                manual = "蓝奏云（提取码 %s）" % (manual_pwd or "无")
            # lambda 默认参数捕获 e（延迟执行时闭包变量会失效，导致 NameError 静默）
            self.after(0, lambda e=e: self._show_links_window(
                "更新失败",
                "自动下载失败：%s\n\n请手动下载新版，覆盖到原程序目录即可（激活状态不受影响）。" % e,
                [("蓝奏云", manual_url)] if manual_url else [],
                extra_btns=[]))

    def _cleanup_stale_mei(self):
        """清理 2 小时前的 _MEI 临时目录残留（PyInstaller onefile 强杀/崩溃后遗留）。
        残留的 _MEI 目录若与下次解压同名（PID 复用）会引发 LoadLibrary 失败。"""
        try:
            import glob, time
            now = time.time()
            for d in glob.glob(os.path.join(tempfile.gettempdir(), "_MEI*")):
                try:
                    if now - os.path.getmtime(d) > 7200:  # 2 小时前
                        shutil.rmtree(d, ignore_errors=True)
                except Exception:
                    pass
        except Exception:
            pass

    def _apply_theme(self):
        """莫兰迪现代风格（参考 AiNiee Fluent 设计）：米白底 + 白卡片 + 深灰主按钮 + 蓝点缀。"""
        self.BG = "#F5F5F5"       # 窗口背景（米白）
        self.PANEL = "#FFFFFF"    # 卡片/侧边栏（白）
        self.FG = "#2C2C2C"       # 主文字（深灰）
        self.FG_DIM = "#8A8A8A"   # 次要文字（中灰）
        self.LINE = "#E8E8E8"     # 分割线/边框（浅灰）
        self.ACCENT = "#60A5FA"   # 品牌蓝（顶部色带，浅蓝细线）
        self.SELECT = "#EEF2FF"   # 选中/悬停底（淡蓝）
        self.BTN = "#2563EB"      # 主按钮（蓝，主操作高亮）
        self.BTN_HOVER = "#1D4ED8"
        self.configure(bg=self.BG)
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.FG)
        style.configure("Dim.TLabel", background=self.BG, foreground=self.FG_DIM)
        style.configure("TRadiobutton", background=self.PANEL, foreground=self.FG)
        style.map("TRadiobutton", background=[("active", self.PANEL)])
        style.configure("TCheckbutton", background=self.PANEL, foreground=self.FG)
        style.map("TCheckbutton", background=[("active", self.PANEL)])
        style.configure("TCombobox", fieldbackground=self.PANEL, background=self.PANEL,
                        foreground=self.FG, arrowcolor=self.FG_DIM)
        style.map("TCombobox", fieldbackground=[("readonly", self.PANEL)],
                  foreground=[("readonly", self.FG)])
        style.configure("TEntry", fieldbackground=self.PANEL, foreground=self.FG, bordercolor=self.LINE)
        style.configure("TSpinbox", fieldbackground=self.PANEL, background=self.PANEL,
                        foreground=self.FG, arrowcolor=self.FG_DIM)
        style.configure("TButton", background=self.PANEL, foreground=self.FG, borderwidth=1,
                        bordercolor=self.LINE, lightcolor=self.PANEL, darkcolor=self.PANEL,
                        padding=(14, 7), font=("Microsoft YaHei", 10))
        style.map("TButton", background=[("active", self.SELECT), ("pressed", self.SELECT)],
                  bordercolor=[("active", self.LINE), ("pressed", self.LINE)])
        style.configure("Primary.TButton", background=self.BTN, foreground="#FFFFFF",
                        borderwidth=0, lightcolor=self.BTN, darkcolor=self.BTN,
                        padding=(22, 10), font=("Microsoft YaHei", 11, "bold"))
        style.map("Primary.TButton",
                  background=[("active", self.BTN_HOVER), ("pressed", self.BTN_HOVER)],
                  foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF")])

    def _card(self, parent, title):
        """创建白卡片（浅灰边框 + 标题 + 分隔线），返回 (卡片Frame, 内容Frame)。"""
        card = tk.Frame(parent, bg=self.PANEL, highlightbackground=self.LINE, highlightthickness=1)
        head = tk.Frame(card, bg=self.PANEL)
        head.pack(fill="x", padx=20, pady=(14, 4))
        tk.Label(head, text=title, bg=self.PANEL, fg="#1E293B",
                 font=("Microsoft YaHei", 11, "bold")).pack(side="left")
        tk.Frame(card, bg=self.LINE, height=1).pack(fill="x", padx=20)
        body = tk.Frame(card, bg=self.PANEL)
        body.pack(fill="x", padx=20, pady=14)
        card.pack(fill="x", padx=16, pady=8)
        return card, body

    def _nav_scroll(self, target=None, btn=None):
        """滚动主区到指定卡片（target=卡片 Frame），并更新侧边栏选中态。"""
        try:
            self.update_idletasks()
            if target is not None:
                y = target.winfo_y()
                total = max(self._canvas.bbox(self._win_id)[3], 1)
                frac = max(0.0, min(1.0, y / total))
                self._canvas.yview_moveto(frac)
            else:
                self._canvas.yview_moveto(0)
        except Exception:
            pass
        for b in self._nav_btns:
            b.configure(bg=self.PANEL, fg="#475569")
        if btn is not None:
            btn.configure(bg=self.SELECT, fg=self.BTN)

    def _nav_to(self, key, btn=None):
        cards = {"auth": getattr(self, "_card_auth", None),
                 "pt": getattr(self, "_card_pt", None),
                 "adv": getattr(self, "_card_adv", None)}
        self._nav_scroll(cards.get(key), btn)

    def _center_window(self):
        """窗口居中并确保完整显示在屏幕内（防止底部按钮被挤出屏幕）。"""
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry("+%d+%d" % (x, y))

    # ---------------- UI ----------------
    def _build_ui(self):
        # ---- 顶部：蓝色色带 + 标题行 ----
        tk.Frame(self, bg=self.ACCENT, height=3).pack(fill="x")
        frm_head = tk.Frame(self, bg=self.PANEL, height=54)
        frm_head.pack(fill="x")
        frm_head.pack_propagate(False)
        tk.Label(frm_head, text="DocFormatTool", bg=self.PANEL, fg="#1E293B",
                 font=("Microsoft YaHei", 14, "bold")).pack(side="left", padx=20)
        tk.Label(frm_head, text="规范文档一键排版工具", bg=self.PANEL, fg="#64748B",
                 font=("Microsoft YaHei", 9)).pack(side="left", padx=(8, 0))
        tk.Label(frm_head, text="v" + version_mod.VERSION, bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 9)).pack(side="right", padx=20)

        # ---- 主体：侧边栏 + 主区 ----
        frm_body = tk.Frame(self, bg=self.BG)
        frm_body.pack(fill="both", expand=True)

        # 侧边栏
        frm_side = tk.Frame(frm_body, bg=self.PANEL, width=168)
        frm_side.pack(side="left", fill="y")
        frm_side.pack_propagate(False)
        tk.Label(frm_side, text="", bg=self.PANEL).pack(pady=6)
        self._nav_btns = []
        nav_defs = [("auth", "🏠  首页"), ("pt", "📄  排版"), ("adv", "⚙️  高级选项")]
        for key, txt in nav_defs:
            b = tk.Button(frm_side, text=txt, command=lambda k=key, x=None: self._nav_to(k, x),
                          bg=self.PANEL, fg="#475569", bd=0, anchor="w", relief="flat",
                          font=("Microsoft YaHei", 10), activebackground=self.SELECT,
                          activeforeground=self.FG, cursor="hand2", width=20, pady=6)
            b.pack(fill="x", pady=2, padx=10)
            b.configure(command=lambda k=key, bb=b: self._nav_to(k, bb))
            self._nav_btns.append(b)
        # 默认选中「首页」
        if self._nav_btns:
            self._nav_btns[0].configure(bg=self.SELECT, fg=self.BTN)
        tk.Label(frm_side, text="", bg=self.PANEL).pack(expand=True)
        # 侧边栏底部：分隔线 + 信息
        tk.Frame(frm_side, bg=self.LINE, height=1).pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(frm_side, text="● 完全本地运行", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 8)).pack(anchor="w", padx=20, pady=(0, 4))
        tk.Label(frm_side, text="论文不离开你的电脑", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 8)).pack(anchor="w", padx=20, pady=(0, 14))

        # 主区：Canvas 滚动（grid row0）+ 底部固定按钮（row1）+ 免责（row2）
        frm_main = tk.Frame(frm_body, bg=self.BG)
        frm_main.pack(side="left", fill="both", expand=True)
        frm_main.rowconfigure(0, weight=1)
        frm_main.columnconfigure(0, weight=1)
        self._canvas = tk.Canvas(frm_main, bg=self.BG, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frm_main, orient="vertical", command=self._canvas.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._canvas.configure(yscrollcommand=sb.set)
        self._main = tk.Frame(self._canvas, bg=self.BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._main, anchor="nw")
        self._main.bind("<Configure>",
                        lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfigure(self._win_id, width=e.width))
        # 全局滚轮：鼠标在任何位置都能滚动主区（bind_all）
        self.bind_all("<MouseWheel>",
                      lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        # 底部固定：按钮横跨底部 + 免责一行小字（不随内容滚动）
        frm_foot = tk.Frame(frm_main, bg=self.BG)
        frm_foot.grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=(4, 4))
        ttk.Button(frm_foot, text="退出", command=self.destroy).pack(side="right")
        ttk.Button(frm_foot, text="一键排版", style="Primary.TButton",
                   command=self._run).pack(side="right", padx=(0, 8))
        tk.Label(frm_main, text="仅做格式排版，不修改内容；学术诚信由论文作者本人负责",
                 bg=self.BG, fg=self.FG_DIM, font=("Microsoft YaHei", 8)).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        # ---- 授权卡片 ----
        self._card_auth, body = self._card(self._main, "📋  授权")
        self.var_key = tk.StringVar()
        tk.Label(body, text="激活密钥：", bg=self.PANEL, fg=self.FG).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        self.ent_key = ttk.Entry(body, textvariable=self.var_key, width=34)
        self.ent_key.grid(row=0, column=1, pady=4, sticky="ew")
        self.btn_activate = ttk.Button(body, text="激活", command=self._activate)
        self.btn_activate.grid(row=0, column=2, padx=8)
        self.lbl_status = ttk.Label(body, text="", foreground="#DC2626")
        self.lbl_status.grid(row=0, column=3, padx=8)
        body.columnconfigure(1, weight=1)
        tk.Label(body, text="完全本地运行 · 断网可用 · 论文不离开电脑", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 9)).grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 0))

        # ---- 格式来源卡片 ----
        self._card_tmpl, body = self._card(self._main, "🎯  选择格式来源")
        self.var_mode = tk.StringVar(value="template")
        tk.Radiobutton(body, text="① 上传学校模板（程序自动识别，最贴合本校要求）",
                       variable=self.var_mode, value="template",
                       command=self._on_mode_change, bg=self.PANEL, fg=self.FG,
                       activebackground=self.PANEL, activeforeground=self.FG,
                       selectcolor=self.PANEL, anchor="w", justify="left",
                       wraplength=460, font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w", pady=4)
        tk.Radiobutton(body, text="② 使用内置通用模板（无需上传，一键套用）",
                       variable=self.var_mode, value="preset",
                       command=self._on_mode_change, bg=self.PANEL, fg=self.FG,
                       activebackground=self.PANEL, activeforeground=self.FG,
                       selectcolor=self.PANEL, anchor="w", justify="left",
                       wraplength=460, font=("Microsoft YaHei", 10)).grid(row=1, column=0, sticky="w", pady=4)
        self.frm_tmpl = tk.Frame(body, bg=self.PANEL)
        self.frm_tmpl.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self.var_tmpl = tk.StringVar()
        self.var_preset = tk.StringVar()
        self.cmb_preset = ttk.Combobox(self.frm_tmpl, textvariable=self.var_preset,
                                       state="readonly", width=46)
        presets = config_mod.list_presets()
        self.cmb_preset["values"] = [title for _, title in presets]
        self._preset_map = dict(presets)
        self._preset_title2id = {v: k for k, v in self._preset_map.items()}
        if presets:
            self.var_preset.set(presets[0][1])
        self.cmb_preset.bind("<<ComboboxSelected>>", lambda e: self._update_source_label())
        self.lbl_source = tk.Label(self.frm_tmpl, text="", fg=self.FG_DIM, bg=self.PANEL,
                                   wraplength=620, justify="left", font=("Microsoft YaHei", 9))
        self._update_source_label()
        self.btn_pick_tmpl = ttk.Button(self.frm_tmpl, text="选择模板…", command=self._pick_tmpl)
        self.ent_tmpl = ttk.Entry(self.frm_tmpl, textvariable=self.var_tmpl, width=44)
        self.frm_tmpl.columnconfigure(0, weight=1)

        # ---- 排版卡片 ----
        self._card_pt, body = self._card(self._main, "📝  排版")
        self.var_input = tk.StringVar()
        self.var_out = tk.StringVar()
        tk.Label(body, text="论文文件", bg=self.PANEL, fg=self.FG).grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Entry(body, textvariable=self.var_input).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(body, text="浏览…", command=self._pick_input).grid(row=0, column=2, padx=6)
        tk.Label(body, text="输出位置", bg=self.PANEL, fg=self.FG).grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Entry(body, textvariable=self.var_out).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(body, text="浏览…", command=self._pick_out).grid(row=1, column=2, padx=6)
        body.columnconfigure(1, weight=1)
        tk.Label(body, text="""提示：
1. 支持 .txt / .md / .docx；docx 保留原图片表格，仅规范格式
2. 标题建议带编号，如「1」「1.1」「第一章」「一、」
3. 摘要、关键词、参考文献写在相应位置，程序自动识别
4. 排版完成会自动质检，通过即符合所选模板格式""",
                  bg=self.PANEL, fg=self.FG_DIM, justify="left",
                  font=("Microsoft YaHei", 9)).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(10, 2))

        # ---- 高级选项卡片 ----
        self._card_adv, body = self._card(self._main, "⚙️  高级选项")
        self.var_adv = tk.BooleanVar(value=False)
        tk.Checkbutton(body, text="自定义排版细节（机器自动识别可能出错的地方，可手动指定）",
                       variable=self.var_adv, command=self._on_adv_toggle, bg=self.PANEL, fg=self.FG,
                       activebackground=self.PANEL, activeforeground=self.FG,
                       selectcolor=self.PANEL, anchor="w", justify="left",
                       wraplength=460, font=("Microsoft YaHei", 10)).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=2)
        self.frm_adv_body = tk.Frame(body, bg=self.PANEL)
        self.frm_adv_body.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(6, 0))

        # 行 0：页眉 + 页码位置
        tk.Label(self.frm_adv_body, text="页眉文字：", bg=self.PANEL, fg=self.FG).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_header = tk.StringVar()
        ttk.Entry(self.frm_adv_body, textvariable=self.var_header, width=16).grid(row=0, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="页码位置：", bg=self.PANEL, fg=self.FG).grid(
            row=0, column=2, sticky="w", padx=(16, 8))
        self.var_footer_pos = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_footer_pos, state="readonly", width=9,
                     values=["跟随模板", "居中", "右侧"]).grid(row=0, column=3, sticky="w")

        # 行 1：正文字号 + 行距
        tk.Label(self.frm_adv_body, text="正文字号：", bg=self.PANEL, fg=self.FG).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_body_size = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_body_size, state="readonly", width=9,
                     values=["跟随模板", "五号(10.5)", "小四(12)", "四号(14)", "三号(16)"]).grid(row=1, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="行距：", bg=self.PANEL, fg=self.FG).grid(
            row=1, column=2, sticky="w", padx=(16, 8))
        self.var_line_spacing = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_line_spacing, state="readonly", width=9,
                     values=["跟随模板", "1.0", "1.25", "1.5", "2.0"]).grid(row=1, column=3, sticky="w")

        # 行 2：首行缩进 + 前置页码
        tk.Label(self.frm_adv_body, text="首行缩进：", bg=self.PANEL, fg=self.FG).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_indent = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_indent, state="readonly", width=9,
                     values=["跟随模板", "2字符", "不缩进"]).grid(row=2, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="前置页码：", bg=self.PANEL, fg=self.FG).grid(
            row=2, column=2, sticky="w", padx=(16, 8))
        self.var_front = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_front, state="readonly", width=9,
                     values=["跟随模板", "无页码", "罗马数字", "阿拉伯"]).grid(row=2, column=3, sticky="w")

        # 行 3：标题字体 + 正文页码起始
        tk.Label(self.frm_adv_body, text="标题字体：", bg=self.PANEL, fg=self.FG).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_heading_font = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_heading_font, state="readonly", width=9,
                     values=["跟随模板", "黑体", "宋体", "楷体_GB2312", "仿宋_GB2312", "微软雅黑"]).grid(row=3, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="正文页码起始：", bg=self.PANEL, fg=self.FG).grid(
            row=3, column=2, sticky="w", padx=(16, 8))
        self.var_body_start = tk.IntVar(value=1)
        ttk.Spinbox(self.frm_adv_body, from_=1, to=99, width=8,
                    textvariable=self.var_body_start).grid(row=3, column=3, sticky="w")

        # 行 4：目录 + 摘要标题字号
        tk.Label(self.frm_adv_body, text="自动插入目录：", bg=self.PANEL, fg=self.FG).grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_toc = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_toc, state="readonly", width=9,
                     values=["跟随模板", "插入", "不插入"]).grid(row=4, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="摘要标题字号：", bg=self.PANEL, fg=self.FG).grid(
            row=4, column=2, sticky="w", padx=(16, 8))
        self.var_abs_size = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_abs_size, state="readonly", width=9,
                     values=["跟随模板", "三号(16)", "四号(14)", "小四(12)"]).grid(row=4, column=3, sticky="w")

        # 行 5：摘要标题字体 + 文档标题字号
        tk.Label(self.frm_adv_body, text="摘要标题字体：", bg=self.PANEL, fg=self.FG).grid(
            row=5, column=0, sticky="w", padx=(0, 8), pady=3)
        self.var_abs_font = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_abs_font, state="readonly", width=9,
                     values=["跟随模板", "黑体", "宋体", "楷体_GB2312"]).grid(row=5, column=1, sticky="w")
        tk.Label(self.frm_adv_body, text="文档标题字号：", bg=self.PANEL, fg=self.FG).grid(
            row=5, column=2, sticky="w", padx=(16, 8))
        self.var_title_size = tk.StringVar(value="跟随模板")
        ttk.Combobox(self.frm_adv_body, textvariable=self.var_title_size, state="readonly", width=9,
                     values=["跟随模板", "一号(26)", "小初(36)", "二号(22)", "小二(18)", "三号(16)"]).grid(row=5, column=3, sticky="w")

        # 行 6-7：保留颜色 / 保留斜体
        self.var_preserve_color = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frm_adv_body, text="保留原文文字颜色（不勾=统一黑色）",
                        variable=self.var_preserve_color).grid(
            row=6, column=0, columnspan=2, sticky="w", pady=3)
        self.var_preserve_italic = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.frm_adv_body, text="保留原文斜体（如英文文献期刊名斜体）",
                        variable=self.var_preserve_italic).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=3)

        self.frm_adv_body.grid_remove()
        self._on_adv_toggle()

        self._on_mode_change()

    def _on_adv_toggle(self):
        """展开/收起高级选项，并自适应窗口高度，防止底部按钮被挤出可视区。"""
        if self.var_adv.get():
            self.frm_adv_body.grid()
        else:
            self.frm_adv_body.grid_remove()
        self._fit_height()

    def _fit_height(self):
        """按内容请求高度调整窗口高度（受屏幕高度限制），保持按钮区完整可见。"""
        self.update_idletasks()
        req = self.winfo_reqheight()
        max_h = self.winfo_screenheight() - 90  # 任务栏 + 系统边距
        h = max(660, min(req + 8, max_h))
        # 窗口上移避免超出屏幕底部
        y = max(0, min(self.winfo_y(), self.winfo_screenheight() - h - 40))
        self.geometry("%dx%d+%d+%d" % (self.winfo_width(), h, self.winfo_x(), y))

    def _on_mode_change(self):
        """切换排版方式：显示上传框或内置模板下拉框。"""
        if self.var_mode.get() == "template":
            self.cmb_preset.grid_remove()
            self.lbl_source.grid_remove()
            self.ent_tmpl.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            self.btn_pick_tmpl.grid(row=0, column=1)
        else:
            self.ent_tmpl.grid_remove()
            self.btn_pick_tmpl.grid_remove()
            self.cmb_preset.grid(row=0, column=0, sticky="w")
            self.lbl_source.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.frm_tmpl.columnconfigure(0, weight=1)

    def _update_source_label(self):
        """显示当前内置模板的规范参考来源。"""
        title = self.var_preset.get()
        pid = self._preset_title2id.get(title)
        src = ""
        if pid:
            try:
                cfg = config_mod.load_preset(pid)
                src = cfg.get("source", "")
            except Exception:
                src = ""
        self.lbl_source.config(text=("模板参考来源：" + src) if src else "")

    # ---------------- actions ----------------
    def _confirm_uncertain(self, structs):
        """排版前批量确认低置信段落（"1. xxx"式：可能是标题也可能是列举）。

        一次弹窗列完所有不确定项，用户下拉选择后继续，不打断流程。
        """
        idxs = [i for i, st in enumerate(structs)
                if st["type"] in ("heading1", "heading2", "heading3")
                and infer.is_uncertain(st["text"])]
        if not idxs:
            return
        idxs = idxs[:12]
        win = tk.Toplevel(self)
        win.title("确认不确定段落")
        win.transient(self)
        win.grab_set()
        ttk.Label(win, text="以下段落可能是标题，也可能是列表/列举。请确认（不确定保持默认即可）：",
                  foreground="#6b7280").pack(padx=14, pady=(10, 6), anchor="w")
        frm = ttk.Frame(win)
        frm.pack(padx=14, pady=2)
        vars_ = []
        for k, i in enumerate(idxs):
            st = structs[i]
            ttk.Label(frm, text=st["text"][:26], width=32, anchor="w").grid(
                row=k, column=0, sticky="w", pady=2)
            v = tk.StringVar(value="按引擎判断")
            ttk.Combobox(frm, textvariable=v, state="readonly", width=10,
                         values=["按引擎判断", "正文", "一级标题", "二级标题", "三级标题"]).grid(
                row=k, column=1, pady=2)
            vars_.append((i, v))

        def _ok():
            for i, v in vars_:
                choice = v.get()
                if choice == "正文":
                    structs[i]["type"] = "body"
                elif choice == "一级标题":
                    structs[i]["type"] = "heading1"
                elif choice == "二级标题":
                    structs[i]["type"] = "heading2"
                elif choice == "三级标题":
                    structs[i]["type"] = "heading3"
            win.destroy()

        ttk.Button(win, text="确认，继续排版", command=_ok).pack(pady=(8, 12))
        win.wait_window()

    def _pick_input(self):
        path = filedialog.askopenfilename(title="选择论文文件",
                                          filetypes=[("文本/文档", "*.txt *.md *.docx"), ("所有文件", "*.*")])
        if path:
            self.var_input.set(path)
            default_out = os.path.splitext(path)[0] + "_已排版.docx"
            if not self.var_out.get():
                self.var_out.set(default_out)

    def _pick_tmpl(self):
        path = filedialog.askopenfilename(title="选择学校模板", filetypes=[("Word 模板", "*.docx")])
        if path:
            self.var_tmpl.set(path)

    def _pick_out(self):
        src = self.var_input.get().strip()
        cur = self.var_out.get().strip()
        init_dir = os.path.dirname(src) if src else os.path.expanduser("~")
        init_file = (os.path.basename(cur) if cur else
                     (os.path.splitext(os.path.basename(src))[0] + "_已排版.docx"
                      if src else "已排版.docx"))
        path = filedialog.asksaveasfilename(title="保存为", defaultextension=".docx",
                                            initialdir=init_dir, initialfile=init_file,
                                            filetypes=[("Word 文档", "*.docx")])
        if path:
            self.var_out.set(path)

    def _activate(self):
        key = self.var_key.get().strip()
        if not keymod.is_valid_format(key):
            messagebox.showerror("激活失败", "密钥格式不正确，请核对后重试。")
            return
        keymod.save_activation(key, self._fp)
        self._refresh_status()
        messagebox.showinfo("激活成功", "已绑定本机，可以正常使用了。\n注意：本密钥仅限当前这台电脑。")

    def _refresh_status(self):
        ok, reason = keymod.check_activation(self._fp)
        self._activated = ok
        if ok:
            self.lbl_status.config(text="✓ 已激活", foreground="#16a34a")
            try:
                self.ent_key.configure(state="disabled")
                self.btn_activate.configure(state="disabled")
            except Exception:
                pass
        else:
            try:
                self.ent_key.configure(state="normal")
                self.btn_activate.configure(state="normal")
            except Exception:
                pass
            # 简短原因：换机/文件异常/未激活 区分开，学生知道该怎么办
            short = {
                "未激活": "未激活",
                "激活文件损坏": "未激活（文件异常，请重新激活）",
                "激活信息校验失败，请重新激活": "未激活（文件异常，请重新激活）",
                "密钥无效": "未激活（密钥异常，请重新激活）",
                "本机未授权（激活信息与当前设备不匹配）": "未激活（非本机授权）",
            }.get(reason, "未激活")
            self.lbl_status.config(text=short, foreground="#dc2626")

    def _scan_uncertain(self, docx_path):
        """扫描低置信段落（引擎拿不准的"数字. 短行"），返回 [(index, text)]。
        与引擎同遍历（body.iter w:p + para_text），表格内段落不弹（数据行）。"""
        import engine.infer as infer
        from docx import Document
        from docx.oxml.ns import qn
        items = []
        try:
            doc = Document(docx_path)
            paras = list(doc.element.body.iter(qn("w:p")))
            for idx, p_el in enumerate(paras):
                t = build_docx.para_text(p_el).strip()
                if not t:
                    continue
                # 跳过表格内段落（数据行，不弹窗）
                if build_docx._in_table(p_el):
                    continue
                if infer.is_uncertain(t, md_mode=False):
                    # 收集上下文：前后最近的非空段落（帮助用户在原文定位）
                    prev_t = next_t = ""
                    for j in range(idx - 1, -1, -1):
                        pt = build_docx.para_text(paras[j]).strip()
                        if pt:
                            prev_t = pt
                            break
                    for j in range(idx + 1, len(paras)):
                        nt = build_docx.para_text(paras[j]).strip()
                        if nt:
                            next_t = nt
                            break
                    items.append((idx, t, prev_t, next_t))
        except Exception:
            pass
        return items

    def _confirm_uncertain_docx(self, items):
        """docx 专用：低置信段落确认弹窗（完整段落 + 上下文 + 程序猜测 + 角色下拉）。
        返回 forced_map {text: role}。txt/md 流程用原 _confirm_uncertain(structs)。"""
        import tkinter as tk
        from tkinter import ttk
        import engine.infer as infer
        if not items:
            return {}
        # 程序猜测 → 中文名（显示"程序认为：三级标题"帮助用户判断）
        guess_cn = {"heading1": "一级标题（一、/第一章）", "heading2": "二级标题（（一）/1.1）",
                    "heading3": "三级标题（1./1.1.1）", "body": "正文（普通段落）"}
        win = tk.Toplevel(self)
        win.title("请确认以下段落格式")
        win.geometry("780x520")
        win.transient(self)
        win.grab_set()
        tk.Label(win,
                 text="下面 %d 个段落，程序拿不准是「章节标题」还是「普通正文」（比如带编号的短句可能是标题，也可能是列举）。\n"
                      "请快速确认（不确定就保持默认，选错也能重新排版改回来）：" % len(items),
                 wraplength=720, justify="left", font=("Microsoft YaHei", 10)).pack(pady=(12, 6), padx=14, anchor="w")
        # 表头
        head = ttk.Frame(win)
        head.pack(fill="x", padx=14)
        tk.Label(head, text="段落内容", font=("Microsoft YaHei", 9, "bold"),
                 fg="#444").pack(side="left", padx=(0, 20))
        tk.Label(head, text="程序认为", font=("Microsoft YaHei", 9, "bold"),
                 fg="#444").pack(side="left", padx=(0, 30))
        tk.Label(head, text="请选择（如与你的意图不符）", font=("Microsoft YaHei", 9, "bold"),
                 fg="#444").pack(side="right", padx=(0, 8))
        # 滚动容器
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=14, pady=(2, 4))
        canvas = tk.Canvas(frame, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        choices = ["保持程序默认", "正文（普通段落）", "一级标题（章：一、/第一章）",
                   "二级标题（节：（一）/1.1）", "三级标题（小节：1./1.1.1）"]
        role_map = {"正文（普通段落）": "body", "一级标题（章：一、/第一章）": "heading1",
                    "二级标题（节：（一）/1.1）": "heading2", "三级标题（小节：1./1.1.1）": "heading3"}
        vars_ = []
        for i, (idx, text, prev_t, next_t) in enumerate(items):
            row = ttk.Frame(inner)
            row.pack(fill="x", pady=5)
            row.grid_columnconfigure(0, weight=1)
            # 段落内容：序号 + 完整文本 + 前后文（帮用户定位原文位置）
            ctx = ""
            if prev_t:
                ctx += "上文：…%s…\n" % (prev_t[:46] + ("…" if len(prev_t) > 46 else ""))
            if next_t:
                ctx += "下文：…%s…" % (next_t[:46] + ("…" if len(next_t) > 46 else ""))
            txt = "第 %d 段：%s" % (idx + 1, text)
            if ctx:
                txt += "\n" + ctx
            tk.Label(row, text=txt, anchor="w", justify="left", font=("Microsoft YaHei", 9),
                     fg="#111111", wraplength=330).grid(row=0, column=0, sticky="w", padx=(0, 10))
            # 程序猜测（小灰字，可换行）
            try:
                typ, _ = infer._classify(text)
                guess = guess_cn.get(typ, "正文（普通段落）")
            except Exception:
                guess = "正文（普通段落）"
            tk.Label(row, text=guess, fg="#888888", font=("Microsoft YaHei", 8),
                     anchor="nw", justify="left", width=20, wraplength=150).grid(row=0, column=1, sticky="nw", padx=(0, 10))
            var = tk.StringVar(value="保持程序默认")
            ttk.Combobox(row, textvariable=var, values=choices, state="readonly",
                         width=24).grid(row=0, column=2, sticky="ne")
            vars_.append((text, var))
        def on_ok():
            win.destroy()
        def on_all():
            for _, var in vars_:
                var.set("正文（普通段落）")
        tk.Button(win, text="全部按正文", command=on_all,
                  font=("Microsoft YaHei", 9)).pack(side="left", padx=(14, 4), pady=10)
        tk.Button(win, text="确定", command=on_ok, width=10,
                  font=("Microsoft YaHei", 9)).pack(side="right", padx=14, pady=10)
        self.wait_window(win)
        forced = {}
        for text, var in vars_:
            v = var.get()
            if v in role_map:
                forced[text] = role_map[v]
        # 数据积累：用户确认的低置信段落 → 训练集 JSONL（ONNX 分类器训练数据，文本+角色）
        if forced:
            try:
                import json
                train_dir = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data")
                os.makedirs(train_dir, exist_ok=True)
                with open(os.path.join(train_dir, "uncertain_labels.jsonl"), "a", encoding="utf-8") as f:
                    for text, role in forced.items():
                        f.write(json.dumps({"text": text, "role": role}, ensure_ascii=False) + "\n")
            except Exception:
                pass
        return forced

    def _run(self):
        if not self._activated:
            messagebox.showwarning("未激活",
                                   "请先输入密钥激活后再排版。\n\n"
                                   "密钥在窗口顶部\u201c授权\u201d区域输入，点\u201c激活\u201d即可。\n"
                                   "还没有密钥？请联系卖家获取（一个密钥仅限一台电脑使用）。")
            return
        src = self.var_input.get().strip()
        out = self.var_out.get().strip()
        if not src or not os.path.exists(src):
            messagebox.showerror("错误", "请选择论文文件。")
            return
        if not out:
            out = os.path.splitext(src)[0] + "_已排版.docx"
            self.var_out.set(out)
        try:
            structs = infer.parse_file(src)
            # 识别预览：从零生成的 txt/md 先让机器"讲出"识别结果，学生确认再排
            if not src.lower().endswith(".docx"):
                self._confirm_uncertain(structs)  # 批量确认低置信段落（标题 or 列举）
                heads = [st for st in structs if st["type"] in ("heading1", "heading2", "heading3")]
                if heads:
                    lines = ["识别到 %d 个章节标题：" % len(heads), ""]
                    for st in heads[:25]:
                        lv = st["type"][-1]
                        lines.append("  [%s级] %s" % (lv, st["text"][:40]))
                    if len(heads) > 25:
                        lines.append("  …（共 %d 个）" % len(heads))
                    lines.append("")
                    lines.append("确认机器识别正确后继续排版；\n识别不准可点\"取消\"，回去调整标题格式（如加编号「1」「第一章」）。")
                    if not messagebox.askyesno("识别预览（确认结构）", "\n".join(lines)):
                        return
            if self.var_mode.get() == "preset":
                title = self.var_preset.get()
                pid = next((k for k, v in self._preset_map.items() if v == title), None)
                if not pid:
                    raise ValueError("请选择内置模板")
                cfg = config_mod.load_preset(pid)
            else:
                tmpl = self.var_tmpl.get().strip()
                if not tmpl or not os.path.exists(tmpl):
                    messagebox.showerror("错误", "请选择学校模板文件。")
                    return
                cfg = config_mod.merge_default(analyzer.analyze(tmpl))
            # 高级选项：页码结构与排版细节覆盖
            if self.var_adv.get():
                front_map = {"无页码": "none", "罗马数字": "roman", "阿拉伯": "decimal"}
                pn = {"body_start": int(self.var_body_start.get())}
                if self.var_front.get() != "跟随模板":
                    pn["front_matter"] = front_map.get(self.var_front.get(), "none")
                cfg["page_numbering"] = pn
                if self.var_header.get().strip():
                    cfg["header_footer"]["header_text"] = self.var_header.get().strip()
                pos = self.var_footer_pos.get()
                if pos == "居中":
                    cfg["header_footer"]["footer_style"] = "center"
                elif pos == "右侧":
                    cfg["header_footer"]["footer_style"] = "right"
                size_map = {"五号(10.5)": 10.5, "小四(12)": 12, "四号(14)": 14, "三号(16)": 16}
                if self.var_body_size.get() in size_map:
                    cfg["fonts"]["body"]["size_pt"] = size_map[self.var_body_size.get()]
                ls = self.var_line_spacing.get()
                if ls != "跟随模板":
                    cfg["paragraph"]["line_spacing"] = float(ls)
                ind = self.var_indent.get()
                if ind == "2字符":
                    cfg["paragraph"]["first_line_indent_chars"] = 2
                elif ind == "不缩进":
                    cfg["paragraph"]["first_line_indent_chars"] = 0
                hf_ = self.var_heading_font.get()
                if hf_ != "跟随模板":
                    for lv in (1, 2, 3):
                        cfg["fonts"]["heading%d" % lv]["cn"] = hf_
                toc_ = self.var_toc.get()
                if toc_ == "插入":
                    cfg["toc"]["enabled"] = True
                elif toc_ == "不插入":
                    cfg["toc"]["enabled"] = False
                # 摘要标题字号/字体
                sz_map = {"三号(16)": 16, "四号(14)": 14, "小四(12)": 12}
                if self.var_abs_size.get() in sz_map:
                    cfg["fonts"].setdefault("abstract_heading", {})["size_pt"] = sz_map[self.var_abs_size.get()]
                af = self.var_abs_font.get()
                if af != "跟随模板":
                    cfg["fonts"].setdefault("abstract_heading", {})["cn"] = af
                # 文档标题字号
                ts_map = {"一号(26)": 26, "小初(36)": 36, "二号(22)": 22, "小二(18)": 18, "三号(16)": 16}
                if self.var_title_size.get() in ts_map:
                    cfg["fonts"].setdefault("doc_title", {})["size_pt"] = ts_map[self.var_title_size.get()]
                # 保留原文文字颜色（默认 False=统一黑色）
                cfg["preserve_colors"] = bool(self.var_preserve_color.get())
                # 保留原文斜体（默认 False=统一清除）
                cfg["preserve_italics"] = bool(self.var_preserve_italic.get())
            # 无标题预警：从零生成的 txt/md 识别不到章节时提醒（学生可能不看就提交）
            if not src.lower().endswith(".docx"):
                n_heads = sum(1 for st in structs if st["type"] in ("heading1", "heading2", "heading3"))
                if n_heads == 0:
                    if not messagebox.askyesno("提示",
                                               "未识别到任何章节标题（如「1」「1.1」「第一章」）。\n"
                                               "排版会保留原文顺序，标题可能不会加粗居中。\n\n仍要继续吗？\n"
                                               "（建议返回检查标题是否带编号，或改用 .docx 文件）"):
                        return
            report_path = None
            if src.lower().endswith(".docx"):
                # 低置信段落确认：引擎拿不准的段落让用户确认角色（防误判，零配置）
                forced = {}
                try:
                    uncertain = self._scan_uncertain(src)
                    if uncertain:
                        forced = self._confirm_uncertain_docx(uncertain)
                except Exception:
                    forced = {}
                stats = build_docx.reformat_existing(cfg, src, out, forced)
                report_path = build_docx.build_change_report(stats, cfg, src, out)
            else:
                build_docx.build(cfg, structs, out, os.path.dirname(os.path.abspath(src)))
            # 自动质检：字体/字号/页面/内容保留
            results, summary = V.validate(out, src, cfg, cfg.get("school", "当前配置"))
            qc_log.record(src, cfg.get("school", "?"), results, out)
            fails = [r for r in results if r[0] == "FAIL"]
            if fails:
                detail = "\n".join("[%s] %s: %s" % r for r in fails)
                messagebox.showwarning("排版完成，自检出异常",
                                       "排版完成！\n%s\n\n自检出以下问题，建议人工复核：\n%s\n\n%s" % (out, detail, summary))
            else:
                msg = "排版完成，自动质检全部通过！\n%s\n\n%s\n提示：如需刷新目录/页码，Ctrl+A 后按 F9。" % (out, summary)
                if report_path:
                    msg += "\n\n已生成《改动报告》：\n%s\n（打开可查看改动了哪些格式、覆盖率多少）" % report_path
                messagebox.showinfo("完成", msg)
        except Exception as e:
            messagebox.showerror("出错", "排版失败：%s" % e)


if __name__ == "__main__":
    # --selftest：更新链路自测（检查 version.json → 下载 full_url → sha256 校验 → 输出结果退出）
    # 用于每次发版后自动验证，无需 GUI 点击。用法: DocFormatTool.exe --selftest [--keep]
    if "--selftest" in sys.argv:
        import license.version as _v
        ok = _v.selftest(keep=("--keep" in sys.argv))
        sys.exit(0 if ok else 1)
    App().mainloop()
