# PaperHelper

PaperHelper is a local-first application that analyzes academic papers and returns a concise summary, interactive mind map, and glossary of key concepts. The project follows the architecture outlined in `plan.md`, pairing a FastAPI backend with a Vite + React frontend.

## Repository Structure

```
plan.md
backend/        # FastAPI service orchestrating ingestion, workflow, and persistence
frontend/       # React application for uploads, progress, and artifact visualization
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend to run on `http://localhost:8000`. You can configure an alternative base URL via the `VITE_API_BASE_URL` environment variable.

## Testing

Backend tests are implemented with `pytest`:

```bash
cd backend
pytest
```

## LangGraph-inspired Workflow

The backend implements a modular workflow with the following stages:

1. **Ingestion** — validates and loads PDF/Markdown files.
2. **Chunking** — keeps structural sections intact using recursive chunking.
3. **Embedding** — generates deterministic bag-of-words embeddings suitable for local experimentation.
4. **Summary** — extracts representative sentences for a quick overview.
5. **Mind Map** — builds a lightweight graph connecting salient keywords.
6. **Glossary** — produces short definitions and references to source sections.
7. **Synthesis** — bundles artifacts for downstream consumption.

Each stage can be extended to integrate real LLMs or improved heuristics while retaining offline compatibility.

## Documentation

Additional details are available in:

- `backend/README.md` — backend setup and configuration guide.
- `frontend/README.md` — frontend usage instructions and component overview.

## Roadmap

Future enhancements include richer vector search, model adapters for local LLM runners, and end-to-end smoke tests using mocked LLM responses.
