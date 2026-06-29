# app/api/v1/match.py
from fastapi import APIRouter, HTTPException
from app.schemas import MatchRequest, MatchResponse, MatchResult
from app.matcher import match_candidates
from app.vector_store import vector_store
from app.db.crud import get_all_candidates, get_candidate_by_file_id, get_candidate_by_id


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

@router.get("/candidates")
def list_candidates():
    """List all candidates indexed in DB with their skills."""
    try:
        candidates = get_all_candidates()
        return {
            "total_in_faiss": vector_store.total,
            "total_in_db": len(candidates),
            "candidates": candidates,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    """Get full profile of one candidate by candidate_id."""
    try:
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")
        return candidate
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))