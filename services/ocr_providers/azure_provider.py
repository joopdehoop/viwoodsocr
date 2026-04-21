from model.ocr_result import OCRPageResult
from services.ocr_providers.base_provider import BaseOCRProvider


class AzureProvider(BaseOCRProvider):
    name = "azure"

    def __init__(self, endpoint: str, api_key: str) -> None:
        self.endpoint = endpoint
        self.api_key = api_key

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        # TODO: Implement Azure Document Intelligence API call.
        return OCRPageResult(page_index=page_index, text="[Azure OCR placeholder]")
