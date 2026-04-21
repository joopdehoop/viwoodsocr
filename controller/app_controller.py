from pathlib import Path

from model.config import ScanConfig
from services.ocr_providers import OpenAIProvider, AzureProvider, GoogleProvider
from services.secrets_loader import SecretsLoader


class AppController:
    def __init__(self, secrets: SecretsLoader) -> None:
        self.secrets = secrets

    def build_provider(self, provider_name: str):
        key = provider_name.lower()
        if key == "openai":
            return OpenAIProvider(api_key=self.secrets.get("OPENAI_API_KEY"))
        if key == "azure":
            return AzureProvider(
                endpoint=self.secrets.get("AZURE_DOCINTEL_ENDPOINT"),
                api_key=self.secrets.get("AZURE_DOCINTEL_KEY"),
            )
        if key == "google":
            return GoogleProvider(credentials_path=self.secrets.get("GOOGLE_APPLICATION_CREDENTIALS"))
        raise ValueError(f"Unknown provider: {provider_name}")

    def default_output_path(self, source: Path) -> Path:
        return source.with_name(f"{source.stem}_searchable.pdf")

    @staticmethod
    def make_config(provider_name: str, language_hint: str = "nl", dpi: int = 300) -> ScanConfig:
        return ScanConfig(provider_name=provider_name, language_hint=language_hint, dpi=dpi)
