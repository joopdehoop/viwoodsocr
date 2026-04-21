from dataclasses import dataclass, field


@dataclass
class OCRWord:
    text: str
    # (x0, y0, x1, y1) in PDF/page coordinates when available.
    bbox: tuple[float, float, float, float] | None = None
    confidence: float | None = None


@dataclass
class OCRPageResult:
    page_index: int
    text: str
    words: list[OCRWord] = field(default_factory=list)


@dataclass
class OCRDocumentResult:
    pages: list[OCRPageResult] = field(default_factory=list)

    def combined_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages)
