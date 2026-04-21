from pathlib import Path

from services.document_file_namer import DocumentFileNamer
from services.secrets_loader import SecretsLoader


class DummySecrets(SecretsLoader):
    def __init__(self):
        pass

    def optional(self, key: str, default: str = "") -> str:
        return ""


def test_normalize_llm_filename():
    name = DocumentFileNamer._normalize_llm_filename("2024-01-31 Team meeting notes.pdf", Path("orig.pdf"))
    assert name == "2024-01-31 Team meeting notes.pdf"


def test_fallback_filename_has_date_and_pdf():
    namer = DocumentFileNamer(DummySecrets())
    result = namer._fallback_filename(Path("my_note.pdf"))
    assert result.endswith(".pdf")
    assert len(result.split(" ")[0]) == 10


def test_ensure_unique_path(tmp_path: Path):
    first = tmp_path / "2024-01-31 Test.pdf"
    first.write_text("x")
    unique = DocumentFileNamer.ensure_unique_path(first)
    assert unique.name == "2024-01-31 Test (1).pdf"
