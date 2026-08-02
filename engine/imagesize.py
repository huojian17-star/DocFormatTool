# -*- coding: utf-8 -*-
"""轻量图片尺寸读取（PNG/JPEG/GIF/BMP），零依赖。

替代 PIL：只为读取图片宽高做自适应缩放，不值得为它打包进 150MB 的 Pillow。
"""
import struct


def image_size(path: str):
    """返回 (width_px, height_px)，失败返回 None。"""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", head[16:24])
            return w, h
        if head[:6] in (b"GIF87a", b"GIF89a"):
            w, h = struct.unpack("<HH", head[6:10])
            return w, h
        if head[:2] == b"BM":
            with open(path, "rb") as f:
                f.seek(18)
                d = f.read(8)
            w, h = struct.unpack("<ii", d)
            return abs(w), abs(h)
        if head[:2] == b"\xff\xd8":
            return _jpeg_size(path)
    except Exception:
        return None
    return None


def _jpeg_size(path: str):
    """扫描 JPEG SOF 段读取宽高。"""
    try:
        with open(path, "rb") as f:
            f.seek(2)
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                marker = f.read(1)
                if not marker:
                    return None
                if marker == b"\xd8":  # SOI
                    continue
                if marker in (b"\xda", b"\xd9"):  # SOS / EOI
                    return None
                seg = f.read(2)
                if len(seg) < 2:
                    return None
                seg_len = int.from_bytes(seg, "big")
                if marker in (b"\xc0", b"\xc1", b"\xc2", b"\xc3",
                              b"\xc5", b"\xc6", b"\xc7", b"\xc9",
                              b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"):
                    data = f.read(5)
                    if len(data) < 5:
                        return None
                    h = int.from_bytes(data[:2], "big")
                    w = int.from_bytes(data[2:4], "big")
                    return w, h
                f.seek(seg_len - 2, 1)
    except Exception:
        return None
    return None
