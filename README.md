# KnackWit Frontend

React dashboard for the KnackWit AI recruitment pipeline. Upload resumes, parse job descriptions, and view ranked candidates with hidden-genius analysis.

## Tech Stack

- React 19 + TypeScript
- Vite
- Tailwind CSS
- Zustand (state)
- Axios (API)
- Framer Motion, Recharts

## Prerequisites

- Node.js 18+
- Backend running at `http://localhost:8000` (see `fastapi/README.md` in the main repo)

## Setup

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

In development, API calls go to `/api/v1` and Vite proxies them to the backend (`vite.config.ts`). No CORS setup is required on the backend for local dev.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (port 5173) |
| `npm run build` | Production build → `dist/` |
| `npm run preview` | Preview production build |

## Usage

1. **Upload resumes** — Sidebar → Upload JD / Resumes → Resumes tab. PDF or TXT, up to 50 files. Waits for Celery indexing to finish.
2. **Parse JD & search** — Job Description tab. Upload a JD PDF or paste text, then **Parse JD & Search Candidates**.
3. **View results** — Dashboard shows ranked candidates, stats, and analytics.
4. **Candidate detail** — Click a candidate for full analysis (scores, skills, strengths, gaps).

## Environment

Optional `.env` in this folder:

```env
VITE_API_BASE_URL=/api/v1
```

For production, set this to your deployed API URL (e.g. `https://api.example.com/api/v1`).

## Project Structure

```
src/
├── components/   # UI (dashboard, candidates, charts, modals)
├── hooks/        # Zustand store + API actions
├── lib/          # Axios API client
├── pages/        # Landing + Dashboard
└── types/        # TypeScript interfaces
```

## Backend API (used by this app)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/ingest/process-files` | Bulk resume upload |
| `POST /api/v1/ingest/tasks-status` | Poll Celery task status |
| `POST /api/v1/ingest/parse-jd` | Parse JD from PDF |
| `POST /api/v1/ingest/parse-jd-text` | Parse JD from text |
| `POST /api/v1/match/search-candidates` | Rank candidates against JD |
| `GET /api/v1/match/candidates/{id}` | Candidate profile |
| `GET /api/v1/candidate/{id}/analysis` | Hidden genius analysis |
