# app/explainer.py
"""
Explainability Layer — Phase 3, Item 6.

Pure template-based explanations — no LLM calls, no external dependencies.

Three outputs per candidate:
    reasons   — why this score (growth signal explanations)
    strengths — what the candidate is genuinely good at
    gaps      — what's missing compared to a typical profile
"""

import logging

logger = logging.getLogger(__name__)

# ── Thresholds used in templates ─────────────────────────────────────────────
_HIGH   = 0.70
_MEDIUM = 0.45
_LOW    = 0.30

# Typical skill count for a well-rounded candidate at each seniority
_EXPECTED_SKILL_COUNT = {
    "junior":     5,
    "mid":        8,
    "mid-senior": 10,
    "senior":     12,
    "lead":       14,
}

# Typical project count per seniority
_EXPECTED_PROJECT_COUNT = {
    "junior":     1,
    "mid":        2,
    "mid-senior": 3,
    "senior":     4,
    "lead":       5,
}


# ── Reasons ───────────────────────────────────────────────────────────────────

def _build_reasons(
    growth_features: dict,
    candidate: dict,
) -> list[str]:
    """
    Template sentences explaining each growth signal score.
    Always returns one sentence per signal — 4 reasons total.
    """
    reasons = []

    seniority        = (candidate.get("seniority") or "unknown").lower()
    experience_years = candidate.get("total_experience_years") or 0.0

    # ── growth_velocity ──────────────────────────────────────────────────
    v = growth_features["growth_velocity"]
    if v >= _HIGH:
        reasons.append(
            f"Reached {seniority.title()} level faster than average "
            f"({experience_years:.1f} yrs experience)."
        )
    elif v >= _MEDIUM:
        reasons.append(
            f"Progression to {seniority.title()} is on par with industry average."
        )
    else:
        reasons.append(
            f"Progression to {seniority.title()} is slower than typical "
            f"({experience_years:.1f} yrs experience)."
        )

    # ── consistency ──────────────────────────────────────────────────────
    c = growth_features["consistency"]
    if c >= _HIGH:
        reasons.append(
            "Highly specialized skill set — strong depth in a focused domain."
        )
    elif c >= _MEDIUM:
        reasons.append(
            "Balanced skill set — mix of specialization and breadth."
        )
    else:
        reasons.append(
            "Generalist skill profile — broad across multiple domains."
        )

    # ── expansion_rate ───────────────────────────────────────────────────
    e = growth_features["expansion_rate"]
    if e >= _HIGH:
        reasons.append(
            "High skill category diversity — technical, tools, and languages covered."
        )
    elif e >= _MEDIUM:
        reasons.append(
            "Moderate skill diversity — covers 2 skill categories."
        )
    else:
        reasons.append(
            "Narrow skill category coverage — mostly one type of skill."
        )

    # ── complexity_growth ────────────────────────────────────────────────
    g = growth_features["complexity_growth"]
    projects = candidate.get("projects") or []
    if g >= _HIGH:
        reasons.append(
            f"High project complexity — {len(projects)} projects with rich tech stacks."
        )
    elif g >= _MEDIUM:
        reasons.append(
            f"Moderate project complexity — {len(projects)} projects with reasonable depth."
        )
    else:
        reasons.append(
            f"Limited project complexity — {len(projects)} project(s) with narrow tech usage."
        )

    return reasons


# ── Strengths ─────────────────────────────────────────────────────────────────

