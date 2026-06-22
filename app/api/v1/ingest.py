from app.embedder import embed_passage, embed_query
from app.vector_store import add_candidate, search
from app.db.crud import save_candidate, get_candidates_by_ids
from uuid import uuid4

from fastapi import APIRouter, UploadFile, HTTPException, Form
from typing import Optional
import asyncio
import os
from pathlib import Path
from app.celery_worker import process_file_task
from app.jd_parser import parse_jd, extract_text_from_pdf
router = APIRouter(prefix="/api/v1/ingest")

# Simulated in-memory task store (async-safe)
tasks = {}
task_lock = asyncio.Lock()


@router.post("/process-file")
async def process_file(file: UploadFile, param1 : str , param2 : int , src: str="web"):
    try:
        file_content = await file.read()
        file_id = str(uuid4())
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("/data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Use absolute path to match celery container expectations
        file_path = uploads_dir / f"{file_id}_{file.filename}"
        
        # Write file with error handling
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Start celery task
        task = process_file_task.delay(file_content.decode("utf-8"), param1, param2, str(file_path), src)
        
        return {"file_id": file_id, "task_id": task.id, "status": "submitted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/parse-jd")
async def parse_jd_endpoint(
    file: Optional[UploadFile] = None,
    text: Optional[str] = Form(default=None),
):
    """
    Module 1 — JD Intelligence Engine.

    Accepts EITHER a PDF upload (`file`) OR raw text (`text` form field)
    and returns a structured JSON representation of the job description.
    """
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a PDF file or raw JD text.")

    try:
        if file:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are supported for upload.")
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
        
@router.post("/add-candidate")
async def add_candidate_endpoint(
    text: str = Form(...)
):
    try:
        candidate_id = str(uuid4())

        vector = embed_passage(text)

        add_candidate(candidate_id, vector)

        save_candidate(
            raw_text=text
        )

        return {
            "candidate_id": candidate_id,
            "status": "indexed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/match-candidates")
async def match_candidates(
    jd_text: str = Form(...),
    k: int = Form(10)
):
    try:
        jd_vector = embed_query(jd_text)

        results = search(jd_vector, k)

        return {
            "matches": results,
            "total": len(results)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )





@router.get("/{task_id}")
async def get_task_status(task_id: str):
    async with task_lock:
        task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    async with task_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        del tasks[task_id]
    return {"status": "deleted", "task_id": task_id}
