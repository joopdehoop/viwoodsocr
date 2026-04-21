from abc import ABC, abstractmethod

from model.ocr_result import OCRPageResult


class BaseOCRProvider(ABC):
    name: str

    @abstractmethod
    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        raise NotImplementedError
