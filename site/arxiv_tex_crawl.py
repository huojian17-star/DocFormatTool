# -*- coding: utf-8 -*-
"""arXiv TeX 源抓取：\section/\subsection → 标题层级，段落 → body。
用法: python arxiv_tex_crawl.py [篇数]"""
import os, sys, time, json, re, tarfile, io, urllib.request, zipfile

OUT = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data", "en_arxiv.jsonl")
UA = {'User-Agent': 'Mozilla/5.0 (research; contact: dev@local)'}
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    return opener.open(req, timeout=timeout).read()


def get_ids(n):
    ids = []
    for cat in ["cs.CL", "cs.AI", "cs.LG", "stat.ML"]:
        url = ("http://export.arxiv.org/api/query?search_query=cat:%s&start=0&max_results=%d"
               "&sortBy=submittedDate&sortOrder=descending" % (cat, max(3, n // 2)))
        xml = fetch(url).decode('utf-8', errors='ignore')
        ids += re.findall(r'<id>http://arxiv.org/abs/([^<]+)</id>', xml)
        time.sleep(2)
    # 优先旧论文（TeX 稳定），去重
    seen, out = set(), []
    for i in ids:
        base = i.split('v')[0]
        if base not in seen:
            seen.add(base)
            out.append(base)
    return out


def parse_tex(tex):
    """TeX → [(role, text)]。\section=H1, \subsection=H2, \subsubsection=H3, 段落=body。"""
    items = []
    # 去注释（行首 %）
    tex = re.sub(r'(?m)^%.*$', '', tex)
    # 提取 section 标题
    for m in re.finditer(r'\\(?:section|chapter)\*?\{(.+?)\}', tex, re.S):
        t = clean_tex(m.group(1))
        if t and len(t) < 200:
            items.append(('heading1', t))
    for m in re.finditer(r'\\subsection\*?\{(.+?)\}', tex, re.S):
        t = clean_tex(m.group(1))
        if t and len(t) < 200:
            items.append(('heading2', t))
    for m in re.finditer(r'\\subsubsection\*?\{(.+?)\}', tex, re.S):
        t = clean_tex(m.group(1))
        if t and len(t) < 200:
            items.append(('heading3', t))
    # 正文段落：去掉 section 标题和命令块，按空行分段
    body_tex = re.sub(r'\\(?:section|subsection|subsubsection|chapter)\*?\{.*?\}', ' ', tex, flags=re.S)
    body_tex = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', ' ', body_tex, flags=re.S)  # 环境
    body_tex = re.sub(r'\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?', ' ', body_tex)
    body_tex = body_tex.replace('\\%', '%').replace('\\&', '&')
    for para in re.split(r'\n\s*\n', body_tex):
        t = clean_tex(para)
        if len(t) >= 40 and t[-1] in '.?!):;”"':
            items.append(('body', t))
    return items


def clean_tex(s):
    s = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?', ' ', s)  # 命令
    s = re.sub(r'[${}~^_]', ' ', s)
    s = re.sub(r'\\[%&#]', lambda m: m.group(0)[1], s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    ids = get_ids(n)
    print('获取 %d 篇（抓取前 %d 篇）' % (len(ids), min(n, len(ids))))
    total = 0
    with open(OUT, 'a', encoding='utf-8') as f:
        for i, aid in enumerate(ids[:n]):
            try:
                raw = fetch('https://export.arxiv.org/e-print/' + aid)
                # 解包 tar.gz / zip / 裸 tex
                tex = None
                if raw[:2] == b'\x1f\x8b':
                    try:
                        tf = tarfile.open(fileobj=io.BytesIO(raw))
                        for m in tf.getmembers():
                            if m.name.endswith('.tex') and not m.name.startswith('.'):
                                tex = tf.extractfile(m).read().decode('utf-8', errors='ignore')
                                break
                    except Exception:
                        pass
                elif raw[:2] == b'PK':
                    try:
                        zf = zipfile.ZipFile(io.BytesIO(raw))
                        for m in zf.namelist():
                            if m.endswith('.tex'):
                                tex = zf.read(m).decode('utf-8', errors='ignore')
                                break
                    except Exception:
                        pass
                else:
                    tex = raw.decode('utf-8', errors='ignore')
                if not tex or len(tex) < 2000:
                    print('  [%d/%d] %s 无 TeX' % (i + 1, n, aid))
                    continue
                items = parse_tex(tex)
                if len(items) < 15:
                    print('  [%d/%d] %s 段落少(%d)' % (i + 1, n, aid, len(items)))
                    continue
                for role, t in items:
                    f.write(json.dumps({"text": t, "role": role, "src": "arxiv:%s" % aid},
                                       ensure_ascii=False) + "\n")
                    total += 1
                print('  [%d/%d] %s → %d 段' % (i + 1, n, aid, len(items)))
            except Exception as e:
                print('  [%d/%d] %s 失败: %r' % (i + 1, n, aid, e))
            time.sleep(1.0)
    print('完成：%d 段 → %s' % (total, OUT))


if __name__ == '__main__':
    main()
