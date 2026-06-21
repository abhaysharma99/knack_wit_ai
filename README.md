# Fast-GPT — Document Ingestion & JD Intelligence Pipeline

A FastAPI + Celery service for ingesting documents and extracting structured
intelligence from job descriptions using Google Gemini.

## Features

- **Document ingestion** — upload a file, chunk it semantically (via Gemini),
  and persist chunks to Postgres for downstream search/embedding.
- **JD Intelligence Engine (Module 1)** — upload a job description (PDF or
  raw text) and get back clean, structured JSON: role, required/preferred
  skills, experience, domain, and seniority.

## Tech Stack

- **API:** FastAPI
- **Async tasks:** Celery + Redis (broker & result backend)
- **Database:** PostgreSQL (via SQLAlchemy)
- **LLM:** Google Gemini (`gemini-2.5-flash`)
- **Containerization:** Docker Compose

## Project Structure

```
fastapi/
├── app/
│   ├── api/v1/
│   │   └── ingest.py        # API routes: /process-file, /parse-jd, task status
│   ├── db/
│   │   ├── crud.py          # DB read/write helpers
│   │   └── models.py        # SQLAlchemy models (File, Chunk)
│   ├── celery_worker.py     # Celery app + process_file_task
│   ├── chunker.py           # Gemini-based semantic document chunking
│   ├── jd_parser.py         # Gemini-based JD -> structured JSON (Module 1)
│   ├── schemas.py           # Pydantic models (Chunk, ChunkResponse, JDStructured)
│   ├── settings.py          # Env-driven config
│   ├── utils.py             # Text helpers (paragraph splitting)
│   └── main.py              # FastAPI app entrypoint
├── data/
│   └── uploads/             # Local file storage (gitignored)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- A free Gemini API key — [get one here](https://aistudio.google.com/apikey)

### Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd fastapi
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your own `GEMINI_API_KEY`. **Never commit `.env`** —
   it's already gitignored. Each teammate should use their own key.

3. **Build and run**
   ```bash
   docker compose up --build
   ```
   This starts four services: `fastapi`, `celery`, `redis`, `postgres`.

4. **Verify it's running**
   API will be available at `http://localhost:8000`.

> **Note:** If you change `requirements.txt`, you must rebuild with
> `docker compose up --build` — a plain `docker compose up` reuses the old
> image and won't pick up new dependencies.

## API Endpoints

### `POST /api/v1/ingest/process-file`

Uploads a file for chunking and storage. Runs asynchronously via Celery.

**Form fields:** `file` (required), `param1` (str), `param2` (int), `src` (str, default `"web"`)

**Response:**
```json
{ "file_id": "...", "task_id": "...", "status": "submitted" }
```

### `GET /api/v1/ingest/{task_id}`

Fetch the status/result of a submitted task.

### `DELETE /api/v1/ingest/{task_id}`

Remove a task record.

### `POST /api/v1/ingest/parse-jd`

**Module 1 — JD Intelligence Engine.** Accepts a PDF file *or* raw text and
returns structured JSON. Runs synchronously (no Celery queue needed — it's a
single fast LLM call).

**Form fields (provide one):**
- `file` — a `.pdf` upload, OR
- `text` — raw job description text

**Example (raw text):**
```bash
curl -X POST http://localhost:8000/api/v1/ingest/parse-jd \
  -F "text=We are hiring an AI Engineer with 3+ years experience in PyTorch and LLMs. AWS and Docker preferred."
```

**Example (PDF):**
```bash
curl -X POST http://localhost:8000/api/v1/ingest/parse-jd \
  -F "file=@/path/to/job_description.pdf"
```

**Response:**
```json
{
  "role": "AI Engineer",
  "required_skills": ["PyTorch", "LLMs"],
  "preferred_skills": ["AWS", "Docker"],
  "experience_years": 3,
  "domain": "Machine Learning",
  "seniority": "Mid-Senior"
}
```

## Gemini Model Notes

This project uses `gemini-2.5-flash`. As of April 2026, Google moved Pro-tier
models behind billing — **only Flash and Flash-Lite remain free**. If you hit
a `429 RESOURCE_EXHAUSTED` error with `limit: 0`, check `GEMINI_MODEL` in your
`.env` is set to a Flash model, not Pro.

## Contributing (Team Workflow)

1. Pull latest `main` before starting work.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit with clear messages.
4. Open a PR into `main` for review before merging.
5. Never commit `.env`, `__pycache__/`, `.idea/`, or anything under `data/uploads/`.

## License

Internal hackathon/team project — add a license here if needed.
