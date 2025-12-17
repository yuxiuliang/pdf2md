# -*- coding: utf-8 -*-
"""PDF 转 Markdown 核心转换逻辑

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from pdf2md.bootstrap import add_vendor_path

add_vendor_path()

try:
    from pypdf import PdfReader  # type: ignore
except ImportError as exc:  # pragma: no cover - 依赖缺失提示
    raise SystemExit(
        "未找到依赖 pypdf，请先运行 `pip install -r requirements.txt` "
        "或 `pip install --target vendor -r requirements.txt` 安装依赖。"
    ) from exc


class PdfConverter:
    """将单个 PDF 转换为 Markdown 文件

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, progress_callback: Callable[[str, int], None]) -> None:
        """保存进度回调函数

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._progress_callback = progress_callback

    def convert(self, pdf_path: Path, output_dir: Path) -> Path:
        """读取 PDF 内容并输出 Markdown，按页上报进度

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
