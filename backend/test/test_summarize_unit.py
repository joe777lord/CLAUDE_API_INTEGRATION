import io
from fastapi.testclient import TestClient
from app.main import app

def test_summarize_happy_path(monkeypatch):
    # avoid touching Anthropic AND the PDF parser
    from app import main as m

    def _fake_call(extracted: str):
        assert "standing" in extracted
        return {
            "title": "Smith v. Jones",
            "summary": "Court discusses standing and dismisses without prejudice.",
            "tags": ["standing", "dismissal"],
            "tokens_used": 123,
        }

    monkeypatch.setattr(m, "call_claude", _fake_call)
    monkeypatch.setattr(m, "extract_text_from_pdf", lambda b: "standing in extracted")

    client = TestClient(app)
    r = client.post(
        "/summarize",
        files={"pdf": ("case.pdf", io.BytesIO(b"anything"), "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Smith v. Jones"
    assert "standing" in data["summary"]
    assert data["tags"] == ["standing", "dismissal"]
