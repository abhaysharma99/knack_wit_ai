from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Base, File, Chunk, Candidate, Skill, Project, Job, Ranking
from app.settings import settings
from app.schemas import JDStructured
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)


# ─────────────────────────────────────────────
# DB INIT
# ─────────────────────────────────────────────

def init_db():
    """Create all tables. Called at startup."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error("Error creating database tables: %s", e)
        raise


# ─────────────────────────────────────────────
# FILE + CHUNKS
# ─────────────────────────────────────────────

def save_files_and_chunks(file_path: str, chunks: list, source: str = "web") -> str:
    """Save a raw file record + its text chunks. Returns file_id."""
    session = Session()
    try:
        file_row = File(path=file_path, source=source)
        session.add(file_row)
        session.flush()

        for idx, c in enumerate(chunks):
            chunk = Chunk(
                file_id=file_row.id,
                chunk_index=c.get("chunk_id", idx),
                content=c["content"],
            )
            session.add(chunk)

        session.commit()
        file_id = file_row.id
        logger.info("Saved file %s with %d chunks", file_path, len(chunks))
        return file_id

    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving file %s: %s", file_path, e)
        raise
    except Exception as e:
        session.rollback()
        logger.error("Unexpected error saving file %s: %s", file_path, e)
        raise
    finally:
        session.close()


def get_chunks_by_file_id(file_id: str) -> list:
    """Fetch all chunks for a file, ordered by chunk_index."""
    session = Session()
    try:
        chunks = (
            session.query(Chunk)
            .filter(Chunk.file_id == file_id)
            .order_by(Chunk.chunk_index)
            .all()
        )
        # Convert to plain dicts so they survive session close
        return [{"content": c.content, "chunk_index": c.chunk_index} for c in chunks]
    except SQLAlchemyError as e:
        logger.error("Error fetching chunks for file_id %s: %s", file_id, e)
        raise
    finally:
        session.close()


# ─────────────────────────────────────────────
# CANDIDATE
# ─────────────────────────────────────────────

def save_candidate(file_id: str, parsed: dict) -> str:
    session = Session()
    try:
        candidate = Candidate(
            file_id                = file_id,
            name                   = parsed.get("name"),
            email                  = parsed.get("email"),
            phone                  = parsed.get("phone"),
            current_role           = parsed.get("current_role"),
            domain                 = parsed.get("domain"),
            seniority              = parsed.get("seniority"),
            total_experience_years = parsed.get("total_experience_years"),
            raw_text               = parsed.get("raw_text"),
        )
        session.add(candidate)
        session.commit()
        logger.info("Saved candidate %s (file_id=%s)", parsed.get("name"), file_id)
        return candidate.id
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving candidate for file_id %s: %s", file_id, e)
        raise
    finally:
        session.close()


def save_skills(candidate_id: str, skills: list[dict]) -> None:
    if not skills:
        return
    session = Session()
    try:
        for s in skills:
            skill = Skill(
                candidate_id=candidate_id,
                name=s.get("name", ""),
                category=s.get("category", "technical"),
            )
            session.add(skill)
        session.commit()
        logger.info("Saved %d skills for candidate_id=%s", len(skills), candidate_id)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving skills for candidate_id %s: %s", candidate_id, e)
        raise
    finally:
        session.close()


def save_projects(candidate_id: str, projects: list[dict]) -> None:
    if not projects:
        return
    session = Session()
    try:
        for p in projects:
            project = Project(
                candidate_id=candidate_id,
                title=p.get("title"),
                description=p.get("description"),
                technologies=p.get("technologies"),
            )
            session.add(project)
        session.commit()
        logger.info("Saved %d projects for candidate_id=%s", len(projects), candidate_id)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving projects for candidate_id %s: %s", candidate_id, e)
        raise
    finally:
        session.close()


def get_candidate_by_id(candidate_id: str) -> dict | None:
    """
    Fetch candidate by candidate_id (primary key of candidates table).
    Used by Phase 3 analysis endpoint.
    """
    session = Session()
    try:
        candidate = (
            session.query(Candidate)
            .options(
                joinedload(Candidate.skills),
                joinedload(Candidate.projects),
            )
            .filter(Candidate.id == candidate_id)
            .first()
        )
        if candidate is None:
            return None
        return {
            "id":                     candidate.id,
            "file_id":                candidate.file_id,
            "name":                   candidate.name,
            "email":                  candidate.email,
            "phone":                  candidate.phone,
            "current_role":           candidate.current_role,
            "domain":                 candidate.domain,
            "seniority":              candidate.seniority,
            "total_experience_years": candidate.total_experience_years,
            "raw_text":               candidate.raw_text,
            "skills":   [{"name": s.name, "category": s.category} for s in candidate.skills],
            "projects": [{"title": p.title, "description": p.description, "technologies": p.technologies} for p in candidate.projects],
        }
    except SQLAlchemyError as e:
        logger.error("Error fetching candidate id=%s: %s", candidate_id, e)
        raise
    finally:
        session.close()


def get_candidate_by_file_id(file_id: str) -> dict | None:
    """
    Fetch candidate with skills eagerly loaded.
    Returns a plain dict so it works after session closes.
    """
    session = Session()
    try:
        candidate = (
            session.query(Candidate)
            .options(
                joinedload(Candidate.skills),
                joinedload(Candidate.projects),
            )
            .filter(Candidate.file_id == file_id)
            .first()
        )
        if candidate is None:
            return None

        # Convert to plain dict while session is still open
        return {
            "id": candidate.id,
            "file_id": candidate.file_id,
            "name": candidate.name,
            "email": candidate.email,
            "domain": candidate.domain,
            "seniority": candidate.seniority,
            "total_experience_years": candidate.total_experience_years,
            "raw_text": candidate.raw_text,
            "skills": [{"name": s.name, "category": s.category} for s in candidate.skills],
            "projects": [{"title": p.title, "technologies": p.technologies} for p in candidate.projects],
        }
    except SQLAlchemyError as e:
        logger.error("Error fetching candidate for file_id %s: %s", file_id, e)
        raise
    finally:
        session.close()


def get_all_candidates() -> list[dict]:
    session = Session()
    try:
        candidates = (
            session.query(Candidate)
            .options(joinedload(Candidate.skills), joinedload(Candidate.projects))
            .all()
        )
        return [
            {
                "id": c.id,
                "file_id": c.file_id,
                "name": c.name,
                "domain": c.domain,
                "seniority": c.seniority,
                "total_experience_years": c.total_experience_years,
                "skills": [{"name": s.name, "category": s.category} for s in c.skills],
            }
            for c in candidates
        ]
    except SQLAlchemyError as e:
        logger.error("Error fetching all candidates: %s", e)
        raise
    finally:
        session.close()


# ─────────────────────────────────────────────
# JOB
# ─────────────────────────────────────────────

def save_job(jd: JDStructured, raw_jd_text: str = None) -> str:
    session = Session()
    try:
        job = Job(
            title=jd.role,
            domain=jd.domain,
            seniority=jd.seniority,
            experience_years=jd.experience_years,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills,
            raw_jd_text=raw_jd_text,
        )
        session.add(job)
        session.commit()
        logger.info("Saved job: %s (id=%s)", jd.role, job.id)
        return job.id
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving job: %s", e)
        raise
    finally:
        session.close()


def get_job_by_id(job_id: str) -> Job | None:
    session = Session()
    try:
        return session.query(Job).filter(Job.id == job_id).first()
    except SQLAlchemyError as e:
        logger.error("Error fetching job %s: %s", job_id, e)
        raise
    finally:
        session.close()


# ─────────────────────────────────────────────
# RANKING
# ─────────────────────────────────────────────

def save_ranking(
    candidate_id: str,
    job_id: str,
    rank: int,
    faiss_score: float,
    rerank_score: float,
    fit_score: float,
    final_score: float,
) -> int:
    session = Session()
    try:
        ranking = Ranking(
            candidate_id=candidate_id,
            job_id=job_id,
            rank=rank,
            faiss_score=faiss_score,
            rerank_score=rerank_score,
            fit_score=fit_score,
            final_score=final_score,
        )
        session.add(ranking)
        session.commit()
        return ranking.id
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("DB error saving ranking: %s", e)
        raise
    finally:
        session.close()


def get_rankings_by_job(job_id: str) -> list[Ranking]:
    session = Session()
    try:
        return (
            session.query(Ranking)
            .filter(Ranking.job_id == job_id)
            .order_by(Ranking.rank)
            .all()
        )
    except SQLAlchemyError as e:
        logger.error("Error fetching rankings for job %s: %s", job_id, e)
        raise
    finally:
        session.close()
