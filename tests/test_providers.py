from services.ocr_providers.azure_provider import AzureProvider
from services.ocr_providers.google_provider import GoogleProvider
from services.ocr_providers.openai_provider import OpenAIProvider


def test_provider_placeholders():
    assert "placeholder" in OpenAIProvider("x").scan_page(b"a", 0).text.lower()
    assert "placeholder" in AzureProvider("e", "k").scan_page(b"a", 0).text.lower()
    assert "placeholder" in GoogleProvider("c").scan_page(b"a", 0).text.lower()
