---
tags: [ONNX, 智能识别, 训练]
created: 2026-08-05
---

# 07-ONNX训练

## 目标

段落角色分类器（heading1/2/3/body/abstract/keywords/ref_item/caption/footer 等 9 类），打进 exe 离线运行，补充规则引擎的低置信段落判断。

## 管线（已通）

1. **采集**：`site/collect_samples.py` — docx/txt/md 段落 → 19 维特征 + 标签
   - 特征：长度、句号结尾、编号模式（digit_dot/cn_num/paren_cn/md_hash...）、引用类型、首字符等
2. **数据源**：
   - 规则弱监督（classify 输出当标签，13 万条——法律语料 `Duyu/Chinese_Law` 19.8MB 章/节/条结构）
   - LLM 机器标注（qwen3.5:latest + think=False，中文角色名归一化，3700 条）
   - arXiv 英文论文（TeX 结构真标签，2179 条）
   - paper.edu.cn 论文元数据（标题/摘要/关键词，144 条 → 摘要/关键词 F1 从 0 到 1.0）
3. **训练**：`site/train_merge.py` — LightGBM 多分类 → ONNX 导出 `engine/role_classifier.onnx`（1.7MB）
   - 5 折交叉验证准确率 ~0.84（小类少拉低 macro-F1）
4. **推理**：onnxruntime（已装）

## ⚠️ 核心结论（诚实版）

**弱监督 ML 只是规则的镜像**——标签来自规则 classify，ML 学到的就是规则的判断（含规则的错误：`1. xxx`→heading1、脚注/列举照样误判），**无法超越规则**。

超越规则需要两样（当前都没够）：
1. **人工标注**：弹窗确认数据 `~/.DocFormatTool/train_data/uncertain_labels.jsonl`（用户每确认一条 = 一条真标签）——量到几千条才有用
2. **上下文特征**（前后段落——（一）的层级要靠前文"一、"）

## 现状

- **ML 分类器暂不上生产**（准确率不如规则 + 上下文调整）
- 数据积累管道已就位（弹窗自动存标注），等真实标注积累后再训第二版
- 用户建议：网上搜样本（不限于论文——公文/企业文件都行），已采集 gov.cn 11 篇 + 法律语料

## 相关文件

- `site/collect_samples.py` / `site/train_onnx.py` / `site/train_merge.py` / `site/llm_label.py`
- `engine/role_classifier.onnx`（模型产物）
- `F:\论文排版工具_测试包\训练语料\`（语料库）
