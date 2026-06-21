
from celery import Celery
import logging
import os
from app.settings import settings
from app.chunker import agentic_chunk_document
from app.db.crud import save_files_and_chunks
from app.utils import simple_paragraph_split
celery_app = Celery(
    "ingest_worker",
    broker_url=settings.celery_broker_url,   # or use env var
    backend=settings.celery_result_backend
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# celery_app.conf.task_routes = {
#     "app.tasks.chunker.chunk_file": {"queue": "chunking"},
# }
@celery_app.task
def process_file_task(file_content: str, param1: str, param2: int, file_path: str, src: str):
    try:
        logger.info("received file with size: %d bytes", len(file_content))
        logger.info("Parameters: param1:%s, param2:%s", param1, param2)
        logger.info("file snippet :%s", file_content[:100])
        
        # Check if file exists before trying to read it
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
        
        # Read file with error handling
        try:
            with open(file_path, "r", encoding="utf8") as f:
                text = f.read()
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}
        
        # Process chunks
        try:
            pre_chunks = simple_paragraph_split(text)
            all_chunks = []
            for block in pre_chunks:
                chunks = agentic_chunk_document(block)
                all_chunks.extend(chunks)
        except Exception as e:
            error_msg = f"Error processing chunks: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        # Save to database with error handling
        try:
            file_id = save_files_and_chunks(file_path=file_path, chunks=all_chunks, source=src)
        except Exception as e:
            error_msg = f"Error saving to database: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

        return {
            "status": "done", 
            "chars": len(file_content), 
            "param1": param1, 
            "param2": param2, 
            "file_id": file_id, 
            "chunks_count": len(all_chunks)
        }
    
    except Exception as e:
        error_msg = f"Unexpected error in process_file_task: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}

