import re
from datetime import datetime
from pathlib import Path

from services.secrets_loader import SecretsLoader


class DocumentFileNamer:
    def __init__(self, secrets: SecretsLoader) -> None:
        self.secrets = secrets

    @staticmethod
    def _sanitize_description(text: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9\-\s]", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned:
            return "Document"
        return cleaned[:60].strip()

    def _fallback_filename(self, original_pdf: Path) -> str:
        date_part = datetime.now().strftime("%Y-%m-%d")
        desc = self._sanitize_description(original_pdf.stem.replace("_", " "))
        return f"{date_part} {desc}.pdf"

    @staticmethod
    def _normalize_llm_filename(candidate: str, original_pdf: Path) -> str:
        line = candidate.strip().splitlines()[0].strip().strip('"')
        line = line.replace("/", "-").replace("\\", "-")
        line = re.sub(r"[<>:\\|?*]", "", line)

        match = re.match(r"^(\d{4}-\d{2}-\d{2})\s+(.+?)(?:\.pdf)?$", line, flags=re.IGNORECASE)
        if not match:
            date_part = datetime.now().strftime("%Y-%m-%d")
            return f"{date_part} {original_pdf.stem}.pdf"

        date_part, description = match.groups()
        description = re.sub(r"\s+", " ", description).strip()
        if not description:
            description = original_pdf.stem
        description = description[:60]
        return f"{date_part} {description}.pdf"

    def suggest_filename(self, original_pdf: Path, ocr_text: str) -> str:
        api_key = self.secrets.optional("OPENAI_API_KEY", "")
        model = self.secrets.optional("OPENAI_FILENAME_MODEL", "gpt-4.1-mini")
        if not api_key:
            return self._fallback_filename(original_pdf)

        try:
            import requests

            prompt = (
                "You rename OCR'd notes. Return ONLY a filename in this exact format: "
                "YYYY-MM-DD Short description.pdf\n"
                "Rules:\n"
                "- Infer the note date from text if possible; otherwise use today's date.\n"
                "- Keep short description 3-8 words, concise and specific.\n"
                "- Use ASCII only, no slashes, no extra punctuation.\n"
                f"Current filename: {original_pdf.name}\n"
                f"OCR text (first 6000 chars):\n{ocr_text[:6000]}"
            )
            payload = {
                "model": model,
                "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
                "temperature": 0.2,
            }
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("output_text", "").strip()
            if not text:
                text = ""
                for item in data.get("output", []):
                    for content in item.get("content", []):
                        if content.get("type") == "output_text" and content.get("text"):
                            text += content["text"]
            if not text:
                return self._fallback_filename(original_pdf)
            return self._normalize_llm_filename(text, original_pdf)
        except Exception:
            return self._fallback_filename(original_pdf)

    @staticmethod
    def ensure_unique_path(target: Path) -> Path:
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        parent = target.parent
        i = 1
        while True:
            candidate = parent / f"{stem} ({i}){suffix}"
            if not candidate.exists():
                return candidate
            i += 1
