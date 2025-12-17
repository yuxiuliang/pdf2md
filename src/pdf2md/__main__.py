# -*- coding: utf-8 -*-
"""pdf2md 应用入口

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk

from pdf2md.app import Pdf2MdApp


def _resolve_icon_path() -> Path | None:
    """解析图标路径，兼容开发与 PyInstaller 环境

    日期: 2025-12-17
    作者: 余炘洋
    """
    candidates = []
    # PyInstaller 展开目录
    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]
    # 可执行文件所在目录（打包后）
    candidates.append(Path(sys.executable).resolve().parent)
    # 项目根目录（源码模式）
    candidates.append(Path(__file__).resolve().parents[2])
    # 当前工作目录兜底
    candidates.append(Path.cwd())

    for base in candidates:
        icon_path = base / "icon.ico"
        if icon_path.exists():
            return icon_path
    return None


def _apply_icon(root: tk.Tk) -> None:
    """为窗口与任务栏设置自定义图标

    日期: 2025-12-17
    作者: 余炘洋
    """
    icon_path = _resolve_icon_path()
    if not icon_path:
        return
    try:
        # Windows 推荐使用 .ico
        root.iconbitmap(default=str(icon_path))
    except Exception:
        # 其他平台可忽略或自行替换为 PNG 后用 iconphoto
        pass


def main() -> None:
    """启动图形界面主循环

    日期: 2025-12-17
    作者: 余炘洋
    """
    root = tk.Tk()
    _apply_icon(root)
    style = ttk.Style()
    style.theme_use("clam")
    Pdf2MdApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
