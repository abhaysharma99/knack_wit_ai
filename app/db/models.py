from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import uuid

Base = declarative_base()


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


# ─────────────────────────────────────────────
# EXISTING TABLES (unchanged — pipeline still works)
# ─────────────────────────────────────────────

class File(Base):
    """Raw upload record — created when a resume file is received."""
    __tablename__ = "files"

    id          = Column(String, primary_key=True, default=_uuid)
    path        = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=_now)
    source      = Column(String, nullable=True)

    # relationship: one file → one candidate (after parsing)
    candidate   = relationship("Candidate", back_populates="file", uselist=False)


class Chunk(Base):
    """Raw text chunks used by FAISS for embedding search."""
    __tablename__ = "chunks"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    file_id     = Column(String, ForeignKey("files.id"))
    chunk_index = Column(Integer)
    content     = Column(Text, nullable=False)


# ─────────────────────────────────────────────
# NEW TABLES
# ─────────────────────────────────────────────

class Candidate(Base):
    """
    Structured candidate profile — populated by the resume parser (Phase 1 item 2).
    One candidate per uploaded resume file.
    """
    __tablename__ = "candidates"

    id                      = Column(String, primary_key=True, default=_uuid)
    file_id                 = Column(String, ForeignKey("files.id"), unique=True, nullable=False)
    name                    = Column(String, nullable=True)
    email                   = Column(String, nullable=True)
    phone                   = Column(String, nullable=True)
    current_role            = Column(String, nullable=True)   # most recent job title
    domain                  = Column(String, nullable=True)   # e.g. "Machine Learning"
    seniority               = Column(String, nullable=True)   # Junior / Mid / Senior / Lead
    total_experience_years  = Column(Float,  nullable=True)
    raw_text                = Column(Text,   nullable=True)   # full resume text (for re-parsing)
    parsed_at               = Column(DateTime, default=_now)

    # relationships
    file     = relationship("File",     back_populates="candidate")
    skills   = relationship("Skill",    back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("Project",  back_populates="candidate", cascade="all, delete-orphan")
    rankings = relationship("Ranking",  back_populates="candidate", cascade="all, delete-orphan")


class Skill(Base):
    """
    Individual skill extracted from a resume.
    Stored as separate rows so we can query "all candidates with PyTorch"
    without scanning JSON columns.
    """
    __tablename__ = "skills"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    name         = Column(String, nullable=False)       # e.g. "PyTorch"
    category     = Column(String, nullable=True)        # "technical" / "soft" / "tool" / "language"

    candidate = relationship("Candidate", back_populates="skills")


class Project(Base):
    """
    Project extracted from a resume — title, description, technologies used.
    """
    __tablename__ = "projects"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    title        = Column(String, nullable=True)
    description  = Column(Text,   nullable=True)
    technologies = Column(String, nullable=True)   # comma-separated: "PyTorch, FastAPI, Docker"

    candidate = relationship("Candidate", back_populates="projects")


class Job(Base):
    """
    Parsed job description — stored so we can re-run matching later
    without re-parsing the same JD through Gemini again.
    """
    __tablename__ = "jobs"

    id                = Column(String,  primary_key=True, default=_uuid)
    title             = Column(String,  nullable=False)          # role name
    domain            = Column(String,  nullable=True)
    seniority         = Column(String,  nullable=True)
    experience_years  = Column(Float,   nullable=True)
    required_skills   = Column(JSON,    nullable=True)           # ["PyTorch", "LLMs"]
    preferred_skills  = Column(JSON,    nullable=True)           # ["AWS", "Docker"]
    raw_jd_text       = Column(Text,    nullable=True)           # original JD text
    created_at        = Column(DateTime, default=_now)

    rankings = relationship("Ranking", back_populates="job", cascade="all, delete-orphan")


class Ranking(Base):
    """
    Match result linking a Candidate to a Job with all three scores.
    Created each time /match/search-candidates is called.
    Lets you retrieve past match results without re-running the pipeline.
    """
    __tablename__ = "rankings"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    job_id       = Column(String, ForeignKey("jobs.id"),       nullable=False)
    faiss_score  = Column(Float, nullable=True)    # cosine similarity from FAISS
    rerank_score = Column(Float, nullable=True)    # cross-encoder score
    fit_score    = Column(Float, nullable=True)    # skill overlap + experience + domain
    final_score  = Column(Float, nullable=True)    # weighted combination of all three
    rank         = Column(Integer, nullable=True)  # 1 = best match
    created_at   = Column(DateTime, default=_now)

    candidate = relationship("Candidate", back_populates="rankings")
    job       = relationship("Job",       back_populates="rankings")
