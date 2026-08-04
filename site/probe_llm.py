# -*- coding: utf-8 -*-
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
prompt = ('你是文档结构标注助手。判断段落角色，只输出JSON数组：[{"text":原文,"role":"heading1|heading2|heading3|body|ref_item|keywords|abstract_heading|caption"}]。'
          '标题=短行+编号+无句号结尾；列举=编号后是短语如"1. 优点"；脚注/注释=含数据来源/资料来源/注：/http。\n\n请标注：\n'
          '1. 一、总体要求\n2. （一）指导思想\n3. 1. 优点：效率高\n4. 1. 这里的数据来源于国家统计局：https://data.stats.gov.cn/')
body = json.dumps({'model': 'qwen3.5:latest',
                   'messages': [{'role': 'user', 'content': prompt}],
                   'stream': False, 'options': {'temperature': 0}}).encode()
req = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=body,
                             headers={'Content-Type': 'application/json'})
resp = json.loads(opener.open(req, timeout=180).read())
c = resp['message']['content']
print('content 长度:', len(c))
print(repr(c[:800]))
