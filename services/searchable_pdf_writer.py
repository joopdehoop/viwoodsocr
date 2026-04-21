from pathlib import Path
import fitz

from model.ocr_result import OCRDocumentResult, OCRWord


class SearchablePDFWriter:
    def _write_word(self, page: fitz.Page, word: OCRWord) -> None:
        if not word.bbox:
            return
        x0, y0, x1, y1 = word.bbox
        rect = fitz.Rect(x0, y0, x1, y1)
        if rect.width <= 0 or rect.height <= 0:
            return
        fontsize = max(6, min(18, rect.height * 0.9))
        page.insert_textbox(
            rect,
            word.text,
            fontsize=fontsize,
            color=(1, 1, 1),
            fill_opacity=0,
            render_mode=3,
        )

    def write(self, source_pdf: Path, target_pdf: Path, result: OCRDocumentResult) -> Path:
        doc = fitz.open(source_pdf)
        try:
            for page_result in result.pages:
                page = doc[page_result.page_index]

                if page_result.words:
                    for word in page_result.words:
                        self._write_word(page, word)
                else:
                    page.insert_textbox(
                        page.rect,
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
