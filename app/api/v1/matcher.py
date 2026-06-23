# app/api/v1/match.py
from fastapi import APIRouter, HTTPException
from app.schemas import MatchRequest, MatchResponse, MatchResult
from app.matcher import match_candidates
from app.vector_store import vector_store

router = APIRouter(prefix="/api/v1/match")

@router.post("/search-candidates", response_model=MatchResponse)
def search_candidates(request: MatchRequest):
    """
    Module 2 — Semantic Candidate Matching.
    Takes a structured JD (output of Module 1) and returns
    semantically ranked candidates from the resume corpus.
    """
    try:
        results = match_candidates(request.jd, top_n=request.top_n)
        return MatchResponse(
            total_indexed=vector_store.total,
            results=[MatchResult(**r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))