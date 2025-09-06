import os
import io
import json
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from anthropic import Anthropic, APIStatusError
from dotenv import load_dotenv

load_dotenv(override=True)  # load .env if present

# --- Config ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
print("Using Anthropic key prefix:", (ANTHROPIC_API_KEY or "")[:10] + "…")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY not set. Create backend/.env from .env.example")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

MAX_INPUT_CHARS = 120_000  # basic guardrail; Claude 3.5 supports long context, but we trim to be safe

app = FastAPI(title="Legal PDF Summarizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryResponse(BaseModel):
    title: str
    summary: str
    tags: List[str]
    tokens_used: Optional[int] = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

    texts = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or "")
        except Exception as e:
            # Continue but note the error location
            texts.append(f"[[Page {i+1} extraction error: {e}]]")
    full_text = "\n\n".join(texts).strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
    return full_text[:MAX_INPUT_CHARS]

def build_prompt(extracted: str) -> str:
    return (
        "You are a legal analyst. Summarize the following U.S. legal opinion.\n"
        "Return STRICT JSON with keys: title (string), summary (multi-paragraph string), tags (array of short strings).\n"
        "Focus on jurisdiction, procedural posture, key facts, issues, holding, reasoning, and outcome.\n"
        "Keep title concise (<= 120 chars). Provide 5-10 tags like 'patent', 'contract', 'standing', 'Federal Circuit'.\n\n"
        "TEXT START\n"
        f"{extracted}\n"
        "TEXT END\n"
    )

def call_claude(extracted: str) -> Dict[str, Any]:
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = build_prompt(extracted)
    try:
        msg = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=800,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
    except APIStatusError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # Extract text content
    text_blocks = [b.text for b in msg.content if b.type == "text"]
    raw = "\n".join(text_blocks).strip() if text_blocks else ""

    # Try to parse JSON; if it isn't strict, try to locate a JSON object heuristically
    data = None
    if raw:
        # Heuristic: find first '{' and last '}' to parse
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            data = json.loads(raw[start:end])
        except Exception:
            pass
    if not data or not isinstance(data, dict):
        # Fallback shape
        data = {
            "title": "Untitled Summary",
            "summary": raw or "No summary text returned.",
            "tags": ["summary", "legal", "claude"]
        }

    # Normalize fields
    title = str(data.get("title", "Untitled Summary")).strip() or "Untitled Summary"
    summary = str(data.get("summary", data.get("content", ""))).strip() or "No summary content."
    tags = data.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    tags = [str(t).strip() for t in tags if str(t).strip()][:10]

    tokens_used = None
    usage = getattr(msg, "usage", None)
    try:
        if usage is not None:
            # Try field access first (Pydantic-style object)
            tokens_used = getattr(usage, "input_tokens", None)
            if tokens_used is None:
                # Pydantic v2
                if hasattr(usage, "model_dump"):
                    tokens_used = usage.model_dump().get("input_tokens")
                # Pydantic v1
                elif hasattr(usage, "dict"):
                    tokens_used = usage.dict().get("input_tokens")
    except Exception:
        tokens_used = None

    return {
        "title": title,
        "summary": summary,
        "tags": tags,
        "tokens_used": tokens_used, 
        # "tokens_used": getattr(msg, "usage", {}).get("input_tokens", None) if hasattr(msg, "usage") else None,
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/summarize", response_model=SummaryResponse)
async def summarize(pdf: UploadFile = File(...)):
    if not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file.")
    file_bytes = await pdf.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    extracted = extract_text_from_pdf(file_bytes)
    result = call_claude(extracted)
    return SummaryResponse(**result)

# Bonus: multiple uploads
class MultiSummaryItem(BaseModel):
    filename: str
    title: str
    summary: str
    tags: List[str]

@app.post("/summarize-multi")
async def summarize_multi(pdfs: List[UploadFile] = File(...)):
    responses = []
    for pdf in pdfs:
        if not pdf.filename.lower().endswith(".pdf"):
            responses.append({"filename": pdf.filename, "error": "Not a PDF"})
            continue
        file_bytes = await pdf.read()
        try:
            extracted = extract_text_from_pdf(file_bytes)
            result = call_claude(extracted)
            responses.append({"filename": pdf.filename, **result})
        except HTTPException as e:
            responses.append({"filename": pdf.filename, "error": e.detail})
        except Exception as e:
            responses.append({"filename": pdf.filename, "error": str(e)})
    return {"items": responses}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
