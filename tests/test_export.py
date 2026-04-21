from model.ocr_result import OCRDocumentResult, OCRPageResult, OCRWord
from services.searchable_pdf_writer import SearchablePDFWriter


def test_combined_text_empty():
    assert OCRDocumentResult().combined_text() == ""


def test_word_can_have_optional_bbox():
    page = OCRPageResult(page_index=0, text="hi", words=[OCRWord("hi", bbox=None)], image_size=None)
    assert page.words[0].bbox is None


def test_scale_bbox_from_image_to_pdf_coordinates():
    # image 1000x2000 gets projected on page 500x1000 => coordinates halve.
    scaled = SearchablePDFWriter._scale_bbox((100, 200, 300, 400), (1000, 2000), (500, 1000))
    assert scaled == (50.0, 100.0, 150.0, 200.0)
