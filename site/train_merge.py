# -*- coding: utf-8 -*-
"""合并训练试跑：LLM标注(真标签) + 规则高置信 + arXiv英文(结构真标签) → LightGBM → 评估低置信段"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from collections import Counter

TRAIN_DIR = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data")
ROLE_IDX = {"heading1": 0, "heading2": 1, "heading3": 2, "body": 3,
            "abstract_heading": 4, "keywords": 5, "ref_heading": 6, "ref_item": 7,
            "caption": 8, "appendix": 9}
FEAT_KEYS = ["len", "ends_punct", "has_url", "has_ref_type", "has_note_word",
             "num_h3", "num_h2", "num_h1", "cn_num", "paren_cn",
             "paren_digit", "digit_space", "digit_dot", "md_hash",
             "abstract", "keywords", "ref_head", "appendix", "first_char_verb"]

# 复用 collect_samples 的 features
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from collect_samples import features


def load():
    X, y, srcs = [], [], []
    # 1) LLM 标注（真标签，最高优先）
    fp = os.path.join(TRAIN_DIR, "llm_labels.jsonl")
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            r = d.get("role", "")
            if r not in ROLE_IDX:
                continue
            t = d.get("text", "")
            # LLM 标注去噪：ref_item 必须 "[数字]" 开头（qwen3.5 把"1. 研究背景"误标成 ref_item）
            if r == "ref_item" and not t.startswith("["):
                continue
            f = features(t)
            X.append([f[k] for k in FEAT_KEYS])
            y.append(ROLE_IDX[r])
            srcs.append("llm")
    # 2) 英文 arXiv（结构真标签）
    fp = os.path.join(TRAIN_DIR, "en_arxiv.jsonl")
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            r = d.get("role", "")
            if r not in ("heading1", "heading2", "body"):
                continue
            f = features(d.get("text", ""))
            X.append([f[k] for k in FEAT_KEYS])
            y.append(ROLE_IDX[r])
            srcs.append("arxiv")
    # 3) paper.edu.cn 元数据（标题/摘要/关键词——论文特有结构真标签）
    fp = os.path.join(TRAIN_DIR, "paperedu.jsonl")
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            r = d.get("role", "")
            if r not in ("heading1", "abstract_heading", "keywords"):
                continue
            t = d.get("text", "")
            if r == "abstract_heading" and len(t) < 30:
                continue
            if r == "keywords" and (t.startswith("关键词：关键词") or len(t) < 6):
                continue
            f = features(t)
            X.append([f[k] for k in FEAT_KEYS])
            y.append(ROLE_IDX[r])
            srcs.append("paperedu")
    # 4) 规则高置信（samples_balanced 中低置信段排除——只保留规则明确类）
    fp = os.path.join(TRAIN_DIR, "samples_balanced.jsonl")
    if os.path.exists(fp):
        for line in open(fp, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            r = d.get("role", "")
            if r not in ROLE_IDX:
                continue
            t = d.get("text", "")
            # 排除低置信段（digit_dot 短行——规则拿不准，避免镜像错误）
            if d.get("digit_dot") and len(t) <= 40 and r in ("heading1", "heading3"):
                continue
            f = features(t)
            X.append([f[k] for k in FEAT_KEYS])
            y.append(ROLE_IDX[r])
            srcs.append("rule")
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32), srcs


def main():
    X, y, srcs = load()
    n = len(y)
    print("合并样本: %d | 来源: %s" % (n, dict(Counter(srcs))))
    print("类别: %s" % dict(Counter(y.tolist())))

    import lightgbm as lgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    # 过滤样本 <2 的类（stratify 需要每类至少 2 条）
    from collections import Counter as _C
    cnt = _C(y.tolist())
    keep = [i for i in range(len(y)) if cnt[y[i]] >= 2]
    X, y = X[keep], y[keep]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.08,
                               num_leaves=15, max_depth=4, class_weight="balanced", verbose=-1)
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    names = [k for k, v in sorted(ROLE_IDX.items(), key=lambda x: x[1])]
    present = sorted(set(yte.tolist()))
    print("准确率: %.3f" % accuracy_score(yte, pred))
    print(classification_report(yte, pred, labels=present,
                                target_names=[names[i] for i in present],
                                zero_division=0, digits=2))

    # 关键测试：低置信段（规则/弱监督会判 heading1 的）
    tests = ["1. 研究背景", "1. 优点：效率高", "2. 缺点：成本较大",
             "1. 这里的数据来源于国家统计局：https://data.stats.gov.cn/",
             "2. 资料来源：教育部历年报告。", "（一）指导思想", "1. 引言"]
    from collect_samples import features as feat
    ROLES = [k for k, v in sorted(ROLE_IDX.items(), key=lambda x: x[1])]
    print("\n=== 低置信段测试（对比：规则=heading1） ===")
    for t in tests:
        f = feat(t)
        x = np.array([[f[k] for k in FEAT_KEYS]], dtype=np.float32)
        p = model.predict(x)[0]
        print("%-30s → %s" % (t, ROLES[p]))

    # ONNX 导出
    try:
        from onnxmltools.convert import convert_lightgbm
        from onnxmltools.convert.common.data_types import FloatTensorType
        import onnx
        onx = convert_lightgbm(model, initial_types=[("input", FloatTensorType([None, X.shape[1]]))],
                               target_opset=15)
        out = os.path.join(os.path.dirname(__file__), '..', 'engine', 'role_classifier.onnx')
        onnx.save_model(onx, out)
        print("\nONNX 已导出: %.1f KB" % (os.path.getsize(out) / 1024))
    except Exception as e:
        print("ONNX 导出失败:", repr(e))


if __name__ == "__main__":
    main()
