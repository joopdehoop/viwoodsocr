import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # optional in minimal test/runtime environments
    def load_dotenv() -> bool:
        return False


class SecretsLoader:
    def __init__(self) -> None:
        load_dotenv()

    def get(self, key: str) -> str:
        value = os.getenv(key, "").strip()
        if not value:
            raise ValueError(f"Missing required secret: {key}")
        return value

    def optional(self, key: str, default: str = "") -> str:
        value = os.getenv(key, "").strip()
        return value or default
