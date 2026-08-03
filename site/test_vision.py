# -*- coding: utf-8 -*-
"""测本地 Ollama 视觉模型连通与速度。"""
import urllib.request, json, time, base64, sys, os

def gen(payload, timeout=120):
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    resp = json.load(urllib.request.urlopen(req, timeout=timeout))
    return time.time() - t0, resp.get("response", "")

# 1) 纯文本连通
t, r = gen({"model": "qwen3.5:latest", "prompt": "回复两个字：正常", "stream": False})
print("文本生成: %.1fs -> %r" % (t, r[:20]))

# 2) 带图（用户截图）
img = r"C:\Users\28253\AppData\Roaming\reasonix\global-workspace\.reasonix\attachments\clipboard-20260804-010545.429474-000023.png"
b64 = base64.b64encode(open(img, "rb").read()).decode()
t, r = gen({"model": "qwen3.5:latest",
            "prompt": "用一两句话描述这张截图里的文档排版问题",
            "images": [b64], "stream": False}, timeout=180)
print("图文生成: %.1fs -> %r" % (t, r[:100]))
