from model.ocr_result import OCRPageResult
from services.ocr_providers.base_provider import BaseOCRProvider


class OpenAIProvider(BaseOCRProvider):
    name = "openai"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        # TODO: Implement OpenAI Vision API call.
        return OCRPageResult(page_index=page_index, text="[OpenAI OCR placeholder]")
