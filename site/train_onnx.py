# -*- coding: utf-8 -*-
"""ONNX 分类器训练：特征(20维) → LightGBM 多分类 → ONNX 导出。
弱监督数据来自 collect_samples.py + 弹窗人工确认（uncertain_labels.jsonl）。
评估交叉验证准确率，达标后导出 onnx 供 exe 推理。
"""
import os, sys, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np

TRAIN_DIR = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data")
MODEL_OUT = os.path.join(os.path.dirname(__file__), '..', 'engine', 'role_classifier.onnx')

ROLE_IDX = {"heading1": 0, "heading2": 1, "heading3": 2, "body": 3,
            "abstract_heading": 4, "keywords": 5, "ref_heading": 6, "ref_item": 7,
            "caption": 8, "appendix": 9}
IDX_ROLE = {v: k for k, v in ROLE_IDX.items()}
FEAT_KEYS = ["len", "ends_punct", "has_url", "has_ref_type", "has_note_word",
             "num_h3", "num_h2", "num_h1", "cn_num", "paren_cn",
             "paren_digit", "digit_space", "digit_dot", "md_hash",
             "abstract", "keywords", "ref_head", "appendix", "first_char_verb"]


def load_samples():
    X, y, texts = [], [], []
    files = [os.path.join(TRAIN_DIR, "samples_balanced.jsonl"),
             os.path.join(TRAIN_DIR, "uncertain_labels.jsonl")]
    for fp in files:
        if not os.path.exists(fp):
            continue
        for line in open(fp, encoding="utf-8"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            role = d.get("role", "")
            if role not in ROLE_IDX:
                continue
            vec = [float(d.get(k, 0)) for k in FEAT_KEYS]
            X.append(vec)
            y.append(ROLE_IDX[role])
            texts.append(d.get("text", ""))
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32), texts


def main():
    X, y, texts = load_samples()
    n = len(y)
    if n < 100:
        print("样本不足（%d），先积累数据" % n)
        return
    print("样本: %d | 特征: %d | 类别: %d" % (n, X.shape[1], len(ROLE_IDX)))

    import lightgbm as lgb
    # 类别不平衡权重
    from collections import Counter
    cnt = Counter(y.tolist())
    w = np.array([n / (len(cnt) * cnt.get(i, 1)) for i in range(len(ROLE_IDX))], dtype=np.float64)

    # 交叉验证评估
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import accuracy_score, f1_score, classification_report
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    accs, f1s = [], []
    for tr, te in skf.split(X, y):
        model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.08,
                                   num_leaves=15, max_depth=4,
                                   class_weight="balanced", verbose=-1)
        model.fit(X[tr], y[tr])
        pred = model.predict(X[te])
        accs.append(accuracy_score(y[te], pred))
        f1s.append(f1_score(y[te], pred, average="macro"))
    print("5折交叉验证: 准确率 %.3f | macro-F1 %.3f" % (np.mean(accs), np.mean(f1s)))

    # 全量训练 + ONNX 导出
    model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.08,
                               num_leaves=15, max_depth=4,
                               class_weight="balanced", verbose=-1)
    model.fit(X, y)
    print("类别: %d | 每类样本: %s" % (len(cnt), dict(cnt)))

    # ONNX 导出（onnxmltools 新版 float16 转换路径变动，模型 <1MB 无需量化，直接用 float32）
    try:
        from onnxmltools.convert import convert_lightgbm
        from onnxmltools.convert.common.data_types import FloatTensorType
        import onnx
        init_types = [("input", FloatTensorType([None, X.shape[1]]))]
        onx = convert_lightgbm(model, initial_types=init_types, target_opset=15)
        onnx.save_model(onx, MODEL_OUT)
        print("ONNX 已导出: %s (%.1f KB)" % (MODEL_OUT, os.path.getsize(MODEL_OUT) / 1024))
    except Exception as e:
        print("ONNX 导出失败: %r" % e)
        # 兜底：joblib
        import joblib
        joblib.dump(model, MODEL_OUT + ".pkl")
        print("已存 joblib 备份")

    # 特征重要性
    imp = sorted(zip(FEAT_KEYS, model.feature_importances_), key=lambda x: -x[1])
    print("Top 特征:", ", ".join("%s(%d)" % (k, v) for k, v in imp[:8]))


if __name__ == "__main__":
    main()
