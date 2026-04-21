from pathlib import Path

from model.config import ScanConfig
from model.ocr_result import OCRDocumentResult
from services.pdf_renderer import PDFRenderer


class OCRController:
    def __init__(self, renderer: PDFRenderer) -> None:
        self.renderer = renderer

    def scan_document(self, pdf_path: Path, provider, config: ScanConfig, on_progress=None) -> OCRDocumentResult:
        result = OCRDocumentResult()
        total = self.renderer.page_count(pdf_path)
        for page_index in range(total):
            rendered = self.renderer.render_page_png(pdf_path, page_index, dpi=config.dpi)
            page_result = provider.scan_page(
                rendered.image_bytes,
                page_index=page_index,
                language_hint=config.language_hint,
            )
            page_result.image_size = (rendered.width, rendered.height)
            result.pages.append(page_result)
            if on_progress:
                on_progress(page_index + 1, total)
        return result
