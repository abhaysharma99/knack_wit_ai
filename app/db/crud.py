from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Base, File, Chunk, Candidate
from app.settings import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def save_files_and_chunks(file_path, chunks, source="web"):
    session = Session()
    try:
        # Create file record
        file_row = File(path=file_path, source=source)
        session.add(file_row)
        session.flush()
        
        # Create chunk records
        for idx, c in enumerate(chunks):
            chunk = Chunk(
                file_id=file_row.id, 
                chunk_index=c.get("chunk_id", idx), 
                content=c["content"]
            )
            session.add(chunk)
        
        # Commit all changes
        session.commit()
        file_id = file_row.id
        logger.info(f"Successfully saved file {file_path} with {len(chunks)} chunks")
        return file_id
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error saving file {file_path}: {str(e)}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error saving file {file_path}: {str(e)}")
        raise
    finally:
        session.close()
        
# =====================================================
# Module 2 - Candidate CRUD
# =====================================================

def save_candidate(
    raw_text,
    name=None,
    skills=None,
    experience_years=None,
    faiss_index=None,
    file_id=None
):
    session = Session()

    try:
        candidate = Candidate(
            file_id=file_id,
            name=name,
            raw_text=raw_text,
            skills=skills,
            experience_years=experience_years,
            faiss_index=faiss_index
        )

        session.add(candidate)
        session.commit()
        session.refresh(candidate)

        logger.info(f"Candidate saved: {candidate.id}")

        return candidate

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error saving candidate: {str(e)}")
        raise

    finally:
        session.close()


def get_candidate(candidate_id):
    session = Session()

    try:
        return (
            session.query(Candidate)
            .filter(Candidate.id == candidate_id)
            .first()
        )

    finally:
        session.close()


def get_candidates_by_ids(candidate_ids):
    session = Session()

    try:
        return (
            session.query(Candidate)
            .filter(Candidate.id.in_(candidate_ids))
            .all()
        )

    finally:
        session.close()
