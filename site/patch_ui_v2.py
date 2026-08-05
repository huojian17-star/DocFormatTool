# -*- coding: utf-8 -*-
"""UI 重做 v2（完整版）：AiNiee Fluent 风格——莫兰迪配色 + 侧边栏导航 + 卡片化 + 主区滚动
替换 app/main.py 的 _apply_theme 与 _build_ui（保留全部回调与控件同名变量）"""
import re

P = r'app\main.py'
src = open(P, encoding='utf-8').read()

NEW_THEME = '''    def _apply_theme(self):
        """莫兰迪现代风格（参考 AiNiee Fluent 设计）：米白底 + 白卡片 + 深灰主按钮 + 蓝点缀。"""
        self.BG = "#F5F5F5"       # 窗口背景（米白）
        self.PANEL = "#FFFFFF"    # 卡片/侧边栏（白）
        self.FG = "#2C2C2C"       # 主文字（深灰）
        self.FG_DIM = "#8A8A8A"   # 次要文字（中灰）
        self.LINE = "#E8E8E8"     # 分割线/边框（浅灰）
        self.ACCENT = "#2563EB"   # 品牌蓝（顶部色带）
        self.SELECT = "#EBEBEB"   # 选中/悬停底（浅灰）
        self.BTN = "#4A4A4A"      # 主按钮（深灰，AiNiee 风格）
        self.BTN_HOVER = "#3A3A3A"
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
        tk.Label(card, text=title, bg=self.PANEL, fg=self.FG,
                 font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", padx=20, pady=(14, 4))
        tk.Frame(card, bg=self.LINE, height=1).pack(fill="x", padx=20)
        body = tk.Frame(card, bg=self.PANEL)
        body.pack(fill="x", padx=20, pady=14)
        card.pack(fill="x", padx=16, pady=8)
        return card, body

    def _nav_scroll(self, frac):
        """侧边栏导航：主区滚动到对应位置。"""
        try:
            self._canvas.yview_moveto(frac)
        except Exception:
            pass

'''

