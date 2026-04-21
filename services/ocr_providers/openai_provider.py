import base64

from model.ocr_result import OCRPageResult
from services.ocr_providers.base_provider import BaseOCRProvider


class OpenAIProvider(BaseOCRProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        self.api_key = api_key
        self.model = model

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        import requests

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract all readable text from this scanned document page. "
                                f"Keep original reading order and return plain text only. Language hint: {language_hint}."
                            ),
                        },
                        {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
                    ],
                }
            ],
            "temperature": 0,
        }

        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        text = data.get("output_text", "").strip()
        if not text:
            text = self._extract_text_from_output(data)

        return OCRPageResult(page_index=page_index, text=text)

    def _extract_text_from_output(self, data: dict) -> str:
        chunks: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks).strip()
