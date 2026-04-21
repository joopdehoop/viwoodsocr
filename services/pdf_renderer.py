from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class RenderedPage:
    image_bytes: bytes
    width: int
    height: int


class PDFRenderer:
    def render_page_png(self, pdf_path: Path, page_index: int, dpi: int = 300) -> RenderedPage:
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_index]
            pix = page.get_pixmap(dpi=dpi)
            return RenderedPage(
                image_bytes=pix.tobytes("png"),
                width=pix.width,
                height=pix.height,
            )
        finally:
            doc.close()

    def page_count(self, pdf_path: Path) -> int:
        doc = fitz.open(pdf_path)
        try:
            return doc.page_count
        finally:
            doc.close()
