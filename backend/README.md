# Backend (FastAPI) — Legal PDF Summarizer

## Quickstart

1. Create and fill `.env` from `.env.example`:

   ```bash
   cp .env.example .env
   # edit .env and set ANTHROPIC_API_KEY
   ```

2. Create a virtual environment and install:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the API:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Test health:

   Open http://localhost:8000/health

### Endpoints

- `POST /summarize` — form-data upload with field name `pdf`.
- `POST /summarize-multi` — form-data upload with multiple `pdfs` files.
- `GET /health` — health check.

### Notes

- Uses `pypdf` to extract text.
- Calls Anthropic Claude (3.5 Sonnet) and requests strict JSON. Has a robust fallback if the model returns non-strict output.
- CORS allowed origin is set via `CORS_ORIGINS` in `.env` (defaults to `http://localhost:5173` for the React dev server).
