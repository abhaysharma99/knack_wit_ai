from celery import Celery
from celery.signals import worker_ready
import logging
import pypdf
import io

from app.settings import settings

from app.db.crud import (
    save_files_and_chunks,
    save_candidate,
    save_skills,
    save_projects,
    init_db
)

from app.resume_parser import parse_resume

from app.utils import simple_paragraph_split
from app.embedder import embedder
from app.vector_store import vector_store

celery_app = Celery(
    "ingest_worker",
    broker_url=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    """Create DB tables when Celery worker starts."""
    logger.info("Worker ready — initializing database tables...")
    init_db()


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from PDF or TXT file bytes."""
    if filename.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
    else:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1")


@celery_app.task
def process_file_task(
    file_bytes_hex: str,
    file_path: str,
    src: str = "resume",
    filename: str = "resume.txt",
):
    try:

        file_bytes = bytes.fromhex(file_bytes_hex)

        logger.info(
            "Received file: %s, size: %d bytes",
            filename,
            len(file_bytes)
        )

        # Extract text
        text = extract_text(file_bytes, filename)

        if not text.strip():
            return {
                "status": "error",
                "error": "Could not extract text from file"
            }

        logger.info(
            "Extracted %d characters from %s",
            len(text),
            filename
        )

        # Chunking
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

        logger.info(
            "Split into %d chunks",
            len(all_chunks)
        )

        # Save file + chunks
        file_id = save_files_and_chunks(
            file_path=file_path,
            chunks=all_chunks,
            source=src
        )

        logger.info(
            "Saved to DB with file_id=%s",
            file_id
        )

        # ----------------------------------
        # Resume Parsing → Candidate Tables
        # ----------------------------------

        candidate_id = None

        try:

            parsed_candidate = parse_resume(text)

            parsed_candidate["raw_text"] = text

            candidate_id = save_candidate(
                file_id,
                parsed_candidate
            )

            save_skills(
                candidate_id,
                parsed_candidate.get("skills", [])
            )

            save_projects(
                candidate_id,
                parsed_candidate.get("projects", [])
            )

            logger.info(
                "Saved candidate profile. candidate_id=%s",
                candidate_id
            )

        except Exception as e:

            logger.warning(
                "Candidate parsing failed (non-fatal): %s",
                e
            )

        # ----------------------------------
        # FAISS Indexing
        # ----------------------------------

        try:

            full_text = " ".join(
                c["content"]
                for c in all_chunks
            )

            vector = embedder.encode([full_text])[0]

            vector_store.add(
                vector,
                meta={
                    "file_id": str(file_id),
                    "candidate_id": str(candidate_id) if candidate_id else None,
                    "file_path": file_path,
                    "source": src,
                    "filename": filename,
                }
            )

            logger.info(
                "Indexed in FAISS. file_id=%s, total=%d",
                file_id,
                vector_store.total
            )

        except Exception as e:

            logger.warning(
                "FAISS indexing failed (non-fatal): %s",
                e
            )

        return {
            "status": "done",
            "file_id": str(file_id),
            "candidate_id": str(candidate_id) if candidate_id else None,
            "filename": filename,
            "chunks_count": len(all_chunks),
        }

    except Exception as e:

        logger.exception(
            "Unexpected error in process_file_task: %s",
            e
        )

        return {
            "status": "error",
            "error": str(e)
        }