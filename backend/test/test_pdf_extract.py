import io
from pypdf import PdfWriter
from app.main import extract_text_from_pdf

def make_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    # Add text via annotation (simple trick for tests)
    writer.add_metadata({"/Title": "Test"})
    writer.write(buf)
    # For reliable text extraction you can instead ship a small sample PDF file
    return buf.getvalue()

def test_extract_raises_on_empty_pdf():
    b = make_pdf_bytes("")  # empty-ish
    try:
        extract_text_from_pdf(b)
        assert False, "should raise"
    except Exception as e:
        assert "No extractable text" in str(e) or "Failed to read PDF" in str(e)
