# -*- coding: utf-8 -*-
"""依赖路径引导模块

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import sys
from pathlib import Path


def add_vendor_path() -> None:
    """将项目内 vendor 目录加入 sys.path，便于离线依赖加载

    日期: 2025-12-17
    作者: 余炘洋
    """
    base_dir = Path(__file__).resolve().parent.parent
    vendor_dir = base_dir / "vendor"
    if vendor_dir.exists():
        vendor_str = str(vendor_dir)
        if vendor_str not in sys.path:
            sys.path.insert(0, vendor_str)


# 模块导入时即执行，保证后续模块能发现 vendor 依赖
add_vendor_path()
