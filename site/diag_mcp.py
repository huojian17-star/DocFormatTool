# -*- coding: utf-8 -*-
"""诊断 minimax MCP server 的 stdio 通信问题（非阻塞、有总超时）"""
import subprocess, json, time, os, threading, sys

SRV = r'thesis-format-tool\tools\mcp_vision_server.py'

def spawn():
    return subprocess.Popen(
        ['python', '-X', 'utf8', SRV],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=dict(os.environ))

def reader(stream, buf, tag):
    try:
        for line in stream:
            buf.append((tag, line))
    except Exception as e:
        buf.append((tag, 'EOF/ERR: %r' % e))

srv = spawn()
buf = []
t = threading.Thread(target=reader, args=(srv.stderr, buf, 'ERR'), daemon=True)
t.start()
time.sleep(1.5)
print('step1 进程存活:', srv.poll() is None)
print('step1 stderr:', [x[1][:200] for x in buf if x[0] == 'ERR'] or '(空)')

# initialize
srv.stdin.write((json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}}) + '\n').encode())
srv.stdin.flush()
t2 = threading.Thread(target=reader, args=(srv.stdout, buf, 'OUT'), daemon=True)
t2.start()
time.sleep(4)
outs = [x[1][:300] for x in buf if x[0] == 'OUT']
print('step2 initialize 4秒内 stdout:', outs or '(无响应!)')
print('step2 stderr 最新:', [x[1][:300] for x in buf if x[0] == 'ERR'] or '(空)')

srv.kill()
print('DONE')
