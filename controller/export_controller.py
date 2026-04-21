from pathlib import Path

from model.ocr_result import OCRDocumentResult
from services.searchable_pdf_writer import SearchablePDFWriter


class ExportController:
    def __init__(self, writer: SearchablePDFWriter) -> None:
        self.writer = writer

    def export_searchable_pdf(self, source_pdf: Path, result: OCRDocumentResult, target_pdf: Path) -> Path:
        return self.writer.write(source_pdf, target_pdf, result)
