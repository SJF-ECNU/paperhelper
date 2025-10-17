import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
});

export interface DocumentRecord {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string | null;
  metadata: Record<string, string>;
  artifacts?: DocumentArtifacts | null;
}

export interface MindMapNode {
  id: string;
  label: string;
  weight: number;
}

export interface MindMapEdge {
  source: string;
  target: string;
  weight: number;
}

export interface GlossaryEntry {
  term: string;
  definition: string;
  score: number;
  references: string[];
}

export interface DocumentArtifacts {
  summary: string;
  mind_map: {
    nodes: MindMapNode[];
    edges: MindMapEdge[];
  };
  glossary: GlossaryEntry[];
}

export interface UploadResponse extends DocumentRecord {}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<UploadResponse>('/api/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function fetchDocument(id: string): Promise<DocumentRecord> {
  const { data } = await api.get<DocumentRecord>(`/api/documents/${id}`);
  return data;
}

export async function fetchArtifacts(id: string): Promise<DocumentArtifacts> {
  const { data } = await api.get<DocumentArtifacts>(`/api/documents/${id}/mindmap`);
  return data;
}
