# PaperHelper Backend

This FastAPI backend powers the PaperHelper application. It accepts document uploads, orchestrates a lightweight analysis workflow, and stores generated artifacts.

## Features
- Document upload endpoint with validation
- LangGraph-inspired workflow producing summary, mind map JSON, and glossary
- SQLite persistence via SQLModel
- Configurable via environment variables
- Automated tests covering utilities, workflow, and API endpoints

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest
```

## Configuration

Environment variables are loaded from `.env` with the `PAPERHELPER_` prefix. Key settings include:

- `PAPERHELPER_STORAGE_PATH`: Directory for uploads, database, and cached artifacts.
- `PAPERHELPER_MODEL_NAME`: Default LLM identifier for downstream integrations.
- `PAPERHELPER_EMBEDDING_MODEL`: Embedding model alias.
- `PAPERHELPER_MAX_WORKERS`: Maximum background workers for workflow execution.
- `PAPERHELPER_OPENAI_BASE_URL`: Base URL for OpenAI-compatible endpoints.
- `PAPERHELPER_OPENAI_API_KEY`: API key for remote LLMs (optional for offline mode).