def _build_strengths(
    growth_features: dict,
    candidate: dict,
) -> list[str]:
    """
    Positive observations about the candidate.
    Only adds a strength if the signal genuinely earns it (above threshold).
    Returns 1–5 strengths.
    """
    strengths = []

    skills   = candidate.get("skills",   []) or []
    projects = candidate.get("projects", []) or []
    domain   = candidate.get("domain") or "their domain"

    # Fast leveler
    if growth_features["growth_velocity"] >= _HIGH:
        strengths.append(
            f"Fast career progression — leveled up ahead of average timeline."
        )

    # Deep specialist
    if growth_features["consistency"] >= _HIGH:
        technical_skills = [
            s["name"] for s in skills
            if (s.get("category") or "").lower() == "technical"
        ][:5]
        if technical_skills:
            strengths.append(
                f"Strong technical depth in {domain}: "
                f"{', '.join(technical_skills)}."
            )

    # Broad skill coverage
    if growth_features["expansion_rate"] >= _HIGH:
        strengths.append(
            "Well-rounded profile — spans technical skills, tools, and languages."
        )

    # Complex projects
    if growth_features["complexity_growth"] >= _MEDIUM:
        tool_skills = [
            s["name"] for s in skills
            if (s.get("category") or "").lower() == "tool"
        ][:4]
        if tool_skills:
            strengths.append(
                f"Practical tool experience: {', '.join(tool_skills)}."
            )

    # Project portfolio
    if len(projects) >= 2:
        project_titles = [p["title"] for p in projects if p.get("title")][:3]
        if project_titles:
            strengths.append(
                f"Demonstrated project portfolio: {', '.join(project_titles)}."
            )

    # Fallback — always return at least one strength
    if not strengths:
        strengths.append(
            f"Has foundational experience in {domain}."
        )

    return strengths


# ── Gaps ──────────────────────────────────────────────────────────────────────

def _build_gaps(
    growth_features: dict,
    candidate: dict,
) -> list[str]:
    """
    Honest observations about what's missing.
    Only flags a gap if the signal is genuinely low.
    Returns 0–4 gaps (empty list = no significant gaps).
    """
    gaps     = []
    skills   = candidate.get("skills",   []) or []
    projects = candidate.get("projects", []) or []
    seniority = (candidate.get("seniority") or "junior").lower()

    # Slow progression
    if growth_features["growth_velocity"] < _LOW:
        gaps.append(
            "Career progression is slower than typical for this seniority level."
        )

    # Narrow skill categories
    if growth_features["expansion_rate"] < _MEDIUM:
        categories_present = {
            (s.get("category") or "technical").lower()
            for s in skills
        }
        missing = {"technical", "tool", "language"} - categories_present
        if missing:
            gaps.append(
                f"Limited skill diversity — missing: {', '.join(sorted(missing))}."
            )

    # Fewer skills than expected for seniority
    expected_skills = _EXPECTED_SKILL_COUNT.get(seniority, 8)
    if len(skills) < expected_skills:
        gaps.append(
            f"Fewer skills listed than typical for {seniority.title()} level "
            f"({len(skills)} vs expected {expected_skills}+)."
        )

    # Fewer projects than expected
    expected_projects = _EXPECTED_PROJECT_COUNT.get(seniority, 2)
    if len(projects) < expected_projects:
        gaps.append(
            f"Limited project history — {len(projects)} project(s) listed "
            f"(expected {expected_projects}+ for {seniority.title()})."
        )

    return gaps


# ── Main entry point ──────────────────────────────────────────────────────────

def explain(
    candidate: dict,
    growth_features: dict,
) -> dict:
    """
    Generate full explainability output for a candidate.

    Args:
        candidate:       dict from get_candidate_by_id()
        growth_features: dict from compute_growth_features()

    Returns:
        {
            "reasons":   list[str],   # 4 sentences, one per signal
            "strengths": list[str],   # 1–5 positive observations
            "gaps":      list[str],   # 0–4 honest gaps
        }
    """
    reasons   = _build_reasons(growth_features, candidate)
    strengths = _build_strengths(growth_features, candidate)
    gaps      = _build_gaps(growth_features, candidate)

    logger.debug(
        "Explanation for %s: %d reasons, %d strengths, %d gaps",
        candidate.get("name", "unknown"),
        len(reasons), len(strengths), len(gaps),
    )

    return {
        "reasons":   reasons,
        "strengths": strengths,
        "gaps":      gaps,
    }

    