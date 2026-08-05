# -*- coding: utf-8 -*-
"""发布 v1.0.16：用 git 凭据里的 token 创建 GitHub release + 上传 exe"""
import subprocess, json, sys, urllib.request, urllib.error

REPO = 'huojian17-star/DocFormatTool'
TAG = 'v1.0.16'
EXE = r'dist\DocFormatTool.exe'

# 1) 从 git 凭据管理器提取 token（不打印）
cred = subprocess.run(['git', 'credential', 'fill'],
                      input='protocol=https\nhost=github.com\n\n',
                      capture_output=True, text=True, encoding='utf-8').stdout
token = None
for line in cred.splitlines():
    if line.startswith('password='):
        token = line[9:]
        break
if not token:
    print('FAIL: 无法从 git 凭据提取 token')
    sys.exit(1)
print('token 已提取（长度 %d，不显示内容）' % len(token))

def api(url, method='GET', data=None, raw=False):
    headers = {'Authorization': 'token ' + token,
               'Accept': 'application/vnd.github+json',
               'User-Agent': 'DocFormatTool-release'}
    if not raw:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(data).encode() if data is not None else None
    else:
        headers['Content-Type'] = 'application/octet-stream'
        body = data
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

# 2) 创建 release（若已存在则跳过创建）
code, body = api('https://api.github.com/repos/%s/releases' % REPO, 'POST',
                 {'tag_name': TAG, 'name': 'v1.0.16',
                  'body': 'v1.0.16：全新界面（AiNiee 风格侧边栏+卡片+吉祥物）+ 拖拽文件选入 + 鼠标滚轮滚动 + 窗口可最大化 + 一键排版固定底部 + 更新链路加固'})
if code == 201:
    rel = json.loads(body)
    print('release 创建 OK:', rel['html_url'])
elif code == 422:
    # 已存在：查已有 release 的 upload_url
    code, body = api('https://api.github.com/repos/%s/releases/tags/%s' % (REPO, TAG))
    rel = json.loads(body)
    print('release 已存在，复用:', rel.get('html_url'))
else:
    print('release 创建失败 code=%s: %s' % (code, body[:200]))
    sys.exit(1)

# 3) 上传 exe
upload_url = rel['upload_url'].split('{')[0]
with open(EXE, 'rb') as f:
    exe_data = f.read()
print('上传 exe: %.1f MB ...' % (len(exe_data) / 1048576))
code, body = api(upload_url + '?name=DocFormatTool.exe', 'POST', exe_data, raw=True)
if code in (201, 200):
    print('exe 上传 OK')
else:
    print('exe 上传失败 code=%s: %s' % (code, body[:300]))
    sys.exit(1)
print('DONE: v1.0.16 release 发布完成')
