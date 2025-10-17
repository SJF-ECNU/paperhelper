import React, { useCallback, useRef, useState } from 'react';

interface UploadPanelProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

const ACCEPTED_TYPES = ['application/pdf', 'text/markdown', 'text/plain'];

export const UploadPanel: React.FC<UploadPanelProps> = ({ onUpload, disabled = false }) => {
  const [isDragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;
      const file = files[0];
      onUpload(file);
    },
    [onUpload],
  );

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      if (disabled) return;
      setDragging(false);
      handleFiles(event.dataTransfer.files);
    },
    [disabled, handleFiles],
  );

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (disabled) return;
    setDragging(true);
  }, [disabled]);

  const onDragLeave = useCallback(() => {
    if (!disabled) {
      setDragging(false);
    }
  }, [disabled]);

  const onButtonClick = useCallback(() => {
    if (!disabled) {
      inputRef.current?.click();
    }
  }, [disabled]);

  return (
    <section>
      <h2>Upload a Paper</h2>
      <p>Drag and drop a PDF or Markdown file, or use the button below.</p>
      <div
        className={`upload-area ${isDragging ? 'drag-active' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        role="presentation"
      >
        <p>Drop your paper here</p>
        <button className="button-primary" onClick={onButtonClick} disabled={disabled} type="button">
          Select a file
        </button>
        <p style={{ fontSize: '0.9rem', color: '#718096' }}>PDF, Markdown, or Text — max 25MB</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(',')}
          style={{ display: 'none' }}
          onChange={(event) => handleFiles(event.target.files)}
          disabled={disabled}
        />
      </div>
    </section>
  );
};
