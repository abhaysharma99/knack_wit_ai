# app/reranker.py
"""
Re-ranker — cross-encoder for precise relevance scoring.

Cross-encoders read both texts *together* (unlike bi-encoders which
encode them independently). Much slower, much more accurate.
We only run this on the top-100 from FAISS, never the full corpus.
"""
import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class Reranker:
    def __init__(self):
        logger.info("Loading cross-encoder: %s", MODEL_NAME)
        self._model = CrossEncoder(MODEL_NAME)
        logger.info("Cross-encoder loaded.")

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        text_key: str = "resume_text",
        top_n: int = 10,
    ) -> list[dict]:
        """
        Score each candidate against the query, sort descending, return top_n.

        candidates: list of dicts, each must have text_key and metadata fields.
        Returns same dicts with an added "rerank_score" field.
        """
        if not candidates:
            return []

        pairs = [[query, c[text_key]] for c in candidates]
        scores = self._model.predict(pairs)   # returns numpy array of floats

        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_n]


# Singleton
reranker = Reranker()