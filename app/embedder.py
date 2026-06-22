"""
Module 2 — Embedding layer.
Turns text into vectors so we can compare JD <-> resume by meaning,
not just keyword overlap.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# Loaded once, reused for every call. Loading takes a few seconds —
# we don't want to repeat that on every request.
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# BGE wants this exact instruction prefix on the QUERY side only.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def embed_query(text: str) -> np.ndarray:
    """Use this for the JOB DESCRIPTION (the thing doing the searching)."""
    vector = model.encode(QUERY_PREFIX + text, normalize_embeddings=True)
    return np.asarray(vector, dtype="float32")


def embed_passage(text: str) -> np.ndarray:
    """Use this for RESUMES (the things being searched over)."""
    vector = model.encode(text, normalize_embeddings=True)
    return np.asarray(vector, dtype="float32")