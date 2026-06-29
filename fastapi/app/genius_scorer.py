# app/genius_scorer.py
"""
Genius Scorer — Phase 3, Items 3-5.

Loads the pre-trained XGBoost classifier once at startup and exposes
two public functions:

    compute_future_potential(growth_features) → float (0.0–1.0)
    compute_true_talent(current_fit, future_potential) → float (0.0–1.0)

The Fusion Engine (item 5) lives here:
    True Talent Score = 0.6 × CurrentFit + 0.4 × FuturePotential
"""

import os
import logging
import numpy as np
import joblib

logger = logging.getLogger(__name__)

# ── Model path ────────────────────────────────────────────────────────────────
_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "genius_classifier.pkl",
)

# ── Thresholds ────────────────────────────────────────────────────────────────
GENIUS_THRESHOLD = 0.65   # future_potential above this → hidden_genius_flag = True

# ── Fusion weights (spec: 0.6 / 0.4) ─────────────────────────────────────────
W_CURRENT_FIT      = 0.6
W_FUTURE_POTENTIAL = 0.4


# ── Singleton loader ──────────────────────────────────────────────────────────

class _GeniusScorer:
    def __init__(self):
        if not os.path.exists(_MODEL_PATH):
            raise FileNotFoundError(
                f"genius_classifier.pkl not found at {_MODEL_PATH}. "
                "Run: python scripts/train_genius_classifier.py"
            )
        logger.info("Loading Hidden Genius classifier from %s", _MODEL_PATH)
        self._model = joblib.load(_MODEL_PATH)
        logger.info("Hidden Genius classifier loaded.")

    def predict_proba(self, features: dict) -> float:
        """
        Run XGBoost on the 4 growth features.
        Returns probability of being a hidden genius (0.0–1.0).
        """
        X = np.array([[
            features["growth_velocity"],
            features["consistency"],
            features["expansion_rate"],
            features["complexity_growth"],
        ]], dtype=np.float32)

        # predict_proba returns [[prob_class_0, prob_class_1]]
        proba = self._model.predict_proba(X)[0][1]
        return round(float(proba), 4)


# Load once at import time — same singleton pattern as embedder.py
try:
    _scorer = _GeniusScorer()
except FileNotFoundError as e:
    # Fail loudly at startup so the developer knows immediately
    logger.error(str(e))
    _scorer = None


# ── Public API ────────────────────────────────────────────────────────────────

def compute_future_potential(growth_features: dict) -> float:
    """
    Compute Future Potential Score from the 4 growth signals.

    Args:
        growth_features: dict with keys:
            growth_velocity, consistency, expansion_rate, complexity_growth
            (output of growth_features.compute_growth_features())

    Returns:
        float 0.0–1.0 — probability of being a hidden genius
    """
    if _scorer is None:
        raise RuntimeError(
            "Hidden Genius classifier not loaded. "
            "Run: python scripts/train_genius_classifier.py"
        )
    return _scorer.predict_proba(growth_features)


def compute_true_talent(current_fit: float, future_potential: float) -> float:
    """
    Fusion Engine — Phase 3, Item 5.

    True Talent Score = 0.6 × CurrentFit + 0.4 × FuturePotential

    Args:
        current_fit:       final_score from matcher.py (0.0–1.0)
        future_potential:  output of compute_future_potential() (0.0–1.0)

    Returns:
        float 0.0–1.0 — the unified talent score
    """
    score = W_CURRENT_FIT * current_fit + W_FUTURE_POTENTIAL * future_potential
    return round(score, 4)


def is_hidden_genius(future_potential: float) -> bool:
    """
    Returns True if future_potential exceeds the genius threshold (0.65).
    Used to set the hidden_genius_flag in AnalysisResult.
    """
    return future_potential >= GENIUS_THRESHOLD