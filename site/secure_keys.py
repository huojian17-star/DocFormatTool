# -*- coding: utf-8 -*-
"""从 keys.py 移除 generate_key（生成端移出公开仓库），gen_key.py 改为自带生成逻辑"""
import re

# 1) keys.py 删除 generate_key 函数 + __main__ 自测
p = r'license\keys.py'
src = open(p, encoding='utf-8').read()
pat = re.compile(r'def generate_key\(school_code: str = "AA"\) -> str:.*?\n\n\n', re.S)
assert pat.search(src), 'generate_key 未找到'
src = pat.sub('', src, count=1)
m = src.find('if __name__ == "__main__":')
if m > 0:
    src = src[:m].rstrip() + '\n'
open(p, 'w', encoding='utf-8', newline='').write(src)
print('keys.py 已删 generate_key；剩余:', [l.split('(')[0].strip() for l in src.splitlines() if l.startswith('def ')])

# 2) gen_key.py 重写为自包含（不 import keys）
g = r'site\gen_key.py'
open(g, 'w', encoding='utf-8', newline='').write('''# -*- coding: utf-8 -*-
"""激活码生成器（卖家端本地工具，勿上传公开仓库）：python gen_key.py [学校代号] [数量]"""
import hashlib
import os
import re
import sys

ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
PRODUCT_CODE = "A"


def _checksum(body):
    n = int(hashlib.sha256(body.encode("utf-8")).hexdigest(), 16)
    return ALPHABET[n % len(ALPHABET)]


def generate_key(school_code="AA"):
    school_code = (school_code or "AA").upper()[:2]
    if not re.match(r"^[2-9A-Z]{2}$", school_code):
        school_code = "AA"
    body = school_code + PRODUCT_CODE + "".join(
        ALPHABET[b % len(ALPHABET)] for b in os.urandom(16))
    body = body[:19]
    while len(body) < 19:
        body += ALPHABET[os.urandom(1)[0] % len(ALPHABET)]
    return body + _checksum(body)


school = sys.argv[1] if len(sys.argv) > 1 else "AA"
count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
for i in range(count):
    print(generate_key(school))
''')
print('gen_key.py 已重写为自包含')

# 3) .gitignore 追加 gen_key.py（防再提交）
ig = r'.gitignore'
try:
    content = open(ig, encoding='utf-8').read()
except Exception:
    content = ''
if 'gen_key.py' not in content:
    content += '\n# 卖家端工具，勿提交\nsite/gen_key.py\n'
    open(ig, 'w', encoding='utf-8', newline='').write(content)
    print('.gitignore 已追加 site/gen_key.py')
else:
    print('.gitignore 已有 gen_key.py')
