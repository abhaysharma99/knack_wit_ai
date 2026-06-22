import faiss
import numpy as np

DIMENSION = 384

index = faiss.IndexFlatIP(DIMENSION)

candidate_ids = []


def add_candidate(candidate_id: str, vector: np.ndarray):
    index.add(vector.reshape(1, -1))
    candidate_ids.append(candidate_id)


def search(vector: np.ndarray, k: int = 10):
    scores, ids = index.search(
        vector.reshape(1, -1),
        k
    )

    results = []

    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue

        results.append(
            {
                "candidate_id": candidate_ids[idx],
                "score": float(score)
            }
        )

    return results