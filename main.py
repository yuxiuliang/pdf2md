# -*- coding: utf-8 -*-
"""PDF 转 Markdown 图形界面工具

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Callable, Dict

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def _bootstrap_vendor() -> None:
    """在启动阶段将 vendor 依赖目录加入 sys.path

    日期: 2025-12-17
    作者: 余炘洋
    """
    base_dir = Path(__file__).resolve().parent
    vendor_dir = base_dir / "vendor"
    if vendor_dir.exists():
        sys.path.insert(0, str(vendor_dir))


_bootstrap_vendor()

try:
    from pypdf import PdfReader  # type: ignore
except ImportError as exc:  # pragma: no cover - 依赖缺失时给出友好提示
    raise SystemExit(
        "未找到依赖 pypdf，请先运行 `PYTHONPATH=.pyhome/local/lib/python3.10/dist-packages "
        "python3 -m pip install --target vendor pypdf` 安装依赖"
    ) from exc


class PdfConverter:
    """将 PDF 文件转换为 Markdown 的工具类

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, progress_callback: Callable[[str, int], None]) -> None:
        """初始化转换器并接收进度回调

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._progress_callback = progress_callback

    def convert(self, pdf_path: Path, output_dir: Path) -> Path:
        """执行单个 PDF 的转换，并将进度回调给 GUI

        日期: 2025-12-17
        作者: 余炘洋
        """
        reader = PdfReader(str(pdf_path))
        total_pages = max(len(reader.pages), 1)
        texts = []

        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            texts.append(text)
            percent = min(int(index / total_pages * 100), 100)
            self._progress_callback(str(pdf_path), percent)

        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / f"{pdf_path.stem}.md"
        content = f"# {pdf_path.stem}\n\n" + "\n\n".join(texts)
        md_path.write_text(content, encoding="utf-8")
        self._progress_callback(str(pdf_path), 100)
        return md_path


class FileItem:
    """表示单个文件的 UI 与状态

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, parent: ttk.Frame, file_path: Path) -> None:
        """创建文件行，包含名称、进度条与状态标签

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
        """代理 grid 方法，方便外部调用

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
    """图形化的 PDF 转 Markdown 应用

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, root: tk.Tk) -> None:
        """初始化主界面、事件绑定与状态管理

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
        """搭建界面布局与控件

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
        """处理单文件选择事件

        日期: 2025-12-17
        作者: 余炘洋
        """
        file_path = filedialog.askopenfilename(
            title="选择PDF文件", filetypes=[("PDF 文件", "*.pdf")]
        )
        if file_path:
            self._append_file(Path(file_path))

    def _select_multiple(self) -> None:
        """处理多文件选择事件

        日期: 2025-12-17
        作者: 余炘洋
        """
        files = filedialog.askopenfilenames(
            title="选择多个PDF文件", filetypes=[("PDF 文件", "*.pdf")]
        )
        for file_path in files:
            self._append_file(Path(file_path))

    def _select_output_dir(self) -> None:
        """让用户选择输出目录

        日期: 2025-12-17
        作者: 余炘洋
        """
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def _append_file(self, file_path: Path) -> None:
        """将文件加入列表并创建对应的进度行

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
        """启动后台线程执行转换任务

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
        """在后台顺序处理所有文件的转换

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
            except Exception as exc:  # pragma: no cover - 运行时异常通知
                self._update_status_async(pdf_path, "失败")
                self._show_error_async(pdf_path, exc)

    def _on_progress(self, file_path: str, percent: int) -> None:
        """转换器的进度回调，转交给主线程更新 UI

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._update_progress_async(Path(file_path), percent)

    def _update_progress_async(self, file_path: Path, percent: int) -> None:
        """使用主线程更新进度以避免线程安全问题

        日期: 2025-12-17
        作者: 余炘洋
        """
        if str(file_path) not in self.items:
            return

        def _apply() -> None:
            self.items[str(file_path)].update_progress(percent)

        self.root.after(0, _apply)

    def _update_status_async(self, file_path: Path, status: str) -> None:
        """使用主线程更新状态显示

        日期: 2025-12-17
        作者: 余炘洋
        """
        if str(file_path) not in self.items:
            return

        def _apply() -> None:
            self.items[str(file_path)].update_status(status)

        self.root.after(0, _apply)

    def _show_error_async(self, file_path: Path, exc: Exception) -> None:
        """在主线程展示错误提示框

        日期: 2025-12-17
        作者: 余炘洋
        """

        def _apply() -> None:
            messagebox.showerror("转换失败", f"{file_path.name} 转换失败: {exc}")

        self.root.after(0, _apply)


def main() -> None:
    """应用程序入口，创建并运行 GUI 主循环

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
