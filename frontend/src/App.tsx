import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  DocumentArtifacts,
  DocumentRecord,
  fetchArtifacts,
  fetchDocument,
  uploadDocument,
} from './api/client';
import { UploadPanel } from './components/UploadPanel';
import { ProgressPanel } from './components/ProgressPanel';
import { SummaryPanel } from './components/SummaryPanel';
import { GlossaryPanel } from './components/GlossaryPanel';
import { MindMapPanel } from './components/MindMapPanel';

const POLLING_INTERVAL = 2500;

type ActiveTab = 'summary' | 'glossary' | 'mindmap';

const App: React.FC = () => {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('summary');
  const queryClient = useQueryClient();

  const { data: document } = useQuery<DocumentRecord | null>(
    ['document', documentId],
    () => (documentId ? fetchDocument(documentId) : Promise.resolve(null)),
    {
      enabled: Boolean(documentId),
      refetchInterval: (data) =>
        data?.status && ['completed', 'failed'].includes(data.status) ? false : POLLING_INTERVAL,
    },
  );

  const { data: artifacts } = useQuery<DocumentArtifacts | null>(
    ['artifacts', documentId],
    () => (documentId ? fetchArtifacts(documentId) : Promise.resolve(null)),
    {
      enabled: Boolean(documentId && document?.status === 'completed'),
    },
  );

  const mutation = useMutation(uploadDocument, {
    onSuccess: (response) => {
      setDocumentId(response.id);
      queryClient.invalidateQueries({ queryKey: ['document', response.id] });
    },
  });

  const handleUpload = useCallback(
    (file: File) => {
      setActiveTab('summary');
      mutation.mutate(file);
    },
    [mutation],
  );

  useEffect(() => {
    if (document?.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['artifacts', document.id] });
    }
  }, [document, queryClient]);

  const isUploading = mutation.isPending;

  const canShowArtifacts = useMemo(() => document?.status === 'completed' && artifacts, [document, artifacts]);

  return (
    <div className="app-container">
      <header>
        <h1>PaperHelper</h1>
        <p>Upload a paper to receive a summary, glossary, and mind map generated locally.</p>
      </header>
      <UploadPanel onUpload={handleUpload} disabled={isUploading} />
      <ProgressPanel document={document} />

      {canShowArtifacts && artifacts && (
        <section>
          <div className="tabs">
            <button
              type="button"
              className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              Summary
            </button>
            <button
              type="button"
              className={`tab-button ${activeTab === 'glossary' ? 'active' : ''}`}
              onClick={() => setActiveTab('glossary')}
            >
              Glossary
            </button>
            <button
              type="button"
              className={`tab-button ${activeTab === 'mindmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('mindmap')}
            >
              Mind Map
            </button>
          </div>

          {activeTab === 'summary' && <SummaryPanel artifacts={artifacts} />}
          {activeTab === 'glossary' && <GlossaryPanel artifacts={artifacts} />}
          {activeTab === 'mindmap' && <MindMapPanel artifacts={artifacts} />}
        </section>
      )}
    </div>
  );
};

export default App;
