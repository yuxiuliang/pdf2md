# -*- coding: utf-8 -*-
"""pdf2md 应用入口

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from pdf2md.app import Pdf2MdApp


def main() -> None:
    """启动图形界面主循环

    日期: 2025-12-17
    作者: 余炘洋
    """
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    Pdf2MdApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
