from fastapi import APIRouter, HTTPException

from app.genius_detector import GeniusDetector
from app.future_potential import FuturePotentialScorer
from app.classifier import HiddenGeniusClassifier
from app.fusion_engine import FusionEngine
from app.explainer import TalentExplainer

from app.db.crud import get_candidate_by_id

router = APIRouter(prefix="/api/v1/analysis")


@router.get("/candidate/{candidate_id}")
def analyze_candidate(candidate_id: str):

    candidate = get_candidate_by_id(candidate_id)

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    detector = GeniusDetector()
    signals = detector.generate_growth_signals(candidate)

    scorer = FuturePotentialScorer()
    future_score = scorer.calculate_score(signals)

    classifier = HiddenGeniusClassifier()
    potential_level = classifier.classify(future_score)

    # Temporary value
    # Later we will fetch actual fit score from Ranking table
    current_fit_score = 75

    fusion_engine = FusionEngine()

    true_talent_score = fusion_engine.calculate_true_talent_score(
        current_fit_score,
        future_score
    )

    explainer = TalentExplainer()

    analysis = explainer.generate_reasons(
        signals,
        future_score,
        potential_level
    )

    return {
        "candidate_id": candidate["id"],
        "candidate_name": candidate["name"],

        "growth_signals": signals,

        "future_score": future_score,

        "potential_level": potential_level,

        "current_fit_score": current_fit_score,

        "true_talent_score": true_talent_score,

        "analysis": analysis
    }