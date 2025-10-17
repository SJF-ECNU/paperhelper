import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'react-flow-renderer';
import { DocumentArtifacts } from '../api/client';

interface MindMapPanelProps {
  artifacts: DocumentArtifacts;
}

export const MindMapPanel: React.FC<MindMapPanelProps> = ({ artifacts }) => {
  const nodes = useMemo<Node[]>(
    () =>
      artifacts.mind_map.nodes.map((node, index) => ({
        id: node.id,
        position: { x: index * 160, y: (index % 3) * 120 },
        data: { label: `${node.label} (${node.weight.toFixed(2)})` },
        style: {
          padding: '12px 16px',
          borderRadius: '12px',
          background: '#eef2ff',
          border: '1px solid #6366f1',
        },
      })),
    [artifacts.mind_map.nodes],
  );

  const edges = useMemo<Edge[]>(
    () =>
      artifacts.mind_map.edges.map((edge) => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        label: `Weight ${edge.weight.toFixed(2)}`,
        type: 'smoothstep',
      })),
    [artifacts.mind_map.edges],
  );

  return (
    <section style={{ height: 400 }}>
      <h2>Mind Map</h2>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background variant="dots" gap={16} size={1} />
        <MiniMap />
        <Controls />
      </ReactFlow>
    </section>
  );
};
