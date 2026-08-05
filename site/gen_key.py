# -*- coding: utf-8 -*-
"""激活码生成器（卖家端 CLI）：python gen_key.py [学校代号] [数量]

示例：
  python site\\gen_key.py HN           → 生成 1 个，前缀 HN（湖南）
  python site\\gen_key.py AA 5         → 生成 5 个，前缀 AA（通用）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from license.keys import generate_key, is_valid_format

school = sys.argv[1] if len(sys.argv) > 1 else "AA"
count = int(sys.argv[2]) if len(sys.argv) > 2 else 1

for i in range(count):
    k = generate_key(school)
    ok = "OK" if is_valid_format(k) else "FAIL"
    print("%s  %s" % (k, ok))
