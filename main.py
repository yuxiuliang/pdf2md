# -*- coding: utf-8 -*-
"""pdf2md 外部启动脚本

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import sys
from pathlib import Path

# 将本地 src 路径加入 sys.path，便于未安装包时直接运行
# 日期: 2025-12-17
# 作者: 余炘洋
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

from pdf2md.__main__ import main  # noqa: E402


if __name__ == "__main__":
    main()
