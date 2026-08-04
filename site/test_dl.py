# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, '.')
import license.version as v
print('APP_NAME 定义:', hasattr(v, 'APP_NAME'), getattr(v, 'APP_NAME', None))
print('VERSION:', v.VERSION)
# 直接调 download（小文件测试）
tmp = os.path.join(os.environ['TEMP'], 'dl_test.bin')
try:
    v.download('https://raw.githubusercontent.com/huojian17-star/DocFormatTool/master/version.json', tmp, timeout=20, total_limit=30)
    print('download OK:', os.path.getsize(tmp), 'bytes')
    os.remove(tmp)
except Exception as e:
    print('download 失败:', repr(e))
