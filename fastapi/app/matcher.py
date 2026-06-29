# app/matcher.py
import logging
import math
from app.schemas import JDStructured
from app.embedder import embedder
from app.vector_store import vector_store
from app.reranker import reranker
from app.db.crud import get_chunks_by_file_id, get_candidate_by_file_id

logger = logging.getLogger(__name__)

W_FAISS  = 0.3
W_RERANK = 0.4
W_FIT    = 0.3


def build_jd_query(jd: JDStructured) -> str:
    parts = [
        f"Role: {jd.role}",
        f"Domain: {jd.domain or 'Unknown'}",
        f"Seniority: {jd.seniority or 'Unknown'}",
        f"Required skills: {', '.join(jd.required_skills)}",
        f"Required skills: {', '.join(jd.required_skills)}",
        f"Preferred skills: {', '.join(jd.preferred_skills)}",
        f"Experience: {jd.experience_years or 0} years",
    ]
    return " | ".join(parts)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _compute_fit_score(jd: JDStructured, candidate_data: dict | None) -> float:
    """
    candidate_data can come from:
    - DB (dict with 'skills' list of dicts)
    - FAISS metadata directly (dict with 'domain', 'seniority', 'current_role')
    """
    if candidate_data is None:
        return 0.0

    # Skill overlap — only possible if DB candidate with skills exists
    required  = {s.lower() for s in jd.required_skills}
    preferred = {s.lower() for s in jd.preferred_skills}

    # Skills can come from DB candidate or from metadata current_role/domain text
    db_skills = candidate_data.get("skills", [])
    candidate_skills = {s["name"].lower() for s in db_skills} if db_skills else set()

    # If no explicit skills, try to match from current_role and domain text
    if not candidate_skills:
        role_text = (candidate_data.get("current_role") or "").lower()
        domain_text = (candidate_data.get("domain") or "").lower()
        combined = role_text + " " + domain_text
        # check which required skills appear in the role/domain text
        candidate_skills = {s for s in required if s in combined}

    req_overlap  = len(required  & candidate_skills) / len(required)  if required  else 0.5
    pref_overlap = len(preferred & candidate_skills) / len(preferred) if preferred else 0.5
    skill_score  = 0.7 * req_overlap + 0.3 * pref_overlap

    # Experience match
    jd_exp   = jd.experience_years or 0
    cand_exp = candidate_data.get("total_experience_years") or 0
    exp_score = 1.0 if jd_exp == 0 or cand_exp >= jd_exp else cand_exp / jd_exp

    # Domain match
    jd_domain   = (jd.domain or "").lower().strip()
    cand_domain = (candidate_data.get("domain") or "").lower().strip()
    if not jd_domain or not cand_domain:
        domain_score = 0.5
    elif jd_domain == cand_domain:
        domain_score = 1.0
    elif any(w in cand_domain for w in jd_domain.split()):
        domain_score = 0.75
    else:
        domain_score = 0.0

    # Seniority match bonus
    jd_seniority   = (jd.seniority or "").lower().strip()
    cand_seniority = (candidate_data.get("seniority") or "").lower().strip()
    seniority_bonus = 0.1 if jd_seniority and jd_seniority == cand_seniority else 0.0

    base = (skill_score + exp_score + domain_score) / 3.0
    return round(min(base + seniority_bonus, 1.0), 4)


def _build_resume_text_from_metadata(meta: dict) -> str:
    """
    Build a descriptive text from FAISS metadata when no chunks exist.
    Used for reranking seeded/legacy candidates.
    """
    parts = []
    if meta.get("name"):
        parts.append(f"Candidate: {meta['name']}")
    if meta.get("current_role"):
        parts.append(f"Role: {meta['current_role']}")
    if meta.get("domain"):
        parts.append(f"Domain: {meta['domain']}")
    if meta.get("seniority"):
        parts.append(f"Seniority: {meta['seniority']}")
    return " | ".join(parts) if parts else "No resume text available"


def match_candidates(jd: JDStructured, top_n: int = 10) -> list[dict]:
    # Step 1 — encode JD
    query_text   = build_jd_query(jd)
    query_vector = embedder.encode([query_text])[0]
    logger.info("JD encoded. Query: %s", query_text[:120])

    # Step 2 — FAISS retrieval (top 100)
    faiss_results = vector_store.search(query_vector, top_k=100)
    if not faiss_results:
        logger.warning("No candidates in FAISS index.")
        return []
    logger.info("FAISS returned %d candidates.", len(faiss_results))

    # Step 3 — build resume text + candidate data for each hit
    for hit in faiss_results:
        file_id = hit.get("file_id", "")

        # Try DB first for uploaded resumes
        db_candidate = get_candidate_by_file_id(file_id)

        # Build resume text
        resume_text = ""
        if db_candidate and db_candidate.get("raw_text"):
            resume_text = db_candidate["raw_text"]
        else:
            chunks = get_chunks_by_file_id(file_id)
            if chunks:
                resume_text = " ".join(c["content"] for c in chunks)

        # Fall back to metadata text for seeded candidates
        if not resume_text.strip():
            resume_text = _build_resume_text_from_metadata(hit)

        # Merge DB data with FAISS metadata
        # FAISS metadata already has name, domain, seniority for seeded candidates
        candidate_data = {
            "name":                   hit.get("name") or (db_candidate or {}).get("name"),
            "domain":                 hit.get("domain") or (db_candidate or {}).get("domain"),
            "seniority":              hit.get("seniority") or (db_candidate or {}).get("seniority"),
            "current_role":           hit.get("current_role") or (db_candidate or {}).get("current_role"),
            "total_experience_years": (db_candidate or {}).get("total_experience_years"),
            "skills":                 (db_candidate or {}).get("skills", []),
        }

        hit["resume_text"]    = resume_text
        hit["_candidate"]     = candidate_data
        hit["candidate_name"] = candidate_data["name"]

    # Step 4 — cross-encoder rerank
    ranked = reranker.rerank(
        query=query_text,
        candidates=faiss_results,
        text_key="resume_text",
        top_n=top_n,
    )

    # Steps 5-6 — fit score + final score
    results = []
    for i, hit in enumerate(ranked):
        candidate    = hit.pop("_candidate", None)
        faiss_score  = hit.get("score", hit.get("faiss_score", 0.0))
        rerank_score = hit.get("rerank_score", 0.0)
        fit_score    = _compute_fit_score(jd, candidate)
        rerank_norm  = _sigmoid(rerank_score)
        final_score  = round(W_FAISS * faiss_score + W_RERANK * rerank_norm + W_FIT * fit_score, 4)

        results.append({
            "rank":           i + 1,
            "file_id":        hit.get("file_id", ""),
            "candidate_id":   hit.get("candidate_id"),
            "candidate_name": hit.get("candidate_name"),
            "faiss_score":    round(float(faiss_score),  4),
            "rerank_score":   round(float(rerank_score), 4),
            "fit_score":      fit_score,
            "final_score":    final_score,
            "file_path":      hit.get("file_path"),
        })

    logger.info("Returning %d ranked candidates.", len(results))
    return results
