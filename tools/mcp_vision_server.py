# -*- coding: utf-8 -*-
"""MiniMax 视觉 MCP 服务器（stdio，无第三方依赖）。

协议：MCP stdio transport = 逐行 JSON-RPC 2.0。
工具：see_image —— 传图片路径+问题，调 MiniMax-M3 视觉模型返回描述。

环境变量：MINIMAX_API_KEY（必填）、MINIMAX_API_HOST（可选，默认 https://api.minimaxi.com）
"""
import base64
import json
import os
import sys
import urllib.request

API_HOST = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com").rstrip("/")
API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MODEL = os.environ.get("MINIMAX_VISION_MODEL", "MiniMax-M3")

TOOL_DEF = {
    "name": "see_image",
    "description": "用 MiniMax 视觉模型看图并回答问题。输入本地图片路径（或 http(s) URL）和问题，返回 AI 的视觉描述/分析。适合：检查截图排版效果、看图识别内容、分析界面布局等。",
    "inputSchema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "本地图片路径（jpg/png/gif/webp，≤10MB）或 http(s) 图片 URL"},
            "question": {"type": "string", "description": "想问图片的问题，越具体越好"},
            "detail": {"type": "string", "enum": ["low", "default", "high"], "description": "解析分辨率（默认 default；文字密集用 high 更准但更贵）"},
        },
        "required": ["path", "question"],
    },
}


def _image_data_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not os.path.isfile(path):
        raise RuntimeError("图片文件不存在: %s" % path)
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(ext, "jpeg")
    if os.path.getsize(path) > 10 * 1024 * 1024:
        raise RuntimeError("图片超过 10MB: %s" % path)
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return "data:image/%s;base64,%s" % (mime, b64)


def _call_minimax(path: str, question: str, detail: str = "default") -> str:
    if not API_KEY:
        return "错误：未设置 MINIMAX_API_KEY 环境变量（在 MiniMax 开放平台 api.minimaxi.com 注册获取）"
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": _image_data_url(path), "detail": detail}},
                {"type": "text", "text": question},
            ],
        }],
        "max_tokens": 2048,
    }
    req = urllib.request.Request(
        API_HOST + "/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def _handle(method: str, params: dict):
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "minimax-vision", "version": "1.0.0"},
        }
    if method == "tools/list":
        return {"tools": [TOOL_DEF]}
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        if name != "see_image":
            return {"content": [{"type": "text", "text": "未知工具: %s" % name}], "isError": True}
        try:
            result = _call_minimax(args.get("path", ""), args.get("question", ""), args.get("detail", "default"))
            return {"content": [{"type": "text", "text": result}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": "调用失败: %s" % e}], "isError": True}
    return {"content": [{"type": "text", "text": "未支持方法: %s" % method}], "isError": True}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = msg.get("id")
        method = msg.get("method")
        if method == "notifications/initialized":
            continue
        result = _handle(method, msg.get("params", {}) or {})
        if mid is not None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": result}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
