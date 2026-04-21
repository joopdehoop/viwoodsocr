from pathlib import Path

from controller.app_controller import AppController
from services.secrets_loader import SecretsLoader


class DummySecrets(SecretsLoader):
    def __init__(self, values: dict[str, str]) -> None:
        self.values = values

    def get(self, key: str) -> str:
        if key not in self.values:
            raise ValueError(key)
        return self.values[key]


def test_default_output_path():
    app = AppController(DummySecrets({}))
    assert app.default_output_path(Path("demo.pdf")).name == "demo_searchable.pdf"
