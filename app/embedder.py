# this file will help us to encode text to the vectors using FAISS
'''embdder consists of the sentence transformer - BGE-M3
    encodes text to the dense vectors 
    loaded once at startup and then it is reused never instantiate it more than once
'''
import logging
import numpy as np 
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
MODEL_NAME = "BAAI/bge-small-en-v1.5"
class Embedder:
    def __init__(self):
        logger.info("Loading Embedding Model: %s", MODEL_NAME)
        self.model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding Model Loaded")
    
    def encode(self, text: list[str]):
        """
        Encode a list of strings into L2-normalized float32 vectors.
        Returns shape: (len(texts), 1024)
        Normalized so inner product == cosine similarity.
        """
        if isinstance(text, str):
            text = [text]
        vectors = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32
        )
        return vectors.astype(np.float32)
    
# Singleton — import this everywhere, don't reinstantiate
embedder = Embedder()