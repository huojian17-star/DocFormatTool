# -*- coding: utf-8 -*-
"""批量回归：对全部内置模板 × 输入文档 跑排版+自动体检，输出汇总表。

用法:
  python tools/regression.py 论文文件... [-o 输出目录] [--verbose]
示例:
  python tools/regression.py samples\学生输入_思政论文.docx "D:\论文_管理研究方法 管理2304邓恺恒2302010189\管理2304邓恺恒2302010189.docx"
"""
import argparse
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import infer, build_docx, config as config_mod
from tools import validate as V


def run_one(preset_id, cfg, src, out_dir):
    """单个 (模板, 输入) 的排版+体检，返回 (preset, src_name, pass, warn, fail, first_problem)。
    坏文件/异常不中断整体回归。"""
    dst = os.path.join(out_dir, "%s_%s.docx" % (os.path.splitext(os.path.basename(src))[0], preset_id))
    base_dir = os.path.dirname(os.path.abspath(src))
    try:
        structs = infer.parse_file(src) if not src.lower().endswith(".docx") else None
        if src.lower().endswith(".docx"):
            build_docx.reformat_existing(cfg, src, dst)
        else:
            build_docx.build(cfg, structs, dst, base_dir)
        results, _ = V.validate(dst, src, cfg, preset_id)
        n_pass = sum(1 for lv, _, _ in results if lv == "PASS")
        n_warn = sum(1 for lv, _, _ in results if lv == "WARN")
        n_fail = sum(1 for lv, _, _ in results if lv == "FAIL")
        first = next((d for lv, it, d in results if lv == "FAIL"), "")
        return (preset_id, os.path.basename(src), n_pass, n_warn, n_fail, first)
    except Exception as e:
        return (preset_id, os.path.basename(src), 0, 0, 1, "处理失败: %s" % type(e).__name__)


def main():
    ap = argparse.ArgumentParser(description="批量回归：内置模板 × 输入 全量体检")
    ap.add_argument("inputs", nargs="+", help="输入论文文件（.txt/.md/.docx）")
    ap.add_argument("-o", "--out", default=None, help="输出目录（默认临时目录）")
    ap.add_argument("--verbose", action="store_true", help="打印每份完整报告")
    args = ap.parse_args()

    presets = config_mod.list_presets()
    out_dir = args.out or tempfile.mkdtemp(prefix="regress_")
    os.makedirs(out_dir, exist_ok=True)

    print("批量回归：%d 个内置模板 × %d 个输入文件" % (len(presets), len(args.inputs)))
    print("=" * 100)
    print("%-20s %-34s %6s %6s %6s  %s" % ("模板", "输入", "PASS", "WARN", "FAIL", "首个问题"))
    print("-" * 100)
    total_fail = 0
    for preset_id, title in presets:
        cfg = config_mod.load_preset(preset_id)
        for src in args.inputs:
            if not os.path.exists(src):
                print("%-20s %-34s 输入文件不存在" % (title, src))
                continue
            pid, srcn, np_, nw, nf, first = run_one(preset_id, cfg, src, out_dir)
            total_fail += nf
            print("%-20s %-34s %6d %6d %6d  %s" % (title[:20], srcn[:34], np_, nw, nf, first[:46]))
            if args.verbose and nf:
                print(V.report(os.path.join(out_dir, "%s_%s.docx" % (os.path.splitext(srcn)[0], preset_id)),
                               src, cfg, title)[0])
    print("=" * 100)
    print("总计失败项: %d" % total_fail)
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
