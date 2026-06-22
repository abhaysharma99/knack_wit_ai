"""
Module 2 — Resume Parsing (feeds Semantic Candidate Matching)

Converts a raw resume (PDF or plain text) into a clean, structured JSON
object (name, skills, experience, projects). Mirrors jd_parser.py.
"""

import json
import logging

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.jd_parser import _strip_code_fences  # reuse the same cleanup helper
from app.schemas import CandidateStructured
from app.settings import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)


RESUME_SYSTEM_PROMPT = """You are a precise JSON extraction engine for resumes.

Given the raw resume text, extract structured data and return ONLY valid
JSON matching this schema — no markdown fences, no commentary, no preamble:

{schema}

Rules:
- skills: flatten all technical skills mentioned anywhere into a single
  deduplicated list.
- experience_years: total years of professional/internship experience.
  Use null if it cannot be determined.
- projects: short titles/descriptions of each project mentioned (max 10).
- domain: the field this person's experience is concentrated in.
  Use null if unclear.
- Do not invent skills or projects that are not present in the text.
- Normalize skill names to common casing (e.g. "pytorch" -> "PyTorch").
"""


def parse_resume(resume_text: str) -> CandidateStructured:
    """
    Sends raw resume text to Gemini and returns a validated
    CandidateStructured object. Raises ValueError if the text is empty or
    the model output can't be parsed/validated after one retry.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    system_prompt = RESUME_SYSTEM_PROMPT.format(
        schema=CandidateStructured.model_json_schema()
    )

    last_error = None
    for attempt in range(2):
        try:
            resp = model.generate_content(
                [system_prompt, resume_text],
                generation_config=GenerationConfig(temperature=0.0),
            )

            raw = resp.text
            if not raw or not raw.strip():
                raise ValueError("Empty response from Gemini.")

            cleaned = _strip_code_fences(raw)
            parsed = json.loads(cleaned)
            return CandidateStructured.model_validate(parsed)

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            logger.warning("Resume parse attempt %d failed: %s", attempt + 1, e)
        except Exception as e:
            last_error = e
            logger.exception("Unexpected error during resume parsing: %s", e)
            break

    raise ValueError(f"Failed to parse resume after retries: {last_error}")