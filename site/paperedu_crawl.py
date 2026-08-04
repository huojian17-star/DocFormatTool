# -*- coding: utf-8 -*-
"""抓取 paper.edu.cn（中国科技论文在线）首发论文详情页：摘要+关键词 → 训练真标签。
只抓 HTML 元数据（不下载 PDF），小批量礼貌限速。用法: python paperedu_crawl.py [篇数]
"""
import os, sys, time, json, re, urllib.request

OUT = os.path.join(os.path.expanduser("~"), ".DocFormatTool", "train_data", "paperedu.jsonl")
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return opener.open(req, timeout=timeout).read().decode('utf-8', errors='ignore')


def extract_meta(html):
    """提取 标题/摘要/关键词（HTML 页有，正文是 PDF 无结构）"""
    body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
    body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', '\n', body)
    body = re.sub(r'&nbsp;', ' ', body)
    lines = [l.strip() for l in body.split('\n') if l.strip()]
    title = re.search(r'<title>([^<]+)</title>', html)
    title = title.group(1).split('，')[0] if title else ''
    # 用 HTML 正则直接抓"摘要：/关键词："后的内容（页面多标签区，正则取正文区首个）
    abstract = ''
    m = re.search(r'摘要[：:]\s*(.{20,800}?)(?:关键词|</|$)', html, re.S)
    if m:
        abstract = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        abstract = re.sub(r'\s+', '', abstract)
    keywords = ''
    m = re.search(r'关键词[：:]\s*(.{2,300}?)(?:导出|</|作者|$)', html, re.S)
    if m:
        keywords = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        keywords = re.sub(r'\s+', '', keywords).rstrip(';；')
    return title, abstract, keywords


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    # 列表页 → 详情链接
    list_html = fetch('https://www.paper.edu.cn/releasepaper/index.shtml')
    links = re.findall(r'href="([^"]*releasepaper/content/[0-9-]+)"', list_html)
    full = list(dict.fromkeys('https://www.paper.edu.cn' + l if l.startswith('/') else l for l in links))
    print('列表发现 %d 篇' % len(full))
    saved = 0
    with open(OUT, 'a', encoding='utf-8') as f:
        for i, url in enumerate(full[:n]):
            try:
                html = fetch(url)
                title, abstract, keywords = extract_meta(html)
                if not title:
                    continue
                # 标题 → heading1 真标签（论文题目）
                f.write(json.dumps({"text": title, "role": "heading1", "src": "paperedu"}, ensure_ascii=False) + "\n")
                # 摘要 → abstract_heading 真标签（"摘要：内容"整行）
                if abstract and len(abstract) > 30:
                    f.write(json.dumps({"text": "摘要：" + abstract, "role": "abstract_heading", "src": "paperedu"},
                                       ensure_ascii=False) + "\n")
                # 关键词 → keywords 真标签
                if keywords:
                    f.write(json.dumps({"text": "关键词：" + keywords, "role": "keywords", "src": "paperedu"},
                                       ensure_ascii=False) + "\n")
                saved += 1
                if i % 5 == 0:
                    print('  [%d/%d] %s' % (i + 1, len(full[:n]), title[:24]))
            except Exception as e:
                print('  [%d] 失败: %r' % (i + 1, e))
            time.sleep(1.2)  # 礼貌限速
    print('完成：%d 篇 → %s' % (saved, OUT))


if __name__ == '__main__':
    main()
