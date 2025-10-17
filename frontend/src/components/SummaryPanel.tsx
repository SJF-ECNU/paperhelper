import React from 'react';
import { DocumentArtifacts } from '../api/client';

interface SummaryPanelProps {
  artifacts: DocumentArtifacts;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ artifacts }) => (
  <section>
    <h2>Summary</h2>
    <div className="summary-block">{artifacts.summary}</div>
  </section>
);
