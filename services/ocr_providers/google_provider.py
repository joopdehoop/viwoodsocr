import base64
import json
from pathlib import Path

from model.ocr_result import OCRPageResult, OCRWord
from services.ocr_providers.base_provider import BaseOCRProvider


class GoogleProvider(BaseOCRProvider):
    name = "google"

    def __init__(self, credentials_source: str) -> None:
        self.credentials_source = credentials_source

    def scan_page(self, image_bytes: bytes, page_index: int, language_hint: str = "nl") -> OCRPageResult:
        import requests

        token = self._get_access_token()
        payload = {
            "requests": [
                {
                    "image": {"content": base64.b64encode(image_bytes).decode("utf-8")},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "imageContext": {"languageHints": [language_hint]},
                }
            ]
        }
        response = requests.post(
            "https://vision.googleapis.com/v1/images:annotate",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json().get("responses", [{}])[0]

        full_text = data.get("fullTextAnnotation", {}).get("text", "").strip()
        words = self._extract_words(data.get("fullTextAnnotation", {}))
        return OCRPageResult(page_index=page_index, text=full_text, words=words)

    def _resolve_credentials_path(self, raw_value: str) -> Path:
        path = Path(raw_value.strip()).expanduser()
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        return path

    def _get_access_token(self) -> str:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account

        raw = self.credentials_source.strip()

        if raw.startswith("{"):
            info = json.loads(raw)
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        else:
            path = self._resolve_credentials_path(raw)
            if not path.exists():
                raise FileNotFoundError(
                    "Google credential file niet gevonden. Zet in .env een pad, bijv. "
                    "GOOGLE_APPLICATION_CREDENTIALS=./my-service-account.json"
                )
            credentials = service_account.Credentials.from_service_account_file(
                str(path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        credentials.refresh(Request())
        return credentials.token

    def _extract_words(self, annotation: dict) -> list[OCRWord]:
        out: list[OCRWord] = []
        for page in annotation.get("pages", []):
            for block in page.get("blocks", []):
                for paragraph in block.get("paragraphs", []):
                    for word in paragraph.get("words", []):
                        symbols = word.get("symbols", [])
                        word_text = "".join(symbol.get("text", "") for symbol in symbols).strip()
                        bbox = self._vertices_to_bbox(word.get("boundingBox", {}).get("vertices", []))
                        out.append(OCRWord(text=word_text, bbox=bbox, confidence=word.get("confidence")))
        return out

    def _vertices_to_bbox(self, vertices: list[dict]) -> tuple[float, float, float, float] | None:
        if not vertices:
            return None
        xs = [float(v.get("x", 0)) for v in vertices]
        ys = [float(v.get("y", 0)) for v in vertices]
        return min(xs), min(ys), max(xs), max(ys)
