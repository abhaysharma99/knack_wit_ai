# app/growth_features.py
"""
Growth Feature Extractor — Phase 3, Item 1.

Computes 4 normalized growth signals (0.0–1.0) from a candidate dict.
All signals are rule-based — no ML, no external calls.

Signals:
    growth_velocity   — leveled up faster than average for their seniority?
    consistency       — how specialized/focused is their skill set?
    expansion_rate    — how many distinct skill categories do they have?
    complexity_growth — how complex are their projects?
"""

import logging

logger = logging.getLogger(__name__)

# Expected years of experience per seniority level (industry average)
_EXPECTED_YEARS = {
    "junior":     1.0,
    "mid":        3.0,
    "mid-senior": 5.0,
    "senior":     7.0,
    "lead":       10.0,
}

# Max cap for velocity ratio before normalization
_VELOCITY_CAP = 2.0

# Max expected (project_count × avg_techs) for complexity normalization
_COMPLEXITY_MAX = 15.0


def _compute_growth_velocity(seniority: str, experience_years: float) -> float:
    """
    How fast did they reach their current seniority vs the average?

    Formula:
        ratio = expected_years / actual_years
        (ratio > 1 means faster than average)
        normalized = min(ratio, _VELOCITY_CAP) / _VELOCITY_CAP

    Examples:
        Senior (expected 7 yrs) with 5 yrs actual → 7/5 = 1.40 → 0.70
        Mid    (expected 3 yrs) with 2 yrs actual → 3/2 = 1.50 → 0.75
        Junior (expected 1 yr)  with 3 yrs actual → 1/3 = 0.33 → 0.17
    """
    level = seniority.lower().strip() if seniority else "junior"
    expected = _EXPECTED_YEARS.get(level, 3.0)
    actual   = experience_years or 1.0      # avoid division by zero

    ratio      = expected / actual
    normalized = min(ratio, _VELOCITY_CAP) / _VELOCITY_CAP
    return round(normalized, 4)


def _compute_consistency(skills: list[dict]) -> float:
    """
    How focused is the candidate's skill set?

    Formula:
        count skills per category
        consistency = dominant_category_count / total_skills

    Examples:
        10 technical, 1 tool → 10/11 = 0.91  (strong specialist)
        3 technical, 3 tool, 3 soft → 3/9 = 0.33  (generalist)
    """
    if not skills:
        return 0.5     # neutral — no data

    category_counts: dict[str, int] = {}
    for s in skills:
        cat = (s.get("category") or "technical").lower().strip()
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total    = sum(category_counts.values())
    dominant = max(category_counts.values())
    return round(dominant / total, 4)


def _compute_expansion_rate(skills: list[dict]) -> float:
    """
    How many distinct skill categories does the candidate have?

    Formula:
        expansion_rate = distinct_categories / 4
        (4 = max possible: technical, tool, language, soft)

    Examples:
        technical + tool + language = 3/4 = 0.75
        technical only              = 1/4 = 0.25
    """
    if not skills:
        return 0.0

    distinct = len({
        (s.get("category") or "technical").lower().strip()
        for s in skills
    })
    return round(min(distinct / 4.0, 1.0), 4)


def _compute_complexity_growth(projects: list[dict]) -> float:
    """
    How complex are the candidate's projects?

    Formula:
        for each project: count techs = len(technologies.split(","))
        avg_techs = mean of tech counts across all projects
        complexity = (project_count × avg_techs) / _COMPLEXITY_MAX  (capped at 1.0)

    Examples:
        5 projects, avg 3 techs → 5×3 / 15 = 1.00 (capped)
        2 projects, avg 2 techs → 2×2 / 15 = 0.27
        0 projects              → 0.0
    """
    if not projects:
        return 0.0

    tech_counts = []
    for p in projects:
        techs = p.get("technologies") or ""
        count = len([t.strip() for t in techs.split(",") if t.strip()])
        tech_counts.append(max(count, 1))   # min 1 even if technologies is empty

    project_count = len(projects)
    avg_techs     = sum(tech_counts) / len(tech_counts)
    raw           = project_count * avg_techs
    return round(min(raw / _COMPLEXITY_MAX, 1.0), 4)


def compute_growth_features(candidate: dict) -> dict:
    """
    Main entry point. Takes a candidate dict (from get_candidate_by_id)
    and returns a dict of 4 normalized growth signals.

    Args:
        candidate: dict with keys:
            seniority, total_experience_years, skills (list), projects (list)

    Returns:
        {
            "growth_velocity":   float,
            "consistency":       float,
            "expansion_rate":    float,
            "complexity_growth": float,
        }
    """
    seniority        = candidate.get("seniority") or "unknown"
    experience_years = candidate.get("total_experience_years") or 0.0
    skills           = candidate.get("skills",   []) or []
    projects         = candidate.get("projects", []) or []

    features = {
        "growth_velocity":   _compute_growth_velocity(seniority, experience_years),
        "consistency":       _compute_consistency(skills),
        "expansion_rate":    _compute_expansion_rate(skills),
        "complexity_growth": _compute_complexity_growth(projects),
    }

    logger.debug(
        "Growth features for %s: %s",
        candidate.get("name", "unknown"),
        features,
    )
    return features

