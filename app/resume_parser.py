"""
Resume Parser — Phase 1, Item 2.

Extracts structured candidate data from raw resume text using pdfplumber
for PDF layout-aware extraction and Gemini for structured field parsing.
"""

import io
import json
import logging
import re

import pdfplumber
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.settings import settings

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel(settings.GEMINI_MODEL)

_SYSTEM_PROMPT = """You are a precise resume parsing engine.

Given the raw resume text below, extract structured data and return ONLY valid
JSON — no markdown fences, no commentary, no preamble, no trailing text.

Return exactly this structure:
{
  "name":                   string or null,
  "email":                  string or null,
  "phone":                  string or null,
  "current_role":           string or null,
  "domain":                 string or null,
  "seniority":              "Junior" | "Mid" | "Mid-Senior" | "Senior" | "Lead" | "Unknown",
  "total_experience_years": number or null,
  "skills": [
    {"name": string, "category": "technical" | "tool" | "language" | "soft"}
  ],
  "projects": [
    {
      "title":        string or null,
      "description":  string or null,
      "technologies": string or null
    }
  ]
}

Rules:
- name: full name from the header/top of the resume. null if not found.
- email: first valid email address found. null if not found.
- phone: first phone number found, keep original format. null if not found.
- current_role: most recent job title. null if not found.
- domain: the primary technical field (e.g. "Machine Learning", "Backend Engineering",
  "Data Analytics", "DevOps", "Full Stack"). null if unclear.
- seniority: infer from years of experience + job titles. Use "Unknown" if unclear.
- total_experience_years: sum of all work experience in years as a decimal
  (e.g. 2 years 6 months = 2.5). null if not determinable.
- skills.name: normalize casing (e.g. "pytorch" → "PyTorch", "aws" → "AWS").
- skills.category:
    technical = programming languages, frameworks, ML libraries
    tool      = platforms and tools (Docker, Git, AWS, Kubernetes)
    language  = spoken/written languages (English, Hindi)
    soft      = soft skills — only include if explicitly stated
- projects: extract up to 5 most significant projects. technologies should be
  a comma-separated string of tools/frameworks used in that project.
- If a section is absent, return [] for skills/projects and null for scalar fields.
- Do NOT invent information not present in the resume text.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pdfplumber.
    Preserves layout better than pypdf — important for detecting
    sections (Education, Experience, Skills) by position.
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    pages.append(text)

        full_text = "\n\n".join(pages).strip()
        if not full_text:
            raise ValueError("No extractable text in PDF (may be scanned/image-only).")
        return full_text

    except Exception as e:
        logger.exception("pdfplumber failed: %s", e)
        raise ValueError(f"Could not read PDF: {e}")


def _strip_fences(raw: str) -> str:
    """Remove markdown fences Gemini sometimes adds despite instructions."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    return cleaned.strip()


def _validate_parsed(data: dict) -> dict:
    """Fill missing keys with safe defaults so pipeline never gets KeyError."""
    return {
        "name":                   data.get("name"),
        "email":                  data.get("email"),
        "phone":                  data.get("phone"),
        "current_role":           data.get("current_role"),
        "domain":                 data.get("domain"),
        "seniority":              data.get("seniority", "Unknown"),
        "total_experience_years": data.get("total_experience_years"),
        "skills": [
            {
                "name":     s.get("name", ""),
                "category": s.get("category", "technical"),
            }
            for s in data.get("skills", [])
            if s.get("name")
        ],
        "projects": [
            {
                "title":        p.get("title"),
                "description":  p.get("description"),
                "technologies": p.get("technologies"),
            }
            for p in data.get("projects", [])
        ],
    }


def parse_resume(resume_text: str) -> dict:
    """
    Parse raw resume text → structured dict using Gemini.

    Args:
        resume_text: plain text extracted from resume.

    Returns:
        Validated dict with name, email, skills, projects, etc.

    Raises:
        ValueError: if text is empty or Gemini fails after retries.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    # Truncate to ~12k chars — resumes are rarely longer
    text_input = resume_text[:12000]
    prompt = _SYSTEM_PROMPT.format(resume_text=text_input)

    last_error = None
    for attempt in range(2):
        try:
            response = _model.generate_content(
                prompt,
                generation_config=GenerationConfig(temperature=0.0),
            )
            raw = response.text
            if not raw or not raw.strip():
                raise ValueError("Empty response from Gemini.")

            cleaned = _strip_fences(raw)
            parsed  = json.loads(cleaned)
            result  = _validate_parsed(parsed)

            logger.info(
                "Parsed resume: name=%s skills=%d projects=%d",
                result.get("name"), len(result["skills"]), len(result["projects"]),
            )
            return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            logger.warning("Resume parse attempt %d failed: %s", attempt + 1, e)
        except Exception as e:
            last_error = e
            logger.exception("Unexpected error during resume parsing: %s", e)
            break

    raise ValueError(f"Failed to parse resume after retries: {last_error}")


def parse_resume_from_pdf(file_bytes: bytes) -> dict:
    """Convenience: PDF bytes → structured dict in one call."""
    text = extract_text_from_pdf(file_bytes)
    return parse_resume(text)