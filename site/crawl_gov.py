# -*- coding: utf-8 -*-
"""爬取中国政府网（gov.cn）公文正文 → txt，供 ONNX 分类器训练。
用法: python crawl_gov.py [篇数]
"""
import re, os, sys, time, urllib.request

OUT_DIR = r'F:\论文排版工具_测试包\训练语料\gov'
os.makedirs(OUT_DIR, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')


def extract_article(html):
    """从 gov.cn 详情页 HTML 提取正文文本（尝试多个正文容器）。"""
    # 容器候选（gov.cn 常见结构）
    for pat in [
        r'<div[^>]*class="[^"]*pages_content[^"]*"[^>]*>(.*?)</div>\s*<!--',
        r'<div[^>]*id="UCAP-CONTENT"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
    ]:
        m = re.search(pat, html, re.S)
        if m:
            body = m.group(1)
            # 去掉 HTML 标签
            body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
            body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
            body = re.sub(r'<[^>]+>', '\n', body)
            body = re.sub(r'&nbsp;', ' ', body)
            body = re.sub(r'&[a-z]+;', '', body)
            lines = [ln.strip() for ln in body.split('\n') if ln.strip()]
            return '\n'.join(lines)
    return ''


def main():
    n_max = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    # 1) 国务院文件列表页（静态 HTML，含 content 链接）→ 提取详情链接
    list_html = fetch('https://www.gov.cn/zhengce/xxgk/')
    links = re.findall(r'href="([^"]*content_\d+\.htm[^"]*)"', list_html)
    # 只保留政策正文页（排除 home/ 导航页脚）
    links = [l for l in links if '/zhengce/' in l and not l.startswith('https://www.gov.cn/home')]
    # 归一化相对链接
    full = []
    for l in links:
        l = l.replace('./', '')
        if l.startswith('/'):
            full.append('https://www.gov.cn' + l)
        elif l.startswith('zhengce'):
            full.append('https://www.gov.cn/' + l)
        else:
            full.append(l)
    full = list(dict.fromkeys(full))  # 去重保序
    print('列表页发现 %d 篇公文' % len(full))

    # 2) 逐篇抓正文
    saved = 0
    for i, url in enumerate(full[:n_max]):
        try:
            html = fetch(url)
            art = extract_article(html)
            if len(art) < 500:
                print('  [跳过] 正文过短 %s' % url.split('/')[-1])
                continue
            # 文件名：标题前 20 字
            title = re.search(r'<title>([^<]+)</title>', html)
            name = (title.group(1).split('_')[0] if title else 'gov_%d' % i)[:20]
            name = re.sub(r'[\\/:*?"<>|]', '', name)
            fp = os.path.join(OUT_DIR, '%s.txt' % name)
            if os.path.exists(fp):
                continue
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(art)
            saved += 1
            print('  [%d/%d] %s (%d 字)' % (i + 1, min(n_max, len(full)), name, len(art)))
        except Exception as e:
            print('  [失败] %s: %r' % (url, e))
        time.sleep(1.0)  # 礼貌限速
    print('完成：保存 %d 篇 → %s' % (saved, OUT_DIR))


if __name__ == '__main__':
    main()
