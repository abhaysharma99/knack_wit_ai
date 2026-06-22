from app.embedder import embed_passage
from app.vector_store import add_candidate, search

v1 = embed_passage(
    "Python FastAPI Docker"
)

v2 = embed_passage(
    "Java Spring Boot"
)

add_candidate("cand1", v1)
add_candidate("cand2", v2)

query = embed_passage(
    "Python backend developer"
)

results = search(query)

print(results)