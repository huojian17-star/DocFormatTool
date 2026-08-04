# -*- coding: utf-8 -*-
"""抓取 arXiv 英文论文（ar5iv HTML 版）→ 按 HTML 结构直接打标（h2=heading1, h3=heading2, p=body）。
HTML 结构标签比规则更准（真标题），与 LLM 标注互补。用法: python arxiv_crawl.py [篇数]
"""
import os, sys, time, json, re, urllib.request

OUT = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data", "en_arxiv.jsonl")
UA = {'User-Agent': 'Mozilla/5.0 (research corpus collector; contact: dev@local)'}
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return opener.open(req, timeout=timeout).read().decode('utf-8', errors='ignore')


def get_arxiv_ids(n):
    """arXiv API 搜最近论文（跨领域）→ 返回 arxiv id 列表"""
    cats = ["cs.CL", "cs.AI", "cs.LG", "stat.ML", "econ.EM", "q-bio.GN", "physics.soc-ph"]
    ids = []
    for cat in cats[:3]:
        url = ("http://export.arxiv.org/api/query?search_query=cat:%s&start=0&max_results=%d"
               "&sortBy=submittedDate&sortOrder=descending" % (cat, max(3, n // 3)))
        xml = fetch(url)
        ids += re.findall(r'<id>http://arxiv.org/abs/([^<]+)</id>', xml)
        time.sleep(2)
    return ids


def parse_ar5iv(html):
    """解析 ar5iv HTML：标题层级 + 正文段落 → [(role, text)]"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    # 去掉导航/引用区
    for tag in soup.find_all(['nav', 'footer', 'script', 'style']):
        tag.decompose()
    items = []
    body = soup.find('body') or soup
    for el in body.find_all(['h1', 'h2', 'h3', 'p']):
        t = el.get_text(" ", strip=True)
        if not t or len(t) < 3:
            continue
        if el.name == 'h1':
            role = 'heading1'
        elif el.name == 'h2':
            role = 'heading1'  # ar5iv 的 h2 = 一级 section
        elif el.name == 'h3':
            role = 'heading2'  # h3 = 二级 section
        else:
            role = 'body'
            if len(t) < 30 or t[-1] not in '.?!':
                continue  # 短行非正文（表格碎片/公式）跳过
        items.append((role, t))
    return items


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    ids = get_arxiv_ids(n)
    print('arXiv 获取 %d 篇（前 %d 篇抓取）' % (len(ids), min(n, len(ids))))
    total = 0
    with open(OUT, 'a', encoding='utf-8') as f:
        for i, aid in enumerate(ids[:n]):
            try:
                html = fetch('https://ar5iv.labs.arxiv.org/html/' + aid, timeout=90)
                items = parse_ar5iv(html)
                if len(items) < 20:
                    print('  [%d/%d] %s 跳过（内容少 %d 段）' % (i + 1, n, aid, len(items)))
                    continue
                for role, t in items:
                    f.write(json.dumps({"text": t, "role": role, "src": "arxiv:%s" % aid},
                                       ensure_ascii=False) + "\n")
                    total += 1
                print('  [%d/%d] %s → %d 段' % (i + 1, n, aid, len(items)))
            except Exception as e:
                print('  [%d/%d] %s 失败: %r' % (i + 1, n, aid, e))
            time.sleep(1.5)
    print('完成：%d 篇，%d 段 → %s' % (min(n, len(ids)), total, OUT))


if __name__ == '__main__':
    main()
