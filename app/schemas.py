from pydantic import BaseModel, Field
from typing import List, Optional

class Chunk(BaseModel):
    text:str
    chunk_id: int
    start_offset: int | None = None
    end_offset: int | None = None
    content: str

class ChunkResponse(BaseModel):
    chunks: List[Chunk]


class JDStructured(BaseModel):
    """Structured output of Module 1 - JD Intelligence Engine."""
    role: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    domain: Optional[str] = None
    seniority: Optional[str] = None


class CandidateStructured(BaseModel):
    """Structured output of Module 2 - Resume parsing (input to embedding)."""
    name: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float] = None
    projects: List[str] = Field(default_factory=list)
    domain: Optional[str] = None
