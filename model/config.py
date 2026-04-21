from dataclasses import dataclass


@dataclass
class ScanConfig:
    provider_name: str
    language_hint: str = "nl"
    dpi: int = 300
