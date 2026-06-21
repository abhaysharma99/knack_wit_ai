import json
import logging
import time
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core.exceptions import ResourceExhausted
from app.schemas import ChunkResponse
from app.settings import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

# Rate limiting for free tier (2 requests per minute)
_last_request_time = 0
_request_count = 0
_request_window_start = time.time()

def _rate_limited_generate_content(prompt, generation_config):
    """Rate-limited wrapper for Gemini API calls"""
    global _last_request_time, _request_count, _request_window_start
    
    current_time = time.time()
    
    # Reset counter every minute
    if current_time - _request_window_start >= 60:
        _request_count = 0
        _request_window_start = current_time
    
    # Check if we've exceeded the rate limit
    if _request_count >= 2:
        wait_time = 60 - (current_time - _request_window_start)
        if wait_time > 0:
            logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            _request_count = 0
            _request_window_start = time.time()
    
    # Ensure minimum 30 seconds between requests for free tier
    time_since_last = current_time - _last_request_time
    if time_since_last < 30:
        wait_time = 30 - time_since_last
        logger.info(f"Waiting {wait_time:.1f} seconds between requests...")
        time.sleep(wait_time)
    
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        _request_count += 1
        _last_request_time = time.time()
        return response
    except ResourceExhausted as e:
        logger.warning(f"API quota exceeded: {e}")
        # Wait for the suggested retry delay
        if "retry_delay" in str(e):
            retry_seconds = 60  # Default to 60 seconds
            logger.info(f"Waiting {retry_seconds} seconds before retry...")
            time.sleep(retry_seconds)
            _request_count = 0
            _request_window_start = time.time()
        raise

def agentic_chunk_document(text_block: str) -> list[dict]:
    """
    Sends `text_block` to Gemini, asks it to chunk into coherent segments,
    and validates against ChunkResponse schema.
    """
    system_prompt = (
        "You are a document chunking agent. "
        "Given a text passage, return JSON conforming to this schema:\n"
        f"{ChunkResponse.model_json_schema()}\n"
        "Each chunk must be semantic, end at sentence boundary, "
        "and be at most 300 characters roughly."
    )

    try:
        resp = _rate_limited_generate_content(
            [system_prompt, text_block],
            GenerationConfig(temperature=0.0)
        )

        arguments_json = resp.text  # Gemini gives plain text
        
        # Check if response is empty or None
        if not arguments_json or not arguments_json.strip():
            logger.warning("Empty response from Gemini API, using fallback")
            return fallback_naive_chunks(text_block)
        
        # Log the raw response for debugging
        logger.debug(f"Raw Gemini response: {arguments_json[:200]}...")
        
        parsed = json.loads(arguments_json)
        validated = ChunkResponse.model_validate(parsed)

        return [c.model_dump() for c in validated.chunks]

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed. Raw response: {resp.text if 'resp' in locals() else 'No response'}")
        logger.exception("JSON decode error: %s", e)
        return fallback_naive_chunks(text_block)
    except Exception as e:
        logger.exception("Failed to parse/validate chunker output: %s", e)
        return fallback_naive_chunks(text_block)

def fallback_naive_chunks(text_block: str, max_len: int = 500) -> list[dict]:
    """
    Fallback: split text by sentences every ~max_len chars.
    """
    chunks = []
    current = ""
    chunk_id = 0
    start_offset = 0
    
    for sentence in text_block.split(". "):
        if len(current) + len(sentence) < max_len:
            current += sentence + ". "
        else:
            if current.strip():
                chunk_text = current.strip()
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "start_offset": start_offset,
                    "end_offset": start_offset + len(chunk_text),
                    "content": chunk_text
                })
                chunk_id += 1
                start_offset += len(chunk_text)
            current = sentence + ". "
    
    if current.strip():
        chunk_text = current.strip()
        chunks.append({
            "text": chunk_text,
            "chunk_id": chunk_id,
            "start_offset": start_offset,
            "end_offset": start_offset + len(chunk_text),
            "content": chunk_text
        })
    
    return chunks
