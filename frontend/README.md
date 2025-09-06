# Frontend (React + Vite) — Legal PDF Summarizer

## Quickstart

```bash
npm install
npm run dev
```

The dev server runs on http://localhost:5173. To point it at your API, create `.env` from `.env.example` and adjust `VITE_API_BASE`.

## Features

- PDF upload and POST to `/summarize`
- Spinner while summarizing
- Displays title, tags, and multi-paragraph summary
- Copy and Download buttons
