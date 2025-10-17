# Paper Analysis Agent — Plan

## 1. Overview
Goal: local web app that accepts academic papers, runs a LangGraph-powered agentic workflow, and returns (a) overall summary, (b) mind map of key ideas, (c) glossary of fundamental concepts. Focus on PDF/Markdown inputs, modular design, and offline-friendly LLM/tool selection.

## 2. Success Criteria
- Upload (drag/drop) a paper and receive the three analysis artifacts within target latency (<3 min for 20-page PDF).
- End-to-end workflow fully local (no external network calls unless explicitly configured).
- Frontend renders mind map interactively and supports exporting summary/glossary.
- Automated tests cover graph execution, parsing, and frontend data handling.
- Documentation explains setup, usage, and extension points.

## 3. Constraints & Assumptions
- Runtime: Python 3.10+, Node 18+ (for frontend build tooling).
- Base models: configurable; default to locally hosted LLM via Ollama or similar.
- Paper formats: prioritize PDF, optionally support Markdown/TXT.
- LangGraph orchestrates tool nodes; underlying embeddings/vector store must also run locally (e.g., Chroma, FAISS).

## 4. Architecture Sketch
- Frontend: React/Vite with drag-and-drop upload, progress indicator, results sections, mind map visualization (e.g., React Flow or D3).
- Backend API (FastAPI/Quart): handles uploads, invokes LangGraph workflow, streams status.
- LangGraph Workflow: orchestrates ingestion → chunking → LLM-powered analyses → post-processing → storage.
- Storage: local cache for processed documents, vector store for semantic retrieval.
- Utilities: PDF text extractor (pymupdf/pdfminer) and metadata parser.

## 5. Detailed Task Breakdown

### 5.1 Project Scaffolding
- [ ] Create Python backend project with virtual environment, dependency management (poetry/pip-tools).
- [ ] Initialize frontend with Vite + React + TypeScript; configure shared types folder.
- [ ] Set up repo tooling: pre-commit, linting (ruff, eslint), formatting (black, prettier).

### 5.2 Environment & Config
- [ ] Define `.env` template covering model selection, storage paths, concurrency settings.
- [ ] Implement configuration loader with validation (pydantic settings).
- [ ] Provide scripts for setting up local LLM (e.g., Ollama model pull) and embedding model download.
- [ ] ensure .env template reflects OpenAI endpoint settings and per-model knobs (temperature, max tokens).

### 5.3 Document Ingestion Pipeline
- [ ] Implement upload endpoint storing files in temp dir and queuing for processing; enforce the same file validation (size, type) server-side within the future `POST /api/documents` handler before queuing.
- [ ] Build PDF/Markdown loader with fallback OCR hook (placeholder).
- [ ] Normalize text: split into sections, maintain structure (headings, figure captions).
- [ ] Persist raw text + metadata for reuse.

### 5.4 LangGraph Workflow Design
- [ ] Define state schema (document metadata, sections, intermediate artifacts).
- [ ] Create nodes:
  - `IngestionNode`: wraps loader, produces structured document.
  - `ChunkingNode`: splits text with sentence-aware chunker.
  - `EmbeddingNode`: creates embeddings, loads into vector store.
  - `SummaryNode`: orchestrated LLM calls for abstract-level summary + section summaries.
  - `MindMapNode`: extracts key concepts/relationships and outputs graph JSON.
  - `GlossaryNode`: identifies fundamental concepts with concise explanations and references.
  - `SynthesisNode`: composes outputs, ensures consistency, attaches supporting quotes.
- [ ] Configure conditional branches for multilingual handling / fallback prompts.
- [ ] Add logging + tracing (LangSmith optional, or local logging) for observability.

### 5.5 LLM & Tooling Integration
- [ ] Implement adapter layer supporting multiple LLM backends (Ollama, OpenAI-compatible).
- [ ] Define prompts/templates for each node with clear instructions.
- [ ] Create rate limiting & timeout safeguards; add retry logic with exponential backoff.

### 5.6 Post-processing & Validation
- [ ] Summaries: enforce target length, highlight contributions, limitations.
- [ ] Mind map: convert extracted relationships into hierarchical structure (nodes/edges), ensure JSON schema validation.
- [ ] Glossary: deduplicate terms, include definition, related sections, external references placeholder.
- [ ] Quality checks: verify each artifact references source sections; compute confidence scores.
- [ ] lock adapter to OpenAI-compatible REST interface; document env vars OPENAI_BASE_URL, OPENAI_API_KEY, model aliases; add tests with mocked OpenAI responses.

### 5.7 Backend API Layer
- [ ] REST endpoints:
  - `POST /api/documents`: upload + start processing.
  - `GET /api/documents/{id}`: fetch status/results.
  - `GET /api/documents/{id}/mindmap`: serve mind map JSON.
- [ ] Websocket or Server-Sent Events for progress updates.
- [ ] Background task runner (Celery, asyncio queue, or LangGraph async executor).
- [ ] Error handling, retries, cleanup of temporary files.

### 5.8 Frontend Implementation
- [ ] UI layout: upload panel, processing indicator, result tabs.
- [ ] Integrate drag-and-drop and file validation (size, type).
- [ ] Summary view with export (Markdown/PDF).
- [ ] Glossary table with search/filter.
- [ ] Mind map visualization (React Flow): render nodes/edges, support expand/collapse.
- [ ] Hook into API for polling/streaming; display error states and retry options.

### 5.9 Persistence & Caching
- [ ] Implement document registry (SQLite/JSON) mapping file hash to artifacts.
- [ ] Allow reloading previous analyses without recomputation.
- [ ] Manage storage cleanup policy.
- [ ] adopt SQLite (via SQLModel/SQLAlchemy Lite); define schema for documents, chunks, artifacts, runs; add migration/bootstrap scripts; wire cleanup & caching to DB; expose DB path in config.

### 5.10 Testing Strategy
- [ ] Unit tests for text extraction, chunking, prompt builders, graph schema validation.
- [ ] Integration tests simulating full pipeline with mocked LLM responses.
- [ ] Frontend component tests (Vitest + Testing Library).
- [ ] End-to-end smoke test invoking backend workflow with sample paper.
- [ ] include fixtures seeding SQLite, verifying retrieval/caching logic, and mocking OpenAI API calls.

### 5.11 Observability & Tooling
- [ ] Structured logging for each LangGraph node.
- [ ] Optional CLI to run analysis headlessly (for testing).
- [ ] Benchmark script measuring processing time across document sizes.

### 5.12 Documentation
- [ ] `README` covering setup, running backend/frontend, configuring models.
- [ ] Architecture doc describing LangGraph design and data flow.
- [ ] Usage guide with screenshots and troubleshooting tips.
- [ ] Developer guide for extending nodes or swapping models.

### 5.13 Packaging & Local Deployment
- [ ] Docker Compose (optional) wiring backend, frontend, vector store.
- [ ] Provide `make` or task runner scripts for common commands (install, test, dev, build).
- [ ] Final verification checklist before release.

## 6. Risks & Mitigations
- Model quality variance → allow plugging in stronger LLMs; add prompt guardrails.
- Mind map accuracy → add heuristic validation and optional manual editing.
- Large PDFs → chunking tuned for memory; stream processing to avoid loading entire doc.
- Frontend performance → virtualize large mind maps.
- Offline constraints → document how to preload models and dependencies.

## 7. Stretch Goals
- Interactive Q&A over paper with retrieval.
- Citation-aware summaries referencing page numbers.
- Export mind map as PNG/SVG/Mermaid.
- Multi-document comparison workspace.
- User accounts with local auth for shared machine setups.