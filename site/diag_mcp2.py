# -*- coding: utf-8 -*-
"""端到端验证：无环境变量场景下 server 仍能正常看图（fallback 注册表 key）"""
import subprocess, json, time, os, threading

SRV = r'thesis-format-tool\tools\mcp_vision_server.py'

# 故意不传 MINIMAX_API_KEY（模拟宿主进程环境里没有）
env = {k: v for k, v in os.environ.items() if k != 'MINIMAX_API_KEY'}
srv = subprocess.Popen(
    ['python', '-X', 'utf8', SRV],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

def reader(stream, buf, tag):
    try:
        for line in stream:
            buf.append((tag, line))
    except Exception:
        pass

buf = []
t = threading.Thread(target=reader, args=(srv.stderr, buf, 'ERR'), daemon=True)
t.start()
time.sleep(1.5)
print('启动日志:', [x[1].strip()[:100] for x in buf if x[0] == 'ERR'])

def send(obj):
    srv.stdin.write((json.dumps(obj) + '\n').encode()); srv.stdin.flush()
    out = []
    tt = threading.Thread(target=lambda: out.append(srv.stdout.readline()), daemon=True)
    tt.start(); tt.join(30)
    return out[0] if out else None

r = send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}})
print('initialize:', 'OK' if r else '超时!')

t0 = time.time()
r = send({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': {
    'name': 'see_image',
    'arguments': {'path': r'thesis-format-tool\gui_expanded.png', 'question': '底部按钮完整吗？一句话'}}})
if r:
    res = json.loads(r)['result']
    print('see_image 耗时 %.1fs: %r' % (time.time() - t0, res['content'][0]['text'][:60]))
else:
    print('see_image 超时!')
srv.kill()
print('DONE')
