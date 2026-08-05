"""pytest 路径引导（仓库根运行 `pytest` 时让 app.* 与 edge.* 可导入）。

沙箱无 pytest 时不影响：各测试文件自带 sys.path 注入与 __main__ 直接运行入口。
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
for p in (ROOT, os.path.join(ROOT, "backend")):
    if p not in sys.path:
        sys.path.insert(0, p)
