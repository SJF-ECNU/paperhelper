from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, ApplicationContext, get_context
from app.config import Settings


class DummyContext(ApplicationContext):
    def __init__(self):
        settings = Settings(storage_path=Path("./test-storage"))
        super().__init__(settings)


def override_context() -> DummyContext:
    return DummyContext()


def test_upload_and_fetch_document(tmp_path: Path):
    app.dependency_overrides[get_context] = override_context
    client = TestClient(app)

    file_path = tmp_path / "paper.md"
    file_path.write_text("# Title\nContent about science and research.")
    with file_path.open("rb") as file_handle:
        response = client.post("/api/documents", files={"file": ("paper.md", file_handle, "text/markdown")})
    assert response.status_code == 200
    doc_id = response.json()["id"]

    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["status"] in {"processing", "completed"}

    app.dependency_overrides.clear()
