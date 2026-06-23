"""
Vector Store — FAISS index over resume embeddings.

IndexFlatIP = exact inner product search (= cosine similarity on
L2-normalised vectors). No approximation, perfect recall. Fine for
up to ~100k resumes; swap to IndexHNSWFlat if you need millions.

Persistence: index + metadata saved to data/faiss/ on every write
so it survives container restarts.
"""
import os
import json
import logging
import numpy as np
import faiss 

logger = logging.getLogger(__name__)

INDEX_DIR = "data/faiss"
INDEX_PATH = os.path.join(INDEX_DIR, "resume.index")
METADATA_PATH = os.path.join(INDEX_DIR, "metadata.json")
DIMENSION = 384 #bge-small-en-v1.5 dimension of output 

class VectorStore:
    def __init__(self):
        os.makedirs(INDEX_DIR,exist_ok=True)
        self._index, self._metadata = self._load_or_create()  
    
    def _load_or_create(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            logger.info("Loading existing FAISS index")
            index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, 'r') as f:
                metadata = json.load(f)
            logger.info("Loaded %d vectors from the FAISS", index.ntotal)
        else:
            logger.info("Creating new FAISS IndexflatIP (dim=%d)",DIMENSION)
            index  = faiss.IndexFlatIP(DIMENSION)
            metadata = [] #list of dicts, one per vector, same order as index
        return index, metadata
    
    def _save(self):
        faiss.write_index(self._index, INDEX_PATH)
        with open(METADATA_PATH, 'w') as f:
            json.dump(self._metadata, f, indent=2)
        logger.info("Saved FAISS index and metadata")

    def add(self, vector: np.ndarray, meta: dict):
        if vector.ndim == 1:
            vector = vector.reshape(1,-1)
        self._index.add(vector)
        self._metadata.append(meta)
        self._save()
        logger.info("added vector to index. Total: %d", self._index.ntotal)

    def search(self, query_vector: np.ndarray, top_k: int=100) -> list[dict]:
        if self._index.ntotal == 0:
            logger.warning("FAISS index is empty - no resumes indexed yet")
            return []
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1,-1)
        
        top_k = min(top_k, self._index.ntotal)
        #inner product
        scores, indices = self._index.search(query_vector, top_k)

        results = []
        for score , idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            entry = dict(self._metadata[idx])
            entry["score"] = float(score)
            results.append(entry)
        return results
    @property
    def total(self):
        return self._index.ntotal
    
vector_store = VectorStore()


