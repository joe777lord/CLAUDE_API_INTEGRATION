import io
from fastapi.testclient import TestClient
from app.main import app

def fake_pdf(text="This is a legal opinion about standing."):
    return ("case.pdf", io.BytesIO(text.encode("utf-8")), "application/pdf")

def test_summarize_happy_path(monkeypatch):
    # monkeypatch call_claude to avoid hitting Anthropic
    from app import main as m

    def _fake_call(extracted: str):
        assert "standing" in extracted
        return {
            "title": "Smith v. Jones",
            "summary": "Court discusses standing and dismisses without prejudice.",
            "tags": ["standing", "dismissal"],
            "tokens_used": 123
        }

    monkeypatch.setattr(m, "call_claude", _fake_call)

    client = TestClient(app)
    files = {"pdf": fake_pdf()[1:]}  # name & mimetype handled by requests-toolbelt in TestClient
    r = client.post("/summarize", files={"pdf": ("case.pdf", io.BytesIO(b"standing"), "application/pdf")})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Smith v. Jones"
    assert "standing" in data["summary"]
    assert data["tags"] == ["standing", "dismissal"]

def test_rejects_non_pdf():
    client = TestClient(app)
    r = client.post("/summarize", files={"pdf": ("notes.txt", io.BytesIO(b"hello"), "text/plain")})
    assert r.status_code == 400
