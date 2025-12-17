# -*- coding: utf-8 -*-
"""PDF 转 Markdown 核心转换逻辑

日期: 2025-12-17
作者: 余炘洋
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Callable, Iterable, Sequence

from pdf2md.bootstrap import add_vendor_path

add_vendor_path()

try:
    from pypdf import PdfReader  # type: ignore
    from fpdf import FPDF  # type: ignore
except ImportError as exc:  # pragma: no cover - 依赖缺失提示
    raise SystemExit(
        "未找到依赖 pypdf/fpdf2，请先运行 `pip install -r requirements.txt` "
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


class MdToPdfConverter:
    """将 Markdown 文本转换为简单 PDF

    日期: 2025-12-17
    作者: 余炘洋
    """

    def __init__(self, progress_callback: Callable[[str, int], None]) -> None:
        """保存进度回调函数

        日期: 2025-12-17
        作者: 余炘洋
        """
        self._progress_callback = progress_callback
        self._font_name: str | None = None
        self._font_path: Path | None = None

    def _iterate_lines(self, text: str) -> Iterable[str]:
        """对 Markdown 文本进行极简行级处理

        日期: 2025-12-17
        作者: 余炘洋
        """
        lines = text.splitlines()
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                yield stripped.lstrip("#").strip()
            else:
                yield line

    def _wrap_line(self, pdf: FPDF, line: str, max_width: float) -> list[str]:
        """按可用宽度对单行文本进行字符级换行

        日期: 2025-12-17
        作者: 余炘洋
        """
        if line == "":
            return [""]

        wrapped: list[str] = []
        current = ""
        for char in line:
            candidate = current + char
            if pdf.get_string_width(candidate) <= max_width:
                current = candidate
                continue

            if current:
                wrapped.append(current)
                current = char
            else:
                # 单字符也超宽时，仍强制输出该字符，避免死循环
                wrapped.append(char)
                current = ""

        if current:
            wrapped.append(current)
        return wrapped

    def _font_candidates(self) -> Sequence[Path]:
        """收集可用字体路径候选

        日期: 2025-12-17
        作者: 余炘洋
        """
        candidates: list[Path] = []

        env_path = os.getenv("PDF2MD_FONT_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists():
                candidates.append(path)

        env_dir = os.getenv("PDF2MD_FONT_DIR")
        if env_dir:
            candidates.extend(self._scan_font_dir(Path(env_dir)))

        base_dirs = []
        if hasattr(sys, "_MEIPASS"):
            base_dirs.append(Path(sys._MEIPASS))  # type: ignore[attr-defined]
        base_dirs.append(Path(sys.executable).resolve().parent)
        base_dirs.append(Path(__file__).resolve().parents[2])
        base_dirs.append(Path.cwd())

        for base in base_dirs:
            candidates.extend(self._scan_font_dir(base / "fonts"))

        if os.name == "nt":
            windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
            for name in [
                "simhei.ttf",
                "simsun.ttf",
                "simfang.ttf",
                "simkai.ttf",
                "msyh.ttf",
            ]:
                font_path = windows_fonts / name
                if font_path.exists():
                    candidates.append(font_path)
        else:
            for name in [
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]:
                font_path = Path(name)
                if font_path.exists():
                    candidates.append(font_path)

        return candidates

    def _scan_font_dir(self, font_dir: Path) -> Sequence[Path]:
        """扫描字体目录中的 .ttf/.otf 文件

        日期: 2025-12-17
        作者: 余炘洋
        """
        if not font_dir.exists():
            return []
        fonts = list(font_dir.glob("*.ttf")) + list(font_dir.glob("*.otf"))
        return sorted(fonts)

    def _ensure_font(self, pdf: FPDF) -> str:
        """加载可用字体并返回字体名称

        日期: 2025-12-17
        作者: 余炘洋
        """
        # 若已有缓存的字体信息，确保在当前 pdf 实例注册
        if self._font_name and self._font_path:
            if self._font_name not in getattr(pdf, "fonts", {}):
                pdf.add_font(self._font_name, "", str(self._font_path), uni=True)
            return self._font_name

        for index, path in enumerate(self._font_candidates(), start=1):
            font_name = f"Custom{index}"
            try:
                pdf.add_font(font_name, "", str(path), uni=True)
                self._font_name = font_name
                self._font_path = path
                return font_name
            except Exception:
                continue

        raise RuntimeError(
            "未找到可用的中文字体，请在 fonts/ 目录放置 .ttf/.otf，"
            "或设置环境变量 PDF2MD_FONT_PATH。"
        )

    def convert(self, md_path: Path, output_dir: Path) -> Path:
        """读取 Markdown 并导出 PDF（不渲染样式，偏重文本）

        日期: 2025-12-17
        作者: 余炘洋
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        font_name = self._ensure_font(pdf)
        pdf.set_font(font_name, size=12)

        content = md_path.read_text(encoding="utf-8")
        raw_lines = list(self._iterate_lines(content))
        max_width = pdf.w - pdf.l_margin - pdf.r_margin
        wrapped_lines: list[str] = []
        for line in raw_lines:
            safe_line = line.replace("\t", "    ")
            wrapped_lines.extend(self._wrap_line(pdf, safe_line, max_width))

        total = max(len(wrapped_lines), 1)
        for idx, line in enumerate(wrapped_lines, start=1):
            pdf.cell(0, 8, txt=line, ln=1)
            percent = min(int(idx / total * 100), 100)
            self._progress_callback(str(md_path), percent)

        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / f"{md_path.stem}.pdf"
        pdf.output(str(pdf_path))
        self._progress_callback(str(md_path), 100)
        return pdf_path
