# -*- coding: utf-8 -*-
"""用本地 Ollama（qwen3.5）给段落做机器标注——验证能否超越规则（区分标题/列举/脚注）"""
import json, urllib.request

OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:latest"

SYSTEM = """你是文档结构标注助手。判断每个段落属于哪种角色，只输出 JSON：{"role": "..."}
可选角色：heading1(一级标题，如"一、xxx"/"第一章 xxx"/"1 xxx")、heading2(二级标题"1.1 xxx"/"（一）xxx")、
heading3(三级标题"1.1.1 xxx"/"1. xxx")、body(正文段落)、ref_item(参考文献条目"[1] xxx")、
keywords(关键词行"关键词：xxx")、abstract_heading(摘要标题)、caption(图表题注)。
判断要点：标题=短行+编号+无句号结尾；列举=编号后是短语(如"1. 优点：效率高")；脚注/注释=含"数据来源""资料来源""注：""http"等。"""


def llm_label(texts):
    batch = "\n".join("%d. %s" % (i + 1, t[:80]) for i, t in enumerate(texts))
    prompt = "请标注以下 %d 个段落，逐条输出 JSON 数组：[{\"text\": 原文, \"role\": \"...\"}, ...]\n\n%s" % (len(texts), batch)
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}],
        "stream": False, "options": {"temperature": 0}}).encode()
    # 不走系统代理（urllib 默认走 127.0.0.1:7890 会拒连本机 Ollama）
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    resp = json.loads(opener.open(req, timeout=180).read())
    out = resp["message"]["content"]
    # 提取 JSON 数组
    start, end = out.find("["), out.rfind("]")
    if start < 0 or end < 0:
        return {}, out
    try:
        return json.loads(out[start:end + 1]), out
    except Exception:
        return {}, out


if __name__ == "__main__":
    tests = [
        "一、总体要求",
        "（一）指导思想",
        "1. 坚持党的全面领导",
        "1. 优点：效率高",
        "2. 缺点：成本较大",
        "1. 这里的数据来源于国家统计局：https://data.stats.gov.cn/",
        "2. 资料来源：教育部历年报告。",
        "第一章 绪论",
        "1.1 研究背景",
        "1.1.1 研究目的",
        "[1] 张伟, 李明. 人工智能教育应用研究综述[J]. 电化教育研究, 2025.",
        "关键词：人工智能；教育应用；个性化学习",
        "随着人工智能技术的快速发展，教育领域正在经历深刻变革。",
        "第一条 为了保护民事主体的合法权益，制定本法。",
    ]
    labels, raw = llm_label(tests)
    print("=== qwen3.5 机器标注结果 ===")
    if labels:
        for d in labels:
            print("%-24s → %s" % (str(d.get("text", ""))[:24], d.get("role")))
    else:
        print("解析失败，原始输出:\n", raw[:500])
