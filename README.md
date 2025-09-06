# Legal PDF Summarizer with Claude and React

A simple full-stack app:
- **Frontend (React + Vite)**: Upload a legal opinion PDF and view the summary.
- **Backend (FastAPI)**: Extract text from the PDF, call Anthropic Claude to summarize, and return JSON.

## Screenshots (sample)
- Upload view: shows a file picker and Summarize button with loading spinner.
- Result view: shows Title, Tags, and Summary with Copy/Download buttons.

## Project Structure

```
legal-pdf-summarizer/
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ main.jsx
│  │  └─ styles.css
│  ├─ index.html
│  ├─ package.json
│  ├─ vite.config.js
│  └─ .env.example
└─ backend/
   ├─ app/
   │  └─ main.py
   ├─ requirements.txt
   ├─ .env.example
   └─ README.md
```

## Setup

### Backend
1) Create `backend/.env` from `.env.example` and set `ANTHROPIC_API_KEY`.
2) Create a venv and install:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3) Verify: open http://localhost:8000/health

### Frontend
1) Copy `.env.example` to `.env` and set `VITE_API_BASE` to your backend (default `http://localhost:8000`).
2) Install and run:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3) Open http://localhost:5173

## Usage
- Select a `.pdf` and click **Summarize PDF**.
- The backend extracts text (via `pypdf`), calls **Claude 3.5 Sonnet**, and returns JSON `{ title, summary, tags }`.
- The UI renders the summary and allows Copy/Download.

## Notes & Assumptions
- The backend trims very long inputs (`MAX_INPUT_CHARS=120_000`) for safety.
- Claude is asked to return strict JSON; robust fallback parsing covers non-compliant outputs.
- Errors return meaningful messages (400 for bad file, 502 for upstream API failures, etc.).

## Multi-file Bonus
- POST `/summarize-multi` with multiple `pdfs` files to receive an array of per-file results.

## Environment Examples
- `backend/.env.example` and `frontend/.env.example` included.

## Testing
- Try with any public U.S. legal opinion PDF.

## Security
- Keep your Anthropic API key **server-side** only.
- Consider request size limits, rate-limiting, and authentication for production.

## License
MIT
