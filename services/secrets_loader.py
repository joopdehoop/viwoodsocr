import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # optional in minimal test/runtime environments
    def load_dotenv(*args, **kwargs) -> bool:
        return False


class SecretsLoader:
    def __init__(self) -> None:
        # Always try the project-root .env first (stable for uv/venv and different cwd's).
        project_env = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=project_env, override=False)

        # Then allow default discovery behavior as fallback.
        load_dotenv(override=False)

    def get(self, key: str) -> str:
        value = os.getenv(key, "").strip()
        if not value:
            raise ValueError(f"Missing required secret: {key}")
        return value

    def optional(self, key: str, default: str = "") -> str:
        value = os.getenv(key, "").strip()
        return value or default
