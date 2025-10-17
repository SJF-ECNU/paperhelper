from __future__ import annotations


from pathlib import Path
from typing import Dict

from fastapi import BackgroundTasks, Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .models import DocumentArtifacts, DocumentRecord, DocumentStatus
from .storage import StorageManager
from .utils import ParsedDocument, generate_document_id, load_document
from .workflow.nodes import PaperAnalysisWorkflow, WorkflowState

app = FastAPI(title="PaperHelper API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApplicationContext:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.storage = StorageManager(settings.storage_path / "paperhelper.json")
        self.workflow = PaperAnalysisWorkflow()


@app.on_event("startup")
async def startup_event() -> None:
    get_settings()


def get_context(settings: Settings = Depends(get_settings)) -> ApplicationContext:
    return ApplicationContext(settings)


def _derive_storage_name(upload: UploadFile) -> str:
    """Return a sanitized filename for the uploaded file."""

    original = upload.filename or ""
    sanitized = Path(original).name
    sanitized = sanitized.strip()
    if not sanitized:
        sanitized = f"upload-{generate_document_id()}"
    return sanitized


def _persist_uploaded_file(upload: UploadFile, storage_dir: Path) -> Path:
    storage_dir.mkdir(parents=True, exist_ok=True)
    safe_name = _derive_storage_name(upload)
    file_path = storage_dir / safe_name
    with file_path.open("wb") as f:
        f.write(upload.file.read())
    return file_path


def _process_document(doc_id: str, parsed: ParsedDocument, context: ApplicationContext) -> DocumentArtifacts:
    state = WorkflowState(document_id=doc_id, filename=doc_id, sections=parsed.sections)
    return context.workflow.run(state)


def _store_artifacts(doc_id: str, artifacts: DocumentArtifacts, context: ApplicationContext) -> None:
    record = context.storage.get_record(doc_id)
    if not record:
        raise RuntimeError(f"Document {doc_id} not found for storage update")
    record.status = DocumentStatus.COMPLETED
    record.artifacts = artifacts
    context.storage.save_record(record)


def _update_record_status(doc_id: str, status: DocumentStatus, context: ApplicationContext, error: str | None = None) -> None:
    record = context.storage.get_record(doc_id)
    if not record:
        return
    record.status = status
    record.error = error
    context.storage.save_record(record)


async def _analyze_document(doc_id: str, file_path: Path, context: ApplicationContext) -> None:
    try:
        parsed = load_document(file_path)
        artifacts = _process_document(doc_id, parsed, context)
        _store_artifacts(doc_id, artifacts, context)
    except Exception as exc:  # noqa: BLE001
        _update_record_status(doc_id, DocumentStatus.FAILED, context, error=str(exc))
        raise


@app.post("/api/documents")
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    context: ApplicationContext = Depends(get_context),
) -> DocumentRecord:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    doc_id = generate_document_id()
    storage_dir = context.settings.storage_path / doc_id
    file_path = _persist_uploaded_file(file, storage_dir)
    parsed = load_document(file_path)

    record = DocumentRecord(
        id=doc_id,
        filename=file_path.name,
        storage_path=file_path,
        status=DocumentStatus.PROCESSING,
        metadata={"content_length": str(len(parsed.text))},
    )
    context.storage.save_record(record)
    background.add_task(_analyze_document, doc_id, file_path, context)
    return record


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str, context: ApplicationContext = Depends(get_context)) -> DocumentRecord:
    record = context.storage.get_record(doc_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return record


@app.get("/api/documents/{doc_id}/mindmap")
async def get_mindmap(doc_id: str, context: ApplicationContext = Depends(get_context)) -> DocumentArtifacts:
    record = context.storage.get_record(doc_id)
    if not record or not record.artifacts:
        raise HTTPException(status_code=404, detail="Artifacts not available")
    return record.artifacts


@app.get("/api/documents")
async def list_documents(context: ApplicationContext = Depends(get_context)) -> Dict[str, DocumentRecord]:
    return context.storage.list_records()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
