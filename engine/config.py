# -*- coding: utf-8 -*-
"""学校格式配置的加载与默认值。

每所学校一个 JSON 文件放 configs/ 下，缺省的键回落到 DEFAULT 里的值。
DEFAULT 本身取自 configs/_example.json（模板制草稿样式名固定，勿改样式键）。
"""
import json
import os

_CONFIGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")

DEFAULT = {
    "school": "示例大学",
    "page": {
        "paper": "A4",
        "margins_cm": {"top": 2.5, "bottom": 2.5, "left": 3.0, "right": 2.5},
    },
    "fonts": {
        # 中文字体名（eastAsia）与西文字体名
        "body": {"cn": "宋体", "en": "Times New Roman", "size_pt": 12},
        "heading1": {"cn": "黑体", "en": "Times New Roman", "size_pt": 16, "bold": True},
        "heading2": {"cn": "黑体", "en": "Times New Roman", "size_pt": 14, "bold": True},
        "heading3": {"cn": "黑体", "en": "Times New Roman", "size_pt": 12, "bold": True},
        "caption": {"cn": "宋体", "en": "Times New Roman", "size_pt": 10.5},
        "header": {"cn": "宋体", "en": "Times New Roman", "size_pt": 9},
        "table": {"cn": "宋体", "en": "Times New Roman", "size_pt": 10.5},
    },
    "paragraph": {
        "line_spacing": 1.5,            # 1.0 / 1.5 / 2.0
        "first_line_indent_chars": 2,   # 正文首行缩进（字符）
        "space_before_pt": 0,
        "space_after_pt": 0,
        "align": "justify",             # justify | left
    },
    # 草稿模板中的样式名 -> 含义（模板制，样式键固定）
    "styles": {
        "instructions": "使用说明",        # 模板第一页的使用说明，输出时整段删除
        "cover_title": "封面题目",          # 封面大标题（论文题目）
        "cover_field": "封面字段",          # 封面上的每行信息（姓名/学号/专业…）
        "abstract_heading": "摘要标题",
        "abstract_body": "摘要正文",
        "keywords": "关键词",
        "toc_placeholder": "目录占位",
        "toc_heading": "目录标题",
        "heading1": "标题 1",
        "heading2": "标题 2",
        "heading3": "标题 3",
        "body": "正文",
        "figure_caption": "图题注",
        "table_caption": "表题注",
        "ref_heading": "参考文献标题",
        "ref_item": "参考文献条目",
    },
    "cover": {
        "enabled": True,
        "title_text": "本科毕业论文（设计）",
        "title_size_pt": 26,
        "line_spacing": 1.5,
    },
    "abstract": {
        "heading_text": "摘  要",
        "keywords_label": "关键词：",
        "keywords_sep": "；",
    },
    "toc": {
        "heading_text": "目  录",
        "levels": 3,
        "need_refresh_note": True,   # 输出后提示在 Word 中更新域
    },
    "header_footer": {
        "header_text": "",
        "header_align": "center",     # center | left | right
        "footer_style": "center",     # center | right
        "front_matter": "roman",      # 前置部分页码：roman | none
        "body_start": "arabic",       # 正文页码：arabic | decimal
    },
    # 页码结构（学生可在 GUI 高级选项调整，消除机器猜测）
    "page_numbering": {
        "front_matter": "none",       # 封面/摘要/目录部分页码：none(无) | roman(罗马) | decimal
        "body_start": 1,              # 正文页码起始值（正文重新从该数字编号）
    },
    # 目录：中文论文标配；生成 TOC 域，Word 打开后 Ctrl+A → F9 刷新
    "toc": {
        "enabled": False,             # 是否自动插入目录（各模板按需开启）
        "heading_text": "目  录",
        "levels": 3,
    },
    "captions": {
        "figure": "图{chapter}-{num}",
        "table": "表{chapter}-{num}",
    },
    "references": {
        "heading_text": "参考文献",
    },
    "headings": {
        "numbering": True,            # 标题自动编号（章-节-小节）
    },
}


def load(school_key: str) -> dict:
    """按 configs/<school_key>.json 加载配置，与默认值深合并。"""
    path = os.path.join(_CONFIGS_DIR, school_key + ".json")
    if not os.path.exists(path):
        raise FileNotFoundError("未找到学校配置: %s" % path)
    with open(path, encoding="utf-8") as f:
        user = json.load(f)
    return _deep_merge(_deep_copy(DEFAULT), user)


def load_path(path: str) -> dict:
    """直接按文件路径加载配置。"""
    if not os.path.exists(path):
        raise FileNotFoundError("未找到学校配置: %s" % path)
    with open(path, encoding="utf-8") as f:
        user = json.load(f)
    return _deep_merge(_deep_copy(DEFAULT), user)


def list_schools() -> list:
    """列出 configs/ 下可用的学校键。"""
    out = []
    for name in sorted(os.listdir(_CONFIGS_DIR)):
        if name.endswith(".json") and not name.startswith("_"):
            out.append(name[:-5])
    return out


def list_presets() -> list:
    """列出内置通用模板（configs/presets/*.json），返回 (id, 名称) 列表。"""
    out = []
    presets_dir = os.path.join(_CONFIGS_DIR, "presets")
    if not os.path.isdir(presets_dir):
        return out
    for name in sorted(os.listdir(presets_dir)):
        if not name.endswith(".json"):
            continue
        pid = name[:-5]
        try:
            with open(os.path.join(presets_dir, name), encoding="utf-8") as f:
                title = json.load(f).get("school", pid)
        except Exception:
            title = pid
        out.append((pid, title))
    return out


def load_preset(preset_id: str) -> dict:
    """加载内置通用模板配置。"""
    path = os.path.join(_CONFIGS_DIR, "presets", preset_id + ".json")
    if not os.path.exists(path):
        raise FileNotFoundError("未找到内置模板: %s" % preset_id)
    with open(path, encoding="utf-8") as f:
        return _deep_merge(_deep_copy(DEFAULT), json.load(f))


def merge_default(cfg: dict) -> dict:
    """把一份不完整的配置（如模板分析结果）与默认配置深合并，缺省回落默认值。"""
    return _deep_merge(_deep_copy(DEFAULT), cfg)


def _deep_copy(d):
    import copy
    return copy.deepcopy(d)


def _deep_merge(base, override):
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
    return base
