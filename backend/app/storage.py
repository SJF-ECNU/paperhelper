from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .models import DocumentArtifacts, DocumentRecord


class StorageManager:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text("{}", encoding="utf-8")

    def _read(self) -> Dict[str, dict]:
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _write(self, data: Dict[str, dict]) -> None:
        self.db_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def save_record(self, record: DocumentRecord) -> None:
        data = self._read()
        data[record.id] = record.to_dict()
        self._write(data)

    def get_record(self, doc_id: str) -> Optional[DocumentRecord]:
        data = self._read()
        record_data = data.get(doc_id)
        if not record_data:
            return None
        return DocumentRecord.from_dict(record_data)

    def list_records(self) -> Dict[str, DocumentRecord]:
        data = self._read()
        return {doc_id: DocumentRecord.from_dict(payload) for doc_id, payload in data.items()}
