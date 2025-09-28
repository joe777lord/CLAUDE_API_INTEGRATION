# ---------- Build stage: install deps via Poetry ----------
    FROM python:3.11-slim AS backend-build

    ENV POETRY_VERSION=1.8.3 \
        POETRY_VIRTUALENVS_CREATE=false \
        PIP_NO_CACHE_DIR=1
    
    # System deps (pypdf sometimes needs libxml2/libxslt for funky PDFs; curl for health/debug)
    RUN apt-get update && apt-get install -y --no-install-recommends \
          build-essential curl libxml2 libxslt1.1 \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Poetry
    RUN curl -sSL https://install.python-poetry.org | python3 -
    
    ENV PATH="/root/.local/bin:${PATH}"
    
    WORKDIR /app
    
    # Copy only dependency files first (better layer caching)
    COPY pyproject.toml poetry.lock* ./
    
    # Install dependencies (no dev)
    RUN poetry install --no-root --only main
    
    # ---------- Runtime stage ----------
    FROM python:3.11-slim
    
    # (Optional) add same libs as build image if needed at runtime
    RUN apt-get update && apt-get install -y --no-install-recommends \
          libxml2 libxslt1.1 \
        && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # Copy installed site-packages and binaries from build stage
    COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
    COPY --from=backend-build /usr/local/bin /usr/local/bin
    
    # Copy your source
    COPY app ./app
    
    # Env (override at runtime)
    ENV HOST=0.0.0.0 \
        PORT=8000 \
        CORS_ORIGINS=http://localhost:5173
    
    # Expose API port
    EXPOSE 8000
    
    # HEALTHCHECK (optional)
    HEALTHCHECK --interval=30s --timeout=3s --retries=5 CMD curl -fsS http://localhost:8000/health || exit 1
    
    # Start FastAPI
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    