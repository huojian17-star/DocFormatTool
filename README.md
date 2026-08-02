# DocFormatTool —— 论文格式一键排版引擎

把任意格式的论文（Word / Markdown / 纯文本）排成符合规范要求的 Word 文档。
这是**引擎核心**部分（公开引流版）：模板格式自动分析、文档结构识别、改写式排版、Markdown 增强、自动质检。

> 注：本仓库仅包含排版引擎。学生端 GUI 与授权/密钥系统为商业部分，不在此公开。

## 能力一览

- **任意学校模板自适应**：上传学校下发的 Word 模板，自动解析其格式规则（字体/字号/页边距/标题层级），生成格式配置
- **改写式排版**：不改内容（图片/表格/公式/超链接 100% 保留），只规范化格式；遇到异常文档自动记录错误日志
- **任意输入**：.docx（改写式）/ .md（Typora 等，含表格/代码块/图片/公式）/ .txt
- **Markdown 增强**（工科友好）：
  - md 表格 → Word 带框表格
  - 代码块 → Consolas 等宽 + 浅灰背景 + 固定小五号
  - LaTeX 公式（`$$...$$`）→ Word 原生可编辑公式（OMML）
  - 图片自动缩放适配页边距、题注编号保留（图3-1 不重复编号）
- **保守结构识别**：章节标题（编号/中文编号/格式特征）、摘要、关键词、参考文献、图/表题注；自动跳过文档自带目录页
- **自动质检**：排版后体检字体/字号/页面/内容保留，输出 PASS/FAIL 报告
- **页码结构**：前置部分（封面/摘要）无页码或罗马数字，正文从指定值起编

## 技术栈

Python 3 + python-docx + lxml（零其他运行时依赖）

## 快速开始

```bash
# 分析学校模板，生成格式配置
python run_pipeline.py 论文.md 学校模板.docx --save-config configs/xxx.json

# 用内置通用模板排版
python run_pipeline.py 论文.md --preset bachelor_cn -o 输出.docx

# 自动体检排版输出
python tools/validate.py 输出.docx 原文档.docx --preset bachelor_cn

# 批量回归：全部内置模板 × 输入文档
python tools/regression.py 论文1.docx 论文2.md
```

内置通用模板（`configs/presets/`）：本科毕业论文通用、研究生学位论文通用、中文核心期刊（双栏）、IEEE、ACM、APA 7th。

## 目录结构

```
engine/           排版引擎核心
  ├── analyze.py  模板格式分析器
  ├── infer.py    文档结构识别
  ├── build_docx.py  改写式排版 + 从零生成
  ├── omml.py     LaTeX → Word 原生公式
  ├── imagesize.py 零依赖图片尺寸读取
  └── ...
configs/presets/  内置通用模板
tools/            配套工具（分析/体检/回归）
run_pipeline.py   CLI 入口
```

## 许可

仅供学习交流使用。请勿用于商业盈利或侵权用途。
