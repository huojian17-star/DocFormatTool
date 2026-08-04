# -*- coding: utf-8 -*-
"""在 app/main.py 注入：低置信段落扫描 + 确认弹窗 + 排版接线"""
src = open(r'app\main.py', encoding='utf-8').read()

# 1) 新方法：_scan_uncertain + _confirm_uncertain（插在 def _run 前）
anchor = '    def _run(self):'
assert anchor in src, '_run 未找到'
new_methods = '''    def _scan_uncertain(self, docx_path):
        """扫描低置信段落（引擎拿不准的"数字. 短行"），返回 [(index, text)]。
        与引擎同遍历（body.iter w:p + para_text），表格内段落不弹（数据行）。"""
        import engine.infer as infer
        from docx import Document
        from docx.oxml.ns import qn
        items = []
        try:
            doc = Document(docx_path)
            for idx, p_el in enumerate(doc.element.body.iter(qn("w:p"))):
                t = build_docx.para_text(p_el).strip()
                if not t:
                    continue
                # 跳过表格内段落（数据行，不弹窗）
                if build_docx._in_table(p_el):
                    continue
                if infer.is_uncertain(t, md_mode=False):
                    items.append((idx, t))
        except Exception:
            pass
        return items

    def _confirm_uncertain(self, items):
        """低置信段落确认弹窗：每行显示文本+角色下拉，返回 forced_map {text: role}。
        用户可保持"按默认"（不覆盖）或指定角色。"""
        import tkinter as tk
        from tkinter import ttk
        if not items:
            return {}
        win = tk.Toplevel(self)
        win.title("请确认以下段落格式")
        win.geometry("620x460")
        win.transient(self)
        win.grab_set()
        tk.Label(win, text="以下段落程序判断不准（可能是一级/二级/三级标题，也可能是正文或列举），"
                           "请帮确认：", wraplength=560, justify="left",
                 font=("Microsoft YaHei", 10)).pack(pady=(12, 6), padx=12, anchor="w")
        # 滚动容器
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=12)
        canvas = tk.Canvas(frame, highlightthickness=0)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        choices = ["按默认处理", "正文", "一级标题", "二级标题", "三级标题"]
        role_map = {"正文": "body", "一级标题": "heading1", "二级标题": "heading2", "三级标题": "heading3"}
        vars_ = []
        for i, (idx, text) in enumerate(items):
            row = ttk.Frame(inner)
            row.pack(fill="x", pady=3)
            tk.Label(row, text="%d. %s" % (i + 1, text[:34] + ("…" if len(text) > 34 else "")),
                     width=42, anchor="w", font=("Microsoft YaHei", 9),
                     wraplength=320).pack(side="left", padx=(0, 8))
            var = tk.StringVar(value="按默认处理")
            ttk.Combobox(row, textvariable=var, values=choices, state="readonly",
                         width=12).pack(side="right")
            vars_.append((text, var))
        def on_ok():
            win.destroy()
        def on_all():
            for _, var in vars_:
                var.set("正文")
        tk.Button(win, text="全部按正文", command=on_all,
                  font=("Microsoft YaHei", 9)).pack(side="left", padx=(12, 4), pady=10)
        tk.Button(win, text="确定", command=on_ok, width=10,
                  font=("Microsoft YaHei", 9)).pack(side="right", padx=12, pady=10)
        self.wait_window(win)
        forced = {}
        for text, var in vars_:
            v = var.get()
            if v in role_map:
                forced[text] = role_map[v]
        return forced

'''
src = src.replace(anchor, new_methods + anchor, 1)
print('已注入扫描+弹窗方法')

# 2) L687 接线：docx 输入时扫描→弹窗→传 forced_map
old = '''            report_path = None
            if src.lower().endswith(".docx"):
                stats = build_docx.reformat_existing(cfg, src, out)'''
new = '''            report_path = None
            if src.lower().endswith(".docx"):
                # 低置信段落确认：引擎拿不准的段落让用户确认角色（防误判，零配置）
                forced = {}
                try:
                    uncertain = self._scan_uncertain(src)
                    if uncertain:
                        forced = self._confirm_uncertain(uncertain)
                except Exception:
                    forced = {}
                stats = build_docx.reformat_existing(cfg, src, out, forced)'''
assert old in src, '接线点未找到'
src = src.replace(old, new, 1)
print('已接线')

open(r'app\main.py', 'w', encoding='utf-8', newline='').write(src)
print('完成')
