# -*- coding: utf-8 -*-
"""图形化 PDF 转 Markdown 应用

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pdf2md.converter import PdfConverter


class FileItem:
    """文件行展示组件，包含进度与状态

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, parent: ttk.Frame, file_path: Path) -> None:
        """初始化控件与数据绑定

        日期: 2025-12-17
        作者: 余炘洋
        """
        self.file_path = file_path
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value="等待")
        self.percent_var = tk.StringVar(value="0%")

        self._row = ttk.Frame(parent)
        name_label = ttk.Label(self._row, text=file_path.name, width=40, anchor="w")
        name_label.grid(row=0, column=0, padx=(4, 6), pady=4, sticky="w")

        progress = ttk.Progressbar(
            self._row, maximum=100, variable=self.progress_var, length=240
        )
        progress.grid(row=0, column=1, padx=6, pady=4)

        percent_label = ttk.Label(self._row, textvariable=self.percent_var, width=6)
        percent_label.grid(row=0, column=2, padx=6, pady=4)

        status_label = ttk.Label(self._row, textvariable=self.status_var, width=10)
        status_label.grid(row=0, column=3, padx=6, pady=4)

    def grid(self, **kwargs) -> None:
        """暴露 grid 以便父组件布局

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._row.grid(**kwargs)

    def update_progress(self, percent: int) -> None:
        """更新进度显示

        日期: 2025-12-17
        作者: 余炘洋
        """
        self.progress_var.set(percent)
        self.percent_var.set(f"{percent}%")

    def update_status(self, status: str) -> None:
        """更新状态文字

        日期: 2025-12-17
        作者: 余炘洋
        """
        self.status_var.set(status)


class Pdf2MdApp:
    """主 GUI 应用，负责文件管理与任务调度

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, root: tk.Tk) -> None:
        """初始化界面元素与事件绑定

        日期: 2025-12-17
        作者: 余炘洋
        """
        self.root = root
        self.root.title("PDF 转 Markdown")
        self.root.geometry("780x520")

        self.output_dir = tk.StringVar()
        self.items: Dict[str, FileItem] = {}
        self.converter = PdfConverter(self._on_progress)
        self.worker: threading.Thread | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        """搭建界面布局

        日期: 2025-12-17
        作者: 余炘洋
        """
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill="x")

        ttk.Button(action_frame, text="选择单个PDF", command=self._select_single).pack(
            side="left", padx=4
        )
        ttk.Button(action_frame, text="选择多个PDF", command=self._select_multiple).pack(
            side="left", padx=4
        )
        ttk.Button(action_frame, text="选择输出目录", command=self._select_output_dir).pack(
            side="left", padx=4
        )
        ttk.Button(action_frame, text="开始转换", command=self._start_convert).pack(
            side="left", padx=12
        )

        output_frame = ttk.Frame(self.root, padding=10)
        output_frame.pack(fill="x")
        ttk.Label(output_frame, text="输出目录:").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=80).pack(
            side="left", padx=6, fill="x", expand=True
        )

        list_frame = ttk.Frame(self.root, padding=10)
        list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(list_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.file_list = ttk.Frame(canvas)

        self.file_list.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.file_list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _select_single(self) -> None:
        """选择单个 PDF 文件

        日期: 2025-12-17
        作者: 余炘洋
        """
        file_path = filedialog.askopenfilename(
            title="选择PDF文件", filetypes=[("PDF 文件", "*.pdf")]
        )
        if file_path:
            self._append_file(Path(file_path))

    def _select_multiple(self) -> None:
        """选择多个 PDF 文件

        日期: 2025-12-17
        作者: 余炘洋
        """
        files = filedialog.askopenfilenames(
            title="选择多个PDF文件", filetypes=[("PDF 文件", "*.pdf")]
        )
        for file_path in files:
            self._append_file(Path(file_path))

    def _select_output_dir(self) -> None:
        """选择输出目录

        日期: 2025-12-17
        作者: 余炘洋
        """
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def _append_file(self, file_path: Path) -> None:
        """添加文件到队列并创建 UI 行

        日期: 2025-12-17
        作者: 余炘洋
        """
        if str(file_path) in self.items:
            return

        if not self.output_dir.get():
            self.output_dir.set(str(file_path.parent))

        item = FileItem(self.file_list, file_path)
        row_index = len(self.items)
        item.grid(row=row_index, column=0, sticky="we")
        self.file_list.columnconfigure(0, weight=1)
        self.items[str(file_path)] = item

    def _start_convert(self) -> None:
        """启动后台转换线程

        日期: 2025-12-17
        作者: 余炘洋
        """
        if not self.items:
            messagebox.showinfo("提示", "请先选择至少一个PDF文件")
            return

        if self.worker and self.worker.is_alive():
            messagebox.showinfo("提示", "转换已在进行中")
            return

        output_dir = Path(self.output_dir.get()) if self.output_dir.get() else None
        if not output_dir:
            messagebox.showinfo("提示", "请先选择输出目录")
            return

        self.worker = threading.Thread(
            target=self._convert_worker, args=(output_dir,), daemon=True
        )
        self.worker.start()

    def _convert_worker(self, output_dir: Path) -> None:
        """顺序处理所有文件的转换任务

        日期: 2025-12-17
        作者: 余炘洋
        """
        for file_key, item in self.items.items():
            pdf_path = Path(file_key)
            self._update_status_async(pdf_path, "转换中")
            self._update_progress_async(pdf_path, 1)
            try:
                self.converter.convert(pdf_path, output_dir)
                self._update_status_async(pdf_path, "完成")
            except Exception as exc:  # pragma: no cover - 运行时异常提示
                self._update_status_async(pdf_path, "失败")
                self._show_error_async(pdf_path, exc)

    def _on_progress(self, file_path: str, percent: int) -> None:
        """转换进度回调

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._update_progress_async(Path(file_path), percent)

    def _update_progress_async(self, file_path: Path, percent: int) -> None:
        """在主线程中更新进度

        日期: 2025-12-17
        作者: 余炘洋
        """
        if str(file_path) not in self.items:
            return

        def _apply() -> None:
            self.items[str(file_path)].update_progress(percent)

        self.root.after(0, _apply)

    def _update_status_async(self, file_path: Path, status: str) -> None:
        """在主线程中更新状态

        日期: 2025-12-17
        作者: 余炘洋
        """
        if str(file_path) not in self.items:
            return

        def _apply() -> None:
            self.items[str(file_path)].update_status(status)

        self.root.after(0, _apply)

    def _show_error_async(self, file_path: Path, exc: Exception) -> None:
        """弹出错误提示框

        日期: 2025-12-17
        作者: 余炘洋
        """

        def _apply() -> None:
            messagebox.showerror("转换失败", f"{file_path.name} 转换失败: {exc}")

        self.root.after(0, _apply)
