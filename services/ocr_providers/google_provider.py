from model.ocr_result import OCRPageResult
from services.ocr_providers.base_provider import BaseOCRProvider


class GoogleProvider(BaseOCRProvider):
    name = "google"

    def __init__(self, credentials_path: str) -> None:
        self.credentials_path = credentials_path

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        # TODO: Implement Google Vision / Document AI call.
        return OCRPageResult(page_index=page_index, text="[Google OCR placeholder]")
