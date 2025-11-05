from __future__ import annotations

from typing import Dict, List

from .scoring import ats_checks, MatchScores


def generate_suggestions(resume_text: str, jd_text: str | None, scores: MatchScores, jd_keywords: List[str]) -> List[str]:
    tips: List[str] = []
    ats = ats_checks(resume_text)

    # Section tips
    for section, present in ats["section_presence"].items():
        if not present:
            tips.append(f"Add a clear '{section.title()}' section with concise bullet points.")

    # Bullet usage
    if ats["bullet_count"] < 5:
        tips.append("Use bullet points (• or -) to list achievements and responsibilities.")

    # Keyword coverage
    if jd_text:
        missing = [k for k in jd_keywords if k.lower() not in resume_text.lower()]
        if missing:
            tips.append(f"Include relevant keywords from the JD where applicable: {', '.join(missing[:10])}...")

    # Readability
    if scores.readability < 0.5:
        tips.append("Improve readability: use shorter sentences, active voice, and consistent formatting.")

    # Formatting heuristics
    if len(resume_text) > 20000:
        tips.append("Keep resume concise (1–2 pages); remove redundant details.")

    # Overall
    if scores.ats_compliance < 0.6:
        tips.append("Ensure ATS-friendly formatting: avoid tables, complex columns, or images.")

    if not tips:
        tips.append("Your resume looks good. Fine-tune phrasing and quantify achievements where possible.")

    return tips
