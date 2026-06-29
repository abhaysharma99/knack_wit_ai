from celery import Celery
from celery.signals import worker_ready
import logging
import io
import time
import json
import re
from app.settings import settings
from app.db.crud import save_files_and_chunks, save_candidate, save_skills, save_projects, init_db
from app.utils import simple_paragraph_split
from app.embedder import embedder
from app.vector_store import vector_store

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import pdfplumber

genai.configure(api_key=settings.GEMINI_API_KEY)
_gemini = genai.GenerativeModel(settings.GEMINI_MODEL)

celery_app = Celery(
    "ingest_worker",
    broker_url=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Silence noisy third-party loggers regardless of root log level
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logging.getLogger("pdfplumber").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

RESUME_PROMPT = """You are a resume parsing engine. Extract data from the resume below and return ONLY a valid JSON object. No markdown, no explanation, just JSON.

Return this exact structure:
{{"name": null, "email": null, "phone": null, "current_role": null, "domain": null, "seniority": "Unknown", "total_experience_years": null, "skills": [{{"name": "skill", "category": "technical"}}], "projects": [{{"title": null, "description": null, "technologies": null}}]}}

Resume:
{text}"""


def _parse_gemini_json(raw: str) -> dict | None:
    """Robustly extract JSON from Gemini response regardless of format."""
    if not raw or not raw.strip():
        return None

    cleaned = raw.strip()

    # Remove markdown fences
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```$", "", cleaned)
    cleaned = cleaned.strip()

    # Find first { and last } to extract JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end+1]
    elif start == -1:
        # No braces at all — wrap everything
        cleaned = "{" + cleaned + "}"

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning("JSON decode failed: %s — raw snippet: %s", e, raw[:150])
        return None


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    logger.info("Worker ready — initializing database tables...")
    init_db()


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from PDF or TXT."""
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text(x_tolerance=2, y_tolerance=2) or "" for page in pdf.pages]
        return "\n\n".join(pages)
    else:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1")


def parse_resume_inline(text: str) -> dict | None:
    """Call Gemini and parse resume — fully inlined, no external module dependency."""
    prompt = RESUME_PROMPT.format(text=text[:12000])

    for attempt in range(2):
        try:
            response = _gemini.generate_content(
                prompt,
                generation_config=GenerationConfig(temperature=0.0),
            )
            raw = response.text
            logger.info("Gemini raw response (first 200): %s", raw[:200])

            result = _parse_gemini_json(raw)
            if result:
                logger.info(
                    "Resume parsed: name=%s skills=%d",
                    result.get("name"), len(result.get("skills", []))
                )
                return result
            else:
                logger.warning("Attempt %d: could not parse JSON from Gemini response", attempt + 1)

        except Exception as e:
            logger.warning("Gemini attempt %d failed: %s", attempt + 1, e)

        # Rate limit sleep between attempts
        time.sleep(35)

    return None


@celery_app.task
def process_file_task(
    file_bytes_hex: str,
    file_path: str,
    src: str = "resume",
    filename: str = "resume.txt",
):
    try:
        file_bytes = bytes.fromhex(file_bytes_hex)
        logger.info("Received file: %s, size: %d bytes", filename, len(file_bytes))

        # Extract text
        text = extract_text(file_bytes, filename)
        if not text.strip():
            return {"status": "error", "error": "Could not extract text from file"}
        logger.info("Extracted %d characters from %s", len(text), filename)

        # Chunk
        pre_chunks = simple_paragraph_split(text)
        all_chunks = []
        for idx, block in enumerate(pre_chunks):
            if block.strip():
                all_chunks.append({
                    "chunk_id": idx,
                    "content": block.strip(),
                    "text": block.strip(),
                    "start_offset": None,
                    "end_offset": None,
                })
        logger.info("Split into %d chunks", len(all_chunks))

        # Save file + chunks to DB
        file_id = save_files_and_chunks(file_path=file_path, chunks=all_chunks, source=src)
        logger.info("Saved to DB with file_id=%s", file_id)

        # Parse resume with Gemini (inlined — no .pyc cache issue)
        candidate_id = None
        candidate_meta = {}
        parsed = parse_resume_inline(text)

        if parsed:
            try:
                candidate_id = save_candidate(str(file_id), {
                    "name":                   parsed.get("name"),
                    "email":                  parsed.get("email"),
                    "phone":                  parsed.get("phone"),
                    "current_role":           parsed.get("current_role"),
                    "domain":                 parsed.get("domain"),
                    "seniority":              parsed.get("seniority"),
                    "total_experience_years": parsed.get("total_experience_years"),
                    "raw_text":               text,
                })
                skills = [
                    {"name": s.get("name", ""), "category": s.get("category", "technical")}
                    for s in parsed.get("skills", []) if s.get("name")
                ]
                save_skills(candidate_id, skills)
                save_projects(candidate_id, parsed.get("projects", []))
                candidate_meta = {
                    "name":         parsed.get("name"),
                    "domain":       parsed.get("domain"),
                    "seniority":    parsed.get("seniority"),
                    "current_role": parsed.get("current_role"),
                    "candidate_id": candidate_id,
                }
                logger.info("Candidate saved: name=%s id=%s", parsed.get("name"), candidate_id)
            except Exception as e:
                logger.warning("DB save for candidate failed (non-fatal): %s", e)
        else:
            logger.warning("Resume parsing returned None — skipping candidate save.")

        # Index in FAISS
        try:
            full_text = " ".join(c["content"] for c in all_chunks)
            vector = embedder.encode([full_text])[0]
            vector_store.add(vector, meta={
                "file_id":   str(file_id),
                "file_path": file_path,
                "source":    src,
                "filename":  filename,
                **candidate_meta,
            })
            logger.info("Indexed in FAISS. file_id=%s, total=%d", file_id, vector_store.total)
        except Exception as e:
            logger.warning("FAISS indexing failed (non-fatal): %s", e)

        return {
            "status":         "done",
            "file_id":        str(file_id),
            "filename":       filename,
            "chunks_count":   len(all_chunks),
            "candidate_name": candidate_meta.get("name"),
            "skills_count":   len(parsed.get("skills", [])) if parsed else 0,
        }

    except Exception as e:
        logger.exception("Unexpected error in process_file_task: %s", e)
        return {"status": "error", "error": str(e)}
