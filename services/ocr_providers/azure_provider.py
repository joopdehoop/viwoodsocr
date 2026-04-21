import time

from model.ocr_result import OCRPageResult, OCRWord
from services.ocr_providers.base_provider import BaseOCRProvider


class AzureProvider(BaseOCRProvider):
    name = "azure"

    def __init__(self, endpoint: str, api_key: str, api_version: str = "2024-11-30") -> None:
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        import requests

        submit_url = (
            f"{self.endpoint}/documentintelligence/documentModels/prebuilt-read:analyze"
            f"?api-version={self.api_version}&locale={language_hint}"
        )
        submit = requests.post(
            submit_url,
            headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "Content-Type": "application/octet-stream",
            },
            data=image_bytes,
            timeout=120,
        )
        submit.raise_for_status()

        operation_location = submit.headers.get("operation-location")
        if not operation_location:
            raise RuntimeError("Azure response bevat geen operation-location header.")

        data = self._poll_result(operation_location)
        analyze = data.get("analyzeResult", {})
        text = analyze.get("content", "").strip()
        words = self._extract_words(analyze)
        return OCRPageResult(page_index=page_index, text=text, words=words)

    def _poll_result(self, operation_location: str, timeout_seconds: int = 120) -> dict:
        import requests

        start = time.time()
        while True:
            response = requests.get(
                operation_location,
                headers={"Ocp-Apim-Subscription-Key": self.api_key},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            status = (data.get("status") or "").lower()
            if status == "succeeded":
                return data
            if status == "failed":
                raise RuntimeError(f"Azure OCR mislukte: {data}")
            if time.time() - start > timeout_seconds:
                raise TimeoutError("Timeout tijdens wachten op Azure OCR resultaat.")
            time.sleep(1.0)

    def _extract_words(self, analyze: dict) -> list[OCRWord]:
        out: list[OCRWord] = []
        for page in analyze.get("pages", []):
            for word in page.get("words", []):
                polygon = word.get("polygon", [])
                bbox = self._polygon_to_bbox(polygon)
                out.append(
                    OCRWord(
                        text=word.get("content", ""),
                        bbox=bbox,
                        confidence=word.get("confidence"),
                    )
                )
        return out

    def _polygon_to_bbox(self, polygon: list[float]) -> tuple[float, float, float, float] | None:
        if not polygon or len(polygon) < 8:
            return None
        xs = polygon[0::2]
        ys = polygon[1::2]
        return min(xs), min(ys), max(xs), max(ys)
