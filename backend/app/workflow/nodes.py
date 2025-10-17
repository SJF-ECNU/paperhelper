from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from ..models import DocumentArtifacts, GlossaryEntry, MindMap, MindMapEdge, MindMapNode
from ..utils import build_embedding, extract_keywords, summarize_sections


@dataclass
class WorkflowState:
    document_id: str
    filename: str
    sections: List[Tuple[str, str]]
    embeddings: List[List[float]] | None = None


class IngestionNode:
    def run(self, sections: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return sections


class ChunkingNode:
    def run(self, sections: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return sections


class EmbeddingNode:
    def run(self, sections: Iterable[Tuple[str, str]]) -> List[List[float]]:
        return [build_embedding(body) for _, body in sections]


class SummaryNode:
    def run(self, sections: Iterable[Tuple[str, str]]) -> str:
        return summarize_sections(sections)


class MindMapBuilderNode:
    def run(self, sections: Iterable[Tuple[str, str]]) -> MindMap:
        keywords = extract_keywords(" ".join(body for _, body in sections), top_k=12)
        nodes = [MindMapNodeModel(keyword, idx) for idx, keyword in enumerate(keywords, start=1)]
        edges: List[MindMapEdge] = []
        for idx, source in enumerate(nodes):
            for target in nodes[idx + 1 : idx + 1 + 3]:
                edges.append(MindMapEdge(source=source.id, target=target.id, weight=0.5))
        return MindMap(nodes=[node.to_dataclass() for node in nodes], edges=edges)


@dataclass
class MindMapNodeModel:
    label: str
    index: int

    @property
    def id(self) -> str:
        return f"node-{self.index}"

    def to_dataclass(self) -> MindMapNode:
        return MindMapNode(id=self.id, label=self.label, weight=max(1.0, 1.5 - self.index * 0.05))


class GlossaryNode:
    def run(self, sections: Iterable[Tuple[str, str]]) -> List[GlossaryEntry]:
        keywords = extract_keywords(" ".join(body for _, body in sections), top_k=8)
        glossary: List[GlossaryEntry] = []
        for keyword in keywords:
            references = [title for title, body in sections if keyword in body.lower()][:2]
            glossary.append(
                GlossaryEntry(
                    term=keyword.title(),
                    definition=f"Key concept related to {keyword} discovered in the document.",
                    score=1.0 - (0.05 * len(glossary)),
                    references=references,
                )
            )
        return glossary


class SynthesisNode:
    def run(self, summary: str, mind_map: MindMap, glossary: List[GlossaryEntry]) -> DocumentArtifacts:
        return DocumentArtifacts(summary=summary, mind_map=mind_map, glossary=glossary)


class PaperAnalysisWorkflow:
    def __init__(self) -> None:
        self.ingestion = IngestionNode()
        self.chunking = ChunkingNode()
        self.embedding = EmbeddingNode()
        self.summary = SummaryNode()
        self.mind_map = MindMapBuilderNode()
        self.glossary = GlossaryNode()
        self.synthesis = SynthesisNode()

    def run(self, state: WorkflowState) -> DocumentArtifacts:
        sections = self.ingestion.run(state.sections)
        sections = self.chunking.run(sections)
        embeddings = self.embedding.run(sections)
        summary = self.summary.run(sections)
        mind_map = self.mind_map.run(sections)
        glossary = self.glossary.run(sections)
        state.embeddings = embeddings
        return self.synthesis.run(summary, mind_map, glossary)


__all__ = ["PaperAnalysisWorkflow", "WorkflowState"]
