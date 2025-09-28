import io
from fastapi.testclient import TestClient
from app.main import app

def test_multi_upload(monkeypatch):
    from app import main as m

    # avoid hitting Anthropic and PDF parser
    monkeypatch.setattr(m, "call_claude", lambda t: {"title":"T","summary":"S","tags":["x"],"tokens_used":1})
    monkeypatch.setattr(m, "extract_text_from_pdf", lambda b: "dummy text")

    client = TestClient(app)
    files = [
        ("pdfs", ("a.pdf", io.BytesIO(b"A"), "application/pdf")),
        ("pdfs", ("b.pdf", io.BytesIO(b"B"), "application/pdf")),
    ]
    r = client.post("/summarize-multi", files=files)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 2 and all("title" in it for it in items)