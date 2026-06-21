"""
Module 1 — JD Intelligence Engine

Converts a raw, unstructured job description (PDF or plain text) into a
clean, structured JSON object that the rest of the pipeline can consume.

Pipeline:
    raw text / PDF bytes -> extract_text_from_pdf (if needed)
                          -> parse_jd(text) -> JDStructured
"""

import io
import json
import logging

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from pypdf import PdfReader

from app.schemas import JDStructured
from app.settings import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)


JD_SYSTEM_PROMPT = """You are a precise JSON extraction engine for job descriptions.

Given the raw job description text, extract structured data and return ONLY
valid JSON matching this schema — no markdown fences, no commentary, no preamble:

{schema}

Rules:
- required_skills: only skills explicitly marked as required / must-have.
- preferred_skills: skills marked as nice-to-have / preferred / bonus.
- experience_years: extract the MINIMUM number of years mentioned
  (e.g. "3-5 years" -> 3). Use null if no experience is mentioned.
- seniority: one of "Junior", "Mid", "Mid-Senior", "Senior", "Lead", "Unknown".
  Infer from title/years/responsibilities if not stated explicitly.
- domain: the industry / field this role sits in (e.g. "Machine Learning",
  "Backend Engineering", "Data Analytics"). Use "Unknown" if unclear.
- Do not invent skills that are not present in the text.
- Normalize skill names to common casing (e.g. "pytorch" -> "PyTorch").
"""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts plain text from PDF bytes using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(text_parts).strip()
        if not text:
            raise ValueError("No extractable text found in PDF (it may be scanned/image-only).")
        return text
    except Exception as e:
        logger.exception("Failed to extract text from PDF: %s", e)
        raise ValueError(f"Could not read PDF: {e}")


def _strip_code_fences(raw: str) -> str:
    """Gemini sometimes wraps JSON in ```json ... ``` despite instructions."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return cleaned.strip()


def parse_jd(jd_text: str) -> JDStructured:
    """
    Sends raw JD text to Gemini and returns a validated JDStructured object.
    Raises ValueError if the JD text is empty or the model output can't be
    parsed/validated after one retry.
    """
    if not jd_text or not jd_text.strip():
        raise ValueError("JD text is empty.")

    system_prompt = JD_SYSTEM_PROMPT.format(schema=JDStructured.model_json_schema())

    last_error = None
    for attempt in range(2):  # one retry on parse/validation failure
        try:
            resp = model.generate_content(
                [system_prompt, jd_text],
                generation_config=GenerationConfig(temperature=0.0),
            )

            raw = resp.text
            if not raw or not raw.strip():
                raise ValueError("Empty response from Gemini.")

            cleaned = _strip_code_fences(raw)
            parsed = json.loads(cleaned)
            return JDStructured.model_validate(parsed)

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            logger.warning("JD parse attempt %d failed: %s", attempt + 1, e)
        except Exception as e:
            last_error = e
            logger.exception("Unexpected error during JD parsing: %s", e)
            break

    raise ValueError(f"Failed to parse job description after retries: {last_error}")
