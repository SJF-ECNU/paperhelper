from __future__ import annotations


from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MindMapNode:
    id: str
    label: str
    weight: float = 1.0


@dataclass
class MindMapEdge:
    source: str
    target: str
    weight: float = 1.0


@dataclass
class MindMap:
    nodes: List[MindMapNode] = field(default_factory=list)
    edges: List[MindMapEdge] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MindMap:
        nodes = [MindMapNode(**node) for node in data.get("nodes", [])]
        edges = [MindMapEdge(**edge) for edge in data.get("edges", [])]
        return cls(nodes=nodes, edges=edges)


@dataclass
class GlossaryEntry:
    term: str
    definition: str
    score: float
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GlossaryEntry:
        return cls(**data)


@dataclass
class DocumentArtifacts:
    summary: str
    mind_map: MindMap
    glossary: List[GlossaryEntry]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "mind_map": self.mind_map.to_dict(),
            "glossary": [entry.to_dict() for entry in self.glossary],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DocumentArtifacts:
        mind_map = MindMap.from_dict(data.get("mind_map", {}))
        glossary = [GlossaryEntry.from_dict(item) for item in data.get("glossary", [])]
        return cls(summary=data.get("summary", ""), mind_map=mind_map, glossary=glossary)


@dataclass
class DocumentRecord:
    id: str
    filename: str
    storage_path: Path
    status: DocumentStatus = DocumentStatus.PENDING
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    artifacts: Optional[DocumentArtifacts] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "filename": self.filename,
            "storage_path": str(self.storage_path),
            "status": self.status.value,
            "uploaded_at": self.uploaded_at.isoformat(),
            "error": self.error,
            "metadata": self.metadata,
        }
        if self.artifacts:
            payload["artifacts"] = self.artifacts.to_dict()
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DocumentRecord:
        artifacts = data.get("artifacts")
        record_artifacts = DocumentArtifacts.from_dict(artifacts) if artifacts else None
        return cls(
            id=data["id"],
            filename=data["filename"],
            storage_path=Path(data["storage_path"]),
            status=DocumentStatus(data.get("status", "pending")),
            uploaded_at=datetime.fromisoformat(data["uploaded_at"]) if "uploaded_at" in data else datetime.utcnow(),
            error=data.get("error"),
            artifacts=record_artifacts,
            metadata=data.get("metadata", {}),
        )
