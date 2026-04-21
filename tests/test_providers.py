from pathlib import Path

from services.ocr_providers.azure_provider import AzureProvider
from services.ocr_providers.google_provider import GoogleProvider
from services.ocr_providers.openai_provider import OpenAIProvider


def test_openai_extract_text_from_output():
    provider = OpenAIProvider("x")
    data = {
        "output": [
            {"content": [{"type": "output_text", "text": "regel 1"}]},
            {"content": [{"type": "output_text", "text": "regel 2"}]},
        ]
    }
    assert provider._extract_text_from_output(data) == "regel 1\nregel 2"


def test_azure_polygon_to_bbox():
    provider = AzureProvider("https://example.cognitiveservices.azure.com", "k")
    bbox = provider._polygon_to_bbox([10, 20, 40, 20, 40, 30, 10, 30])
    assert bbox == (10, 20, 40, 30)


def test_google_vertices_to_bbox():
    provider = GoogleProvider("/tmp/creds.json")
    bbox = provider._vertices_to_bbox(
        [
            {"x": 5, "y": 10},
            {"x": 20, "y": 10},
            {"x": 20, "y": 16},
            {"x": 5, "y": 16},
        ]
    )
    assert bbox == (5.0, 10.0, 20.0, 16.0)


def test_google_resolve_relative_credentials_path():
    provider = GoogleProvider("creds.json")
    resolved = provider._resolve_credentials_path("creds.json")
    assert resolved.name == "creds.json"
    assert resolved.is_absolute()
    assert str(resolved).startswith(str(Path.cwd()))