NEW_UI = '''    def _build_ui(self):
        # ---- 顶部：蓝色色带 + 标题行 ----
        tk.Frame(self, bg=self.ACCENT, height=4).pack(fill="x")
        frm_head = tk.Frame(self, bg=self.PANEL, height=54)
        frm_head.pack(fill="x")
        frm_head.pack_propagate(False)
        tk.Label(frm_head, text="DocFormatTool", bg=self.PANEL, fg=self.FG,
                 font=("Microsoft YaHei", 14, "bold")).pack(side="left", padx=20)
        tk.Label(frm_head, text="规范文档一键排版工具", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 10)).pack(side="left", padx=(8, 0))
        tk.Label(frm_head, text="v" + version_mod.VERSION, bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 9)).pack(side="right", padx=20)

        # ---- 主体：侧边栏 + 主区 ----
        frm_body = tk.Frame(self, bg=self.BG)
        frm_body.pack(fill="both", expand=True)

        # 侧边栏
        frm_side = tk.Frame(frm_body, bg=self.PANEL, width=168)
        frm_side.pack(side="left", fill="y")
        frm_side.pack_propagate(False)
        tk.Label(frm_side, text="导 航", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 9)).pack(anchor="w", padx=20, pady=(16, 8))
        for txt, frac in [("首页", 0.0), ("排版", 0.24), ("高级选项", 0.52)]:
            b = tk.Button(frm_side, text="  " + txt, command=lambda f=frac: self._nav_scroll(f),
                          bg=self.PANEL, fg=self.FG, bd=0, anchor="w", relief="flat",
                          font=("Microsoft YaHei", 10), activebackground=self.SELECT,
                          activeforeground=self.FG, cursor="hand2", width=18)
            b.pack(fill="x", pady=1, padx=8)
        tk.Label(frm_side, text="", bg=self.PANEL).pack(expand=True)
        tk.Label(frm_side, text="● 完全本地运行", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 8)).pack(anchor="w", padx=20, pady=(0, 4))
        tk.Label(frm_side, text="论文不离开你的电脑", bg=self.PANEL, fg=self.FG_DIM,
                 font=("Microsoft YaHei", 8)).pack(anchor="w", padx=20, pady=(0, 14))

        # 主区：Canvas 滚动
        self._canvas = tk.Canvas(frm_body, bg=self.BG, highlightthickness=0)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._main = tk.Frame(self._canvas, bg=self.BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._main, anchor="nw")
        self._main.bind("<Configure>",
                        lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfigure(self._win_id, width=e.width))
        self._canvas.bind("<MouseWheel>",
                          lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ---- 授权卡片 ----
        _, body = self._card(self._main, "授权")
        self.var_key = tk.StringVar()
        tk.Label(body, text="激活密钥：", bg=self.PANEL, fg=self.FG).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        ttk.Entry(body, textvariable=self.var_key, width=30).grid(row=0, column=1, pady=4)
        ttk.Button(body, text="激活", command=self._activate).grid(row=0, column=2, padx=8)
        self.lbl_status = ttk.Label(body, text="", foreground="#DC2626")
        self.lbl_status.grid(row=0, column=3, padx=8)

        # ---- 格式来源卡片 ----
        _, body = self._card(self._main, "选择格式来源")
        self.var_mode = tk.StringVar(value="template")
        ttk.Radiobutton(body, text="① 上传学校模板（程序自动识别，最贴合本校要求）",
                        variable=self.var_mode, value="template",
                        command=self._on_mode_change).grid(row=0, column=0, sticky="w", pady=4)
        ttk.Radiobutton(body, text="② 使用内置通用模板（无需上传，一键套用）",
                        variable=self.var_mode, value="preset",
                        command=self._on_mode_change).grid(row=1, column=0, sticky="w", pady=4)
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
        _, body = self._card(self._main, "排版")
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
        tk.Label(body, text="提示：\\n"
                  "1. 支持 .txt / .md / .docx；docx 保留原图片表格，仅规范格式\\n"
                  "2. 标题建议带编号，如「1」「1.1」「第一章」「一、」\\n"
                  "3. 摘要、关键词、参考文献写在相应位置，程序自动识别\\n"
                  "4. 排版完成会自动质检，通过即符合所选模板格式",
                  bg=self.PANEL, fg=self.FG_DIM, justify="left",
                  font=("Microsoft YaHei", 9)).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(10, 2))

        # ---- 高级选项卡片 ----
        _, body = self._card(self._main, "高级选项")
        self.var_adv = tk.BooleanVar(value=False)
        ttk.Checkbutton(body, text="自定义排版细节（机器自动识别可能出错的地方，可手动指定）",
                        variable=self.var_adv, command=self._on_adv_toggle).grid(
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

        # ---- 底部：一键排版按钮 + 隐私/免责 ----
        frm_foot = tk.Frame(self._main, bg=self.BG)
        frm_foot.pack(fill="x", padx=16, pady=(6, 4))
        ttk.Button(frm_foot, text="一键排版", style="Primary.TButton",
                   command=self._run).pack(side="right", padx=(8, 0))
        ttk.Button(frm_foot, text="退出", command=self.destroy).pack(side="right")
        tk.Label(self._main, text="本软件完全本地运行，断网也能正常排版，论文不会离开你的电脑。",
                 bg=self.BG, fg=self.FG_DIM, font=("Microsoft YaHei", 9)).pack(pady=(4, 2))
        tk.Label(self._main, text="免责声明：本工具仅做格式排版，不修改论文内容；不提供代写、降重、降低AIGC检测等服务，不保证通过任何审核。学术诚信由论文作者本人负责，请遵守学校规范。",
                 bg=self.BG, fg=self.FG_DIM, wraplength=720, justify="center",
                 font=("Microsoft YaHei", 8)).pack(pady=(0, 12))

        self._on_mode_change()

'''

# ---- 替换 _apply_theme ----
pat_theme = re.compile(r'    def _apply_theme\(self\):.*?\n    def _center_window\(self\):', re.S)
assert pat_theme.search(src), '_apply_theme 未找到'
src = pat_theme.sub(NEW_THEME + '    def _center_window(self):', src, count=1)

# ---- 替换 _build_ui ----
pat_ui = re.compile(r'    def _build_ui\(self\):.*?\n    def _on_adv_toggle\(self\):', re.S)
assert pat_ui.search(src), '_build_ui 未找到'
src = pat_ui.sub(NEW_UI + '    def _on_adv_toggle(self):', src, count=1)

open(P, 'w', encoding='utf-8', newline='').write(src)
print('UI 重做完成：_apply_theme + _build_ui 已替换')
