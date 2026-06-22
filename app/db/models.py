from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
import datetime
import uuid

Base = declarative_base()


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    source = Column(String, nullable=True)


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String, ForeignKey("files.id"))
    chunk_index = Column(Integer)
    content = Column(Text, nullable=False)


class Candidate(Base):
    """
    Module 2 — Semantic Candidate Matching.

    One row per parsed resume. faiss_index stores the integer position of
    this candidate's embedding inside the FAISS index, so a FAISS search
    hit can be mapped back to this row.
    """
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.id"), nullable=True)

    name = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    skills = Column(Text, nullable=True)
    experience_years = Column(Float, nullable=True)

    faiss_index = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
