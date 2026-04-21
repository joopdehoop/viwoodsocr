from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    path: Path

    @property
    def name(self) -> str:
        return self.path.name
