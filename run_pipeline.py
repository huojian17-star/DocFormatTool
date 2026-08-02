# -*- coding: utf-8 -*-
"""论文排版工具 CLI（学生端/测试用）。

用法:
  python run_pipeline.py 输入文件 [学校模板.docx] -o 输出.docx [--config 配置.json]
  python run_pipeline.py --inspect 输入文件          # 仅显示识别出的结构

输入支持 .txt / .md（图片用 ![描述](路径) 引用）/ .docx（仅文字）。
学校模板：程序自动分析其格式规则；可用 --save-config 保存分析结果供人工微调。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import infer
from engine import build_docx
from engine import config as config_mod
from tools import analyze as analyzer


def main():
    ap = argparse.ArgumentParser(description="论文格式排版工具")
    ap.add_argument("input", nargs="?", default=None, help="学生论文文件 (.txt/.md/.docx)")
    ap.add_argument("template", nargs="?", default=None, help="学校模板 .docx（自动分析格式）")
    ap.add_argument("-o", "--out", default=None, help="输出 .docx 路径")
    ap.add_argument("--config", default=None, help="已生成的格式配置 JSON（跳过模板分析）")
    ap.add_argument("--preset", default=None, help="内置通用模板 id，如 bachelor_cn / ieee / apa")
    ap.add_argument("--save-config", default=None, help="把模板分析结果保存为 JSON")
    ap.add_argument("--inspect", action="store_true", help="只显示识别结构，不生成文档")
    ap.add_argument("--list-presets", action="store_true", help="列出内置模板")
    args = ap.parse_args()

    if args.list_presets:
        for pid, title in config_mod.list_presets():
            print("%-16s %s" % (pid, title))
        return

    if not args.input:
        sys.exit("需要提供输入文件（或使用 --list-presets）")
    if not os.path.exists(args.input):
        sys.exit("输入文件不存在: %s" % args.input)

    # 1. 结构识别
    structs = infer.parse_file(args.input)
    if args.inspect:
        for st in structs:
            print("[%s] %s" % (st["type"], st["text"][:80]))
        return
    # 无标题预警（仅从零生成的 txt/md 有影响；docx 改写式保留原结构）
    if not args.input.lower().endswith(".docx"):
        n_heads = sum(1 for st in structs if st["type"] in ("heading1", "heading2", "heading3"))
        if n_heads == 0:
            print("警告：未识别到任何章节标题，排版将保留原文顺序。建议检查标题是否带编号。")

    # 2. 格式配置
    cfg = None
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = config_mod.merge_default(json.load(f))
    elif args.template:
        cfg = config_mod.merge_default(analyzer.analyze(args.template))
        if args.save_config:
            with open(args.save_config, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            print("格式配置已保存 ->", args.save_config)
    elif args.preset:
        cfg = config_mod.load_preset(args.preset)
        print("使用内置模板: %s" % cfg.get("school", args.preset))
    else:
        sys.exit("需要提供学校模板（.docx）、--config 配置 JSON 或 --preset 内置模板")

    # 3. 生成
    out = args.out or (os.path.splitext(args.input)[0] + "_已排版.docx")
    base_dir = os.path.dirname(os.path.abspath(args.input))
    if args.input.lower().endswith(".docx"):
        build_docx.reformat_existing(cfg, args.input, out)
        print("排版完成（保留原图片/表格）->", out)
    else:
        build_docx.build(cfg, structs, out, base_dir)
        print("排版完成 ->", out)
    print("提示：请用 Word 打开检查；目录/页码域如需刷新请 Ctrl+A → F9。")

    # 质检记录（卖家成功率统计）
    try:
        from engine import qc_log
        from tools import validate as V
        results, _ = V.validate(out, args.input, cfg, cfg.get("school", "?"))
        qc_log.record(args.input, cfg.get("school", "?"), results, out)
    except Exception:
        pass


if __name__ == "__main__":
    main()
