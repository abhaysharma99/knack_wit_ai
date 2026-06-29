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
from app.embedder import embedder

logger = logging.getLogger(__name__)

INDEX_DIR = "/data/faiss"
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

    def reload(self):
        """Reload index and metadata from disk to catch updates from other processes."""
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            try:
                self._index = faiss.read_index(INDEX_PATH)
                with open(METADATA_PATH, 'r') as f:
                    self._metadata = json.load(f)
            except Exception as e:
                logger.error("Error reloading FAISS index: %s", e)

    def add(self, vector: np.ndarray, meta: dict):
        self.reload()
        if vector.ndim == 1:
            vector = vector.reshape(1,-1)
        self._index.add(vector)
        self._metadata.append(meta)
        self._save()
        logger.info("added vector to index. Total: %d", self._index.ntotal)

    def search(self, query_vector: np.ndarray, top_k: int=100) -> list[dict]:
        self.reload()
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
    
    # Add this method to the VectorStore class (after the search method, before @property total)

    def add_from_candidate(self, file_id: str, raw_text: str, candidate_meta: dict):
        """
        Embed candidate text and add to FAISS.
        Called when a new candidate is saved to DB.
        """
        try:
            if not raw_text or not raw_text.strip():
                logger.warning("Skipping FAISS index: raw_text is empty for file_id=%s", file_id)
                return
            
            # Embed the full resume text
            vector = embedder.encode([raw_text])[0]
            
            # Prepare metadata
            meta = {
                "file_id": str(file_id),
                **candidate_meta,  # includes name, domain, seniority, candidate_id, current_role
            }
            
            # Add to FAISS
            self.add(vector, meta)
            logger.info("Synced candidate to FAISS: file_id=%s, candidate_id=%s", 
                    file_id, candidate_meta.get("candidate_id"))
        except Exception as e:
            logger.error("Failed to sync candidate to FAISS: %s", e)
            # Don't re-raise — DB save should succeed even if FAISS fails

    @property
    def total(self):
        self.reload()
        return self._index.ntotal


    
vector_store = VectorStore()


