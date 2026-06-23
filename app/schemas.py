from pydantic import BaseModel, Field
from typing import List, Optional
import datetime


# ─────────────────────────────────────────────
# EXISTING (unchanged — pipeline still works)
# ─────────────────────────────────────────────

class Chunk(BaseModel):
    text: str
    chunk_id: int
    start_offset: int | None = None
    end_offset: int | None = None
    content: str


class ChunkResponse(BaseModel):
    chunks: List[Chunk]


# ─────────────────────────────────────────────
# MODULE 1 — JD Intelligence Engine
# ─────────────────────────────────────────────

class JDStructured(BaseModel):
    """Structured output of Module 1 - JD Intelligence Engine."""
    role:             str
    required_skills:  List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    domain:           Optional[str]   = None
    seniority:        Optional[str]   = None


# ─────────────────────────────────────────────
# MODULE 2 — Semantic Matching
# ─────────────────────────────────────────────

class MatchRequest(BaseModel):
    """Input to /match/search-candidates."""
    jd:    JDStructured
    top_n: int = Field(default=10, ge=1, le=50)


class MatchResult(BaseModel):
    rank:           int
    file_id:        str
    faiss_score:    float
    rerank_score:   float
    fit_score:      Optional[float] = None
    final_score:    Optional[float] = None
    candidate_name: Optional[str]   = None
    file_path:      Optional[str]   = None


class MatchResponse(BaseModel):
    total_indexed: int
    results:       List[MatchResult]


# ─────────────────────────────────────────────
# CANDIDATE — API response models
# ─────────────────────────────────────────────

class SkillOut(BaseModel):
    name:     str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    title:        Optional[str] = None
    description:  Optional[str] = None
    technologies: Optional[str] = None     # comma-separated string

    class Config:
        from_attributes = True


class CandidateOut(BaseModel):
    """Returned by GET /candidates and GET /candidates/{id}."""
    id:                     str
    file_id:                str
    name:                   Optional[str]   = None
    email:                  Optional[str]   = None
    phone:                  Optional[str]   = None
    current_role:           Optional[str]   = None
    domain:                 Optional[str]   = None
    seniority:              Optional[str]   = None
    total_experience_years: Optional[float] = None
    parsed_at:              Optional[datetime.datetime] = None
    skills:                 List[SkillOut]   = []
    projects:               List[ProjectOut] = []

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# JOB — API response models
# ─────────────────────────────────────────────

class JobOut(BaseModel):
    """Returned when a JD is saved to the DB."""
    id:               str
    title:            str
    domain:           Optional[str]        = None
    seniority:        Optional[str]        = None
    experience_years: Optional[float]      = None
    required_skills:  List[str]            = []
    preferred_skills: List[str]            = []
    created_at:       Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# RANKING — API response models
# ─────────────────────────────────────────────

class RankingOut(BaseModel):
    """One row in a ranked results list — candidate info + all scores."""
    rank:           int
    candidate_id:   str
    candidate_name: Optional[str]   = None
    current_role:   Optional[str]   = None
    faiss_score:    Optional[float] = None
    rerank_score:   Optional[float] = None
    fit_score:      Optional[float] = None
    final_score:    Optional[float] = None

    class Config:
        from_attributes = True


class RankingResponse(BaseModel):
    """Returned by POST /rank-candidates."""
    job_id:        str
    total_indexed: int
    results:       List[RankingOut]
