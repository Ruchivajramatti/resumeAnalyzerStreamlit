from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import math
import re


@dataclass
class MatchScores:
    similarity: float
    skill_match: float
    keyword_coverage: float
    readability: float
    ats_compliance: float


def tfidf_cosine_similarity(a: str, b: str) -> float:
    """Approximate cosine similarity using token frequency vectors and stopwords filtering."""
    if not a.strip() or not b.strip():
        return 0.0
    stop = {
        'the','and','for','with','from','that','this','you','your','are','was','were','will','shall','would','could','should','have','has','had','but','not','can','our','their','his','her','its','they','them','him','she','he','we','i','to','in','of','on','at','by','as','or','an','a'
    }
    def vecify(t: str):
        tokens = re.findall(r"[a-zA-Z]{2,}", t.lower())
        v = {}
        for tok in tokens:
            if tok in stop:
                continue
            v[tok] = v.get(tok, 0) + 1
        return v
    va = vecify(a)
    vb = vecify(b)
    keys = set(va) | set(vb)
    dot = sum(va.get(k,0)*vb.get(k,0) for k in keys)
    na = math.sqrt(sum(c*c for c in va.values()))
    nb = math.sqrt(sum(c*c for c in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return float(max(0.0, min(1.0, dot/(na*nb))))


def ats_checks(text: str, required_sections: List[str] | None = None) -> Dict[str, bool | float]:
    """Simple ATS heuristics.
    - Section presence: Education, Experience, Skills, Projects.
    - Keyword density: ratio of non-stopword tokens.
    - Bullet usage: count of '-' or '•'.
    """
    t = text.lower()
    sections = required_sections or ["education", "experience", "skills", "projects"]
    section_presence = {s: (s in t) for s in sections}

    words = re.findall(r"[a-zA-Z]+", t)
    stop = {
        'the','and','for','with','from','that','this','you','your','are','was','were','will','shall','would','could','should','have','has','had','but','not','can','our','their','his','her','its','they','them','him','she','he','we','i','to','in','of','on','at','by','as','or','an','a'
    }
    non_stop = [w for w in words if w not in stop]
    density = (len(non_stop) / max(1, len(words))) if words else 0.0
    bullets = len(re.findall(r"(^|\n)[\-•]", text))

    score = (
        0.5 * (sum(section_presence.values()) / len(sections)) +
        0.3 * min(1.0, density) +
        0.2 * min(1.0, bullets / 10.0)
    )

    return {
        "section_presence": section_presence,
        "keyword_density": density,
        "bullet_count": bullets,
        "score": float(max(0.0, min(1.0, score))),
    }


def readability_score(text: str) -> float:
    try:
        import textstat
        fk = textstat.flesch_reading_ease(text)
        # Normalize Flesch score (~0-100) to 0-1
        return float(max(0.0, min(1.0, fk / 100.0)))
    except Exception:
        return 0.5


def aggregate_scores(resume_text: str, jd_text: str, skills_found: List[str], jd_keywords: List[str]) -> MatchScores:
    sim = tfidf_cosine_similarity(resume_text, jd_text) if jd_text else 0.0
    jd_kw_set = set([k.lower() for k in jd_keywords])
    skills_set = set([s.lower() for s in skills_found])
    skill_match = len(skills_set & jd_kw_set) / max(1, len(jd_kw_set)) if jd_kw_set else (0.7 if skills_set else 0.0)

    keyword_coverage = 0.0
    if jd_kw_set:
        covered = sum(1 for k in jd_kw_set if k in resume_text.lower())
        keyword_coverage = covered / len(jd_kw_set)

    ats = ats_checks(resume_text)
    read = readability_score(resume_text)

    return MatchScores(
        similarity=float(sim),
        skill_match=float(max(0.0, min(1.0, skill_match))),
        keyword_coverage=float(max(0.0, min(1.0, keyword_coverage))),
        readability=read,
        ats_compliance=ats["score"],
    )
