# PaperHelper Frontend

This Vite-powered React application provides an intuitive interface for uploading academic papers and viewing the resulting analysis artifacts.

## Scripts

- `npm run dev` — start the local development server at `http://localhost:5173`.
- `npm run build` — create a production build in `dist/`.
- `npm run preview` — preview the production build locally.

## Environment Variables

- `VITE_API_BASE_URL` — optional base URL for the backend API (defaults to `http://localhost:8000`).

## Components

- `UploadPanel` — drag-and-drop upload widget with file validation guidance.
- `ProgressPanel` — displays backend processing status and errors.
- `SummaryPanel` — renders the overall summary text.
- `GlossaryPanel` — tabular view of glossary entries.
- `MindMapPanel` — interactive mind map visualization using React Flow.

## Testing

Component tests can be added using Vitest and Testing Library (not included by default).
