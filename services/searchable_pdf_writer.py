from pathlib import Path
import fitz

from model.ocr_result import OCRDocumentResult


class SearchablePDFWriter:
    def write(self, source_pdf: Path, target_pdf: Path, result: OCRDocumentResult) -> Path:
        doc = fitz.open(source_pdf)
        try:
            for page_result in result.pages:
                page = doc[page_result.page_index]
                rect = page.rect
                # Simple invisible text layer across the page.
                page.insert_textbox(
                    rect,
                    page_result.text,
                    fontsize=9,
                    color=(1, 1, 1),
                    fill_opacity=0,
                    render_mode=3,
                )
            doc.save(target_pdf)
        finally:
            doc.close()
        return target_pdf
