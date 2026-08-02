# -*- coding: utf-8 -*-
"""质检日志：记录每次排版的体检结果，供卖家统计真实成功率。

日志写 %APPDATA%/DocFormatTool/qc_log.jsonl（学生端 exe 无写权限的目录不可用）。
"""
import json
import os
import time

_LOG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "DocFormatTool")
_LOG_FILE = os.path.join(_LOG_DIR, "qc_log.jsonl")


def record(src: str, cfg_label: str, results, out: str = ""):
    """记录一次排版的体检结果。results: [(level, item, detail), ...]"""
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        entry = {
            "t": time.strftime("%Y-%m-%d %H:%M:%S"),
            "src": os.path.basename(src) if src else "",
            "cfg": cfg_label,
            "out": os.path.basename(out) if out else "",
            "pass": sum(1 for lv, _, _ in results if lv == "PASS"),
            "warn": sum(1 for lv, _, _ in results if lv == "WARN"),
            "fail": sum(1 for lv, _, _ in results if lv == "FAIL"),
            "problems": [d for lv, _, d in results if lv == "FAIL"],
        }
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 日志失败不影响主流程


def summary(n: int = 500):
    """统计最近 n 条记录的通过率。返回 (总次数, 全通过次数, 通过率, 按配置分组, 高频问题)。"""
    rows = []
    if os.path.exists(_LOG_FILE):
        with open(_LOG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
    rows = rows[-n:]
    total = len(rows)
    ok = sum(1 for r in rows if r.get("fail", 0) == 0)
    by_cfg = {}
    for r in rows:
        c = r.get("cfg", "?")
        by_cfg.setdefault(c, [0, 0])
        by_cfg[c][0] += 1
        if r.get("fail", 0) == 0:
            by_cfg[c][1] += 1
    problems = {}
    for r in rows:
        for p in r.get("problems", []):
            problems[p] = problems.get(p, 0) + 1
    top = sorted(problems.items(), key=lambda x: -x[1])[:5]
    rate = (ok / total * 100) if total else 0
    return total, ok, rate, by_cfg, top
