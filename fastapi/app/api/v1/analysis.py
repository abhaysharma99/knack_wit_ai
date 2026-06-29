"""
GET /candidate/{candidate_id}/analysis

Returns a full breakdown of a candidate:
    - Growth features (4 signals)
    - Future Potential Score (XGBoost)
    - True Talent Score (fusion engine)
    - Hidden Genius flag
    - Explainability (reasons, strengths, gaps)
"""

import logging
from fastapi import APIRouter, HTTPException, Query

from app.db.crud          import get_candidate_by_id
from app.growth_features  import compute_growth_features
from app.genius_scorer    import compute_future_potential, compute_true_talent, is_hidden_genius
from app.explainer        import explain
from app.schemas          import AnalysisResult, GrowthFeatures

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/candidate")


@router.get("/{candidate_id}/analysis", response_model=AnalysisResult)
def get_candidate_analysis(
    candidate_id: str,
    current_fit: float = Query(
        default=0.5,
        ge=0.0,
        le=1.0,
        description=(
            "Current fit score from /match/search-candidates. "
            "Pass the final_score of this candidate from that response. "
            "Defaults to 0.5 (neutral) if not provided."
        ),
    ),
):
    """
    Phase 3 — Hidden Genius Detection.

    Full candidate analysis combining:
    - Phase 2: current_fit (skill match + semantic similarity)
    - Phase 3: future_potential (growth velocity, consistency,
               expansion rate, complexity growth)
    - Fusion:  true_talent = 0.6 × current_fit + 0.4 × future_potential

    Usage:
        # After running /match/search-candidates, take the final_score
        # of a candidate and pass it here for an accurate true_talent_score.

        GET /api/v1/candidate/{candidate_id}/analysis?current_fit=0.82
    """

    # ── Step 1: fetch candidate ───────────────────────────────────────────
    try:
        candidate = get_candidate_by_id(candidate_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate {candidate_id} not found. "
                   "Make sure the resume was uploaded and parsed successfully.",
        )

    # ── Step 2: compute growth features ──────────────────────────────────
    try:
        growth_dict = compute_growth_features(candidate)
    except Exception as e:
        logger.exception("Growth feature computation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Growth feature error: {e}")

    # ── Step 3: compute future potential (XGBoost) ────────────────────────
    try:
        future_potential = compute_future_potential(growth_dict)
    except RuntimeError as e:
        # .pkl file missing — clear message to developer
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Future potential computation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Scorer error: {e}")

    # ── Step 4: fusion engine ─────────────────────────────────────────────
    true_talent   = compute_true_talent(current_fit, future_potential)
    genius_flag   = is_hidden_genius(future_potential)

    # ── Step 5: explainability ────────────────────────────────────────────
    try:
        explanation = explain(candidate, growth_dict)
    except Exception as e:
        logger.exception("Explainer failed: %s", e)
        explanation = {"reasons": [], "strengths": [], "gaps": []}

    # ── Step 6: build response ────────────────────────────────────────────
    logger.info(
        "Analysis complete — candidate=%s future_potential=%.3f "
        "true_talent=%.3f hidden_genius=%s",
        candidate.get("name"), future_potential, true_talent, genius_flag,
    )

    return AnalysisResult(
        candidate_id       = candidate_id,
        candidate_name     = candidate.get("name"),
        domain             = candidate.get("domain"),
        seniority          = candidate.get("seniority"),
        current_fit_score  = current_fit,
        growth_features    = GrowthFeatures(**growth_dict),
        future_potential   = future_potential,
        true_talent_score  = true_talent,
        hidden_genius_flag = genius_flag,
        reasons            = explanation["reasons"],
        strengths          = explanation["strengths"],
        gaps               = explanation["gaps"],
    )