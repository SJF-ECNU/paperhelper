import React, { useMemo } from 'react';
import { DocumentRecord } from '../api/client';

interface ProgressPanelProps {
  document?: DocumentRecord | null;
}

const statusMessages: Record<DocumentRecord['status'], string> = {
  pending: 'Queued for processing…',
  processing: 'Analyzing document…',
  completed: 'Analysis completed!',
  failed: 'Processing failed. Please try again.',
};

export const ProgressPanel: React.FC<ProgressPanelProps> = ({ document }) => {
  const fill = useMemo(() => {
    switch (document?.status) {
      case 'pending':
        return 0.2;
      case 'processing':
        return 0.6;
      case 'completed':
        return 1;
      case 'failed':
        return 1;
      default:
        return 0;
    }
  }, [document?.status]);

  return (
    <section>
      <h2>Status</h2>
      <p>{document ? statusMessages[document.status] : 'Upload a document to begin analysis.'}</p>
      <div className="progress-bar">
        <div className="fill" style={{ width: `${fill * 100}%` }} />
      </div>
      {document?.error && (
        <p style={{ color: '#e53e3e', marginTop: '0.5rem' }}>Error: {document.error}</p>
      )}
    </section>
  );
};
