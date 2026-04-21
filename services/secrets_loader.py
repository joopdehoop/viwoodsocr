import os
from dotenv import load_dotenv


class SecretsLoader:
    def __init__(self) -> None:
        load_dotenv()

    def get(self, key: str) -> str:
        value = os.getenv(key, "").strip()
        if not value:
            raise ValueError(f"Missing required secret: {key}")
        return value
