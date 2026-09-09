import os
import sys

# 把项目根目录（shop_test）加入 sys.path，保证下面这些导入能找到模块：
#   from common import Request
#   from config import LOGIN_URL, AJAX_HEADERS
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
