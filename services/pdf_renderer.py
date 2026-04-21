from pathlib import Path
import fitz


class PDFRenderer:
    def render_page_png(self, pdf_path: Path, page_index: int, dpi: int = 300) -> bytes:
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_index]
            pix = page.get_pixmap(dpi=dpi)
            return pix.tobytes("png")
        finally:
            doc.close()

    def page_count(self, pdf_path: Path) -> int:
        doc = fitz.open(pdf_path)
        try:
            return doc.page_count
        finally:
            doc.close()
