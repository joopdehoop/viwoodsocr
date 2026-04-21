from model.ocr_result import OCRDocumentResult


def test_combined_text_empty():
    assert OCRDocumentResult().combined_text() == ""
