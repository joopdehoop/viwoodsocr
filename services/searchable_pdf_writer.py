from pathlib import Path

from model.ocr_result import OCRDocumentResult, OCRWord


class SearchablePDFWriter:
    @staticmethod
    def _scale_bbox(
        bbox: tuple[float, float, float, float],
        source_size: tuple[int, int],
        target_size: tuple[float, float],
    ) -> tuple[float, float, float, float]:
        sx = target_size[0] / float(source_size[0])
        sy = target_size[1] / float(source_size[1])
        x0, y0, x1, y1 = bbox
        return x0 * sx, y0 * sy, x1 * sx, y1 * sy

    def _write_word(
        self,
        page,
        word: OCRWord,
        source_size: tuple[int, int],
    ) -> None:
        import fitz

        if not word.bbox:
            return

        x0, y0, x1, y1 = self._scale_bbox(
            word.bbox,
            source_size=source_size,
            target_size=(page.rect.width, page.rect.height),
        )

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
        import fitz

        doc = fitz.open(source_pdf)
        try:
            for page_result in result.pages:
                page = doc[page_result.page_index]

                if page_result.words and page_result.image_size:
                    for word in page_result.words:
                        self._write_word(page, word, source_size=page_result.image_size)
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
