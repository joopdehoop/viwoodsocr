from model.ocr_result import OCRDocumentResult, OCRPageResult, OCRWord


def test_combined_text_empty():
    assert OCRDocumentResult().combined_text() == ""


def test_word_can_have_optional_bbox():
    page = OCRPageResult(page_index=0, text="hi", words=[OCRWord("hi", bbox=None)])
    assert page.words[0].bbox is None
