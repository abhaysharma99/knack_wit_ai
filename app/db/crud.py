from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Base, File, Chunk
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
