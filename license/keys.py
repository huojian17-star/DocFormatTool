# -*- coding: utf-8 -*-
"""密钥系统（离线版）。

密钥：20 位字符（去易混淆 0O1lI），最后 1 位为校验位，
前 19 位含 4 段 4 字符 + 1 位产品代码，可带学校代号前缀便于管理。
生成端在卖家手里（gen_key_cli.py）；程序内只做校验 + 机器指纹绑定。
"""
import hashlib
import hmac
import os
import re
import time

# 去掉易混淆字符的字母数字表
ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
KEY_PATTERN = re.compile(r"^[23456789A-Z]{20}$")

# 产品代码：A=规范文档排版工具 v1（必须取自 ALPHABET，不能含 0/1/O/I）
PRODUCT_CODE = "A"

_ACT_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")),
                        "DocFormatTool")
_ACT_FILE = os.path.join(_ACT_DIR, "license.dat")

# 激活文件签名密钥（内嵌 exe，防小白用记事本伪造激活文件；
# 能防"改指纹"这类手改，防不了专业逆向——离线方案的可接受边界）
_SIGN_PARTS = ("Do", "cFo", "rmat", "Tool", "-v1-", "sig", "key")
_SIGN_KEY = "".join(_SIGN_PARTS)


def _sign(key: str, fp: str) -> str:
    """对 密钥+指纹 计算 HMAC 签名。"""
    return hmac.new(_SIGN_KEY.encode(), (key + "|" + fp).encode(),
                    hashlib.sha256).hexdigest()[:16]


def _checksum(body: str) -> str:
    """校验位：body 哈希后取模映射到字母表。"""
    n = int(hashlib.sha256(body.encode("utf-8")).hexdigest(), 16)
    return ALPHABET[n % len(ALPHABET)]


def is_valid_format(key: str) -> bool:
    """格式 + 校验位验证（不检查是否已使用）。"""
    key = (key or "").strip().upper()
    if not KEY_PATTERN.match(key):
        return False
    body, check = key[:19], key[19]
    return _checksum(body) == check


def save_activation(key: str, fp: str) -> str:
    """绑定激活：写入 %APPDATA%/DocFormatTool/license.dat（含防篡改签名）。"""
    os.makedirs(_ACT_DIR, exist_ok=True)
    stamp = int(time.time())
    with open(_ACT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(["DocFormatTool-v1", key, fp, str(stamp), _sign(key, fp)]))
    return _ACT_FILE


def check_activation(fp: str):
    """返回 (ok, reason)。
    ok=True: 已激活且指纹匹配且签名有效；
    否则 reason 说明（未激活 / 密钥无效 / 本机未授权 / 激活文件被篡改）。
    """
    if not os.path.exists(_ACT_FILE):
        return False, "未激活"
    try:
        with open(_ACT_FILE, encoding="utf-8") as f:
            lines = [l.strip() for l in f.read().splitlines()]
        if len(lines) < 3 or lines[0] != "DocFormatTool-v1":
            return False, "激活文件损坏"
        key, bound_fp = lines[1], lines[2]
        # 防篡改签名：签名缺失（旧版）或与内容不匹配 → 拒绝
        if len(lines) < 5 or lines[4] != _sign(key, bound_fp):
            return False, "激活信息校验失败，请重新激活"
        if not is_valid_format(key):
            return False, "密钥无效"
        if bound_fp != fp:
            return False, "本机未授权（激活信息与当前设备不匹配）"
        return True, "已激活"
    except Exception:
        return False, "激活文件无法读取"
