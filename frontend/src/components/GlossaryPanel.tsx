import React from 'react';
import { DocumentArtifacts } from '../api/client';

interface GlossaryPanelProps {
  artifacts: DocumentArtifacts;
}

export const GlossaryPanel: React.FC<GlossaryPanelProps> = ({ artifacts }) => (
  <section>
    <h2>Glossary</h2>
    <table className="glossary-table">
      <thead>
        <tr>
          <th>Term</th>
          <th>Definition</th>
          <th>References</th>
        </tr>
      </thead>
      <tbody>
        {artifacts.glossary.map((entry) => (
          <tr key={entry.term}>
            <td>{entry.term}</td>
            <td>{entry.definition}</td>
            <td>{entry.references.join(', ')}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </section>
);
