from fastapi import APIRouter, UploadFile, HTTPException, Form, File
from typing import Optional, List
import os
from pathlib import Path
from uuid import uuid4
from app.celery_worker import process_file_task, celery_app
from app.jd_parser import parse_jd, extract_text_from_pdf
from celery.result import AsyncResult

router = APIRouter(prefix="/api/v1/ingest")


# ─────────────────────────────────────────────
# Single resume upload
# ─────────────────────────────────────────────

@router.post("/process-file")
async def process_file(
    file: UploadFile,
    src: str = "resume",
):
    """Upload a single resume (PDF or TXT) and index it into FAISS."""
    try:
        file_bytes = await file.read()
        file_id = str(uuid4())

        uploads_dir = Path("/data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_path = uploads_dir / f"{file_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        task = process_file_task.delay(
            file_bytes.hex(),
            str(file_path),
            src,
            file.filename or "resume.txt",
        )

        return {
            "file_id": file_id,
            "task_id": task.id,
            "filename": file.filename,
            "status": "submitted",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


# ─────────────────────────────────────────────
# Bulk resume upload — up to 50 resumes at once
# ─────────────────────────────────────────────

@router.post("/process-files")
async def process_files(
    files: List[UploadFile] = File(...),
    src: str = "resume",
):
    """
    Upload multiple resumes at once (PDF or TXT).
    Each file is queued as a separate Celery task.
    Returns a list of task IDs — poll GET /{task_id} for each.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per upload.")

    uploads_dir = Path("/data/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)

    submitted = []
    failed = []

    for file in files:
        try:
            file_bytes = await file.read()
            file_id = str(uuid4())

            file_path = uploads_dir / f"{file_id}_{file.filename}"
            with open(file_path, "wb") as f:
                f.write(file_bytes)

            task = process_file_task.delay(
                file_bytes.hex(),
                str(file_path),
                src,
                file.filename or "resume.txt",
            )

            submitted.append({
                "file_id": file_id,
                "task_id": task.id,
                "filename": file.filename,
                "status": "submitted",
            })

        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e),
            })

    return {
        "total_submitted": len(submitted),
        "total_failed": len(failed),
        "submitted": submitted,
        "failed": failed,
    }


# ─────────────────────────────────────────────
# Bulk status check — check all tasks at once
# ─────────────────────────────────────────────

@router.post("/tasks-status")
async def bulk_task_status(task_ids: List[str]):
    """
    Check status of multiple tasks at once.
    Pass a list of task_ids returned from /process-files.
    """
    results = []
    for task_id in task_ids:
        result = AsyncResult(task_id, app=celery_app)
        entry = {"task_id": task_id, "status": result.status}
        if result.status == "SUCCESS":
            entry["result"] = result.result
        elif result.status == "FAILURE":
            entry["error"] = str(result.result)
        results.append(entry)

    total = len(results)
    done = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = sum(1 for r in results if r["status"] == "FAILURE")
    pending = total - done - failed

    return {
        "total": total,
        "done": done,
        "failed": failed,
        "pending": pending,
        "tasks": results,
    }


# ─────────────────────────────────────────────
# Module 1 — JD Parser
# ─────────────────────────────────────────────

@router.post("/parse-jd")
async def parse_jd_endpoint(
    file: Optional[UploadFile] = None,
    text: Optional[str] = Form(default=None),
):
    """
    Module 1 — JD Intelligence Engine.
    Accepts EITHER a PDF upload OR raw text and returns structured JD JSON.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a PDF file or raw JD text.")

    try:
        if file:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are supported.")
            file_bytes = await file.read()
            jd_text = extract_text_from_pdf(file_bytes)
        else:
            jd_text = text

        structured = parse_jd(jd_text)
        return structured.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")


from pydantic import BaseModel as _BaseModel

class JDTextRequest(_BaseModel):
    text: str

@router.post("/parse-jd-text")
async def parse_jd_text_endpoint(body: JDTextRequest):
    """
    Module 1 — JD Intelligence Engine (JSON body).
    Paste raw JD text — easiest way to test from Swagger.
    """
    if not body.text or not body.text.strip():
        raise HTTPException(status_code=400, detail="JD text cannot be empty.")
    try:
        structured = parse_jd(body.text)
        return structured.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing job description: {str(e)}")


# ─────────────────────────────────────────────
# Task status endpoints
# ─────────────────────────────────────────────

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Check a single Celery task status."""
    result = AsyncResult(task_id, app=celery_app)
    response = {"task_id": task_id, "status": result.status}
    if result.status == "SUCCESS":
        response["result"] = result.result
    elif result.status == "FAILURE":
        response["error"] = str(result.result)
    return response


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    result.forget()
    return {"status": "deleted", "task_id": task_id}
