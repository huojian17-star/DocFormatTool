# -*- coding: utf-8 -*-
"""LaTeX 子集 → Word OMML（原生可编辑公式）。

覆盖工科论文常见公式：上下标、分数、根号、求和/积分带上下限、希腊字母、
常用符号（× ± ≤ ≥ → ≈ 等）。不支持的复杂结构退化为原样文本（Word 中仍可手改）。

OMML 命名空间：
  xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
"""
import re
from xml.sax.saxutils import escape

GREEK = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "epsilon": "\u03b5", "zeta": "\u03b6", "eta": "\u03b7", "theta": "\u03b8",
    "iota": "\u03b9", "kappa": "\u03ba", "lambda": "\u03bb", "mu": "\u03bc",
    "nu": "\u03bd", "xi": "\u03be", "pi": "\u03c0", "rho": "\u03c1",
    "sigma": "\u03c3", "tau": "\u03c4", "upsilon": "\u03c5", "phi": "\u03c6",
    "chi": "\u03c7", "psi": "\u03c8", "omega": "\u03c9",
    "Gamma": "\u0393", "Delta": "\u0394", "Theta": "\u0398", "Lambda": "\u039b",
    "Pi": "\u03a0", "Sigma": "\u03a3", "Phi": "\u03a6", "Psi": "\u03a8",
    "Omega": "\u03a9",
}
SYMBOLS = {
    "times": "\u00d7", "pm": "\u00b1", "mp": "\u2213", "leq": "\u2264",
    "geq": "\u2265", "neq": "\u2260", "approx": "\u2248", "equiv": "\u2261",
    "rightarrow": "\u2192", "leftarrow": "\u2190", "Rightarrow": "\u21d2",
    "infty": "\u221e", "cdot": "\u22c5", "ldots": "\u2026", "cdots": "\u22ef",
    "partial": "\u2202", "nabla": "\u2207", "forall": "\u2200", "exists": "\u2203",
    "in": "\u2208", "notin": "\u2209", "subset": "\u2282", "subseteq": "\u2286",
    "cup": "\u222a", "cap": "\u2229", "sin": "sin", "cos": "cos", "tan": "tan",
    "log": "log", "ln": "ln", "exp": "exp", "min": "min", "max": "max",
    "argmin": "argmin", "argmax": "argmax", "lim": "lim", "sum": "\u2211",
    "int": "\u222b", "prod": "\u220f",
}
_CMD_RE = re.compile(r"\\[a-zA-Z]+")
_GROUP_RE = re.compile(r"\{([^{}]*)\}")
_OPT_RE = re.compile(r"\[([^\[\]]*)\]")


def latex_to_omml(latex: str) -> str:
    """LaTeX 字符串 → OMML XML 字符串（<m:oMath> 内容片段，不含 <m:oMath> 包裹）。"""
    frag, _ = _parse(latex.strip())
    return frag


def _t(text: str) -> str:
    return '<m:r><m:t xml:space="preserve">%s</m:t></m:r>' % escape(text)


def _parse(s: str, i: int = 0, stop_at: str = "") -> tuple:
    """递归解析，返回 (omml片段, 新索引)。stop_at: 遇该字符停止（用于 { } 分组）。"""
    parts = []
    while i < len(s):
        c = s[i]
        if stop_at and c in stop_at:
            return "".join(parts), i
        if c == "\\":
            m = _CMD_RE.match(s, i)
            if m:
                cmd = m.group(0)
                i = m.end()
                name = cmd[1:]
                if name == "frac":
                    num, i = _parse_group(s, i)
                    den, i = _parse_group(s, i)
                    parts.append("<m:f><m:num>%s</m:num><m:den>%s</m:den></m:f>" % (num, den))
                elif name == "sqrt":
                    deg, i = _parse_opt(s, i)
                    e, i = _parse_group(s, i)
                    if deg:
                        parts.append("<m:rad><m:deg>%s</m:deg><m:e>%s</m:e></m:rad>" % (deg, e))
                    else:
                        parts.append("<m:rad><m:e>%s</m:e></m:rad>" % e)
                elif name in ("sum", "int", "prod"):
                    chr_map = {"sum": "\u2211", "int": "\u222b", "prod": "\u220f"}
                    sub = sup = ""
                    # 可选上下限
                    if name != "int" and i < len(s) and s[i] == "_":
                        sub, i = _parse_arg(s, i)
                    if name != "int" and i < len(s) and s[i] == "^":
                        sup, i = _parse_arg(s, i)
                    if name == "int" and i < len(s) and s[i] == "_":
                        sub, i = _parse_arg(s, i)
                    if name == "int" and i < len(s) and s[i] == "^":
                        sup, i = _parse_arg(s, i)
                    parts.append(
                        '<m:nary><m:naryPr><m:chr m:val="%s"/></m:naryPr>'
                        "<m:sub>%s</m:sub><m:sup>%s</m:sup><m:e>%s</m:e></m:nary>"
                        % (chr_map[name], sub, sup, _parse_until_end(s, i)))
                    return "".join(parts), len(s)
                elif name == "left" or name == "right":
                    # 括号类：忽略 \left \right，直接继续（下一字符是括号本身）
                    i += 1  # 跳过 '(' / ')' 等
                elif name in GREEK:
                    parts.append(_t(GREEK[name]))
                elif name in SYMBOLS:
                    parts.append(_t(SYMBOLS[name]))
                else:
                    parts.append(_t(cmd))
            else:
                parts.append(_t("\\"))
                i += 1
        elif c in "{}":
            i += 1
        elif c == "^":
            arg, i = _parse_arg(s, i)
            if parts:
                base = parts.pop()
                parts.append("<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>" % (base, arg))
        elif c == "_":
            arg, i = _parse_arg(s, i)
            if parts:
                base = parts.pop()
                parts.append("<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>" % (base, arg))
        else:
            parts.append(_t(c))
            i += 1
    return "".join(parts), i


def _parse_until_end(s: str, i: int) -> str:
    """解析到字符串末尾（nary 的基数内容）。"""
    frag, _ = _parse(s, i)
    return frag


def _parse_arg(s: str, i: int) -> tuple:
    """解析上标/下标参数：^{...} 或单字符/单命令。"""
    if i < len(s) and s[i] == "^":
        i += 1
    if i < len(s) and s[i] == "_":
        i += 1
    if i < len(s) and s[i] == "{":
        return _parse_group(s, i)
    if i < len(s) and s[i] == "\\":
        m = _CMD_RE.match(s, i)
        if m:
            frag, _ = _parse(m.group(0))
            return frag, m.end()
    if i < len(s) and s[i] not in "{}":
        return _t(s[i]), i + 1
    return "", i


def _parse_group(s: str, i: int) -> tuple:
    """解析 { ... } 分组，返回 (内部omml, 跳过 } 后的索引)。"""
    if i < len(s) and s[i] == "{":
        i += 1
    frag, i = _parse(s, i, stop_at="}")
    if i < len(s) and s[i] == "}":
        i += 1
    return frag, i


def _parse_opt(s: str, i: int) -> tuple:
    """解析可选参数 [ ... ]（如 \\sqrt[n] 的 [n]）。"""
    if i < len(s) and s[i] == "[":
        m = _OPT_RE.match(s, i)
        if m:
            frag, _ = _parse(m.group(1))
            return frag, m.end()
    return "", i
