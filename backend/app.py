from __future__ import annotations

import io
from pathlib import Path
from typing import List

from flask import Flask, jsonify, request
from flask_cors import CORS

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from resume_analyzer.parsers import extract_text, clean_text
from resume_analyzer.nlp import extract_skills, keywords_tfidf
from resume_analyzer.scoring import aggregate_scores
from resume_analyzer.suggestions import generate_suggestions
from resume_analyzer import db as dbm


app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze_single():
    """Analyze one resume with optional JD text/file."""
    files = request.files
    form = request.form

    resume_file = files.get("resume")
    jd_file = files.get("jd")
    jd_text_in = form.get("jd_text", "")

    if not resume_file:
        return jsonify({"error": "resume file is required"}), 400

    # Save to temp in memory and parse
    # preserve suffix for parser
    resume_name = Path(resume_file.filename or "resume").name
    tmp_path = Path(f"tmp_{resume_name}")
    tmp_path.write_bytes(resume_file.read())
    resume_text = clean_text(extract_text(tmp_path))
    tmp_path.unlink(missing_ok=True)

    jd_text = jd_text_in
    if jd_file and not jd_text:
        jd_name = Path(jd_file.filename or "jd").name
        tmp_jd = Path(f"tmp_{jd_name}")
        tmp_jd.write_bytes(jd_file.read())
        jd_text = clean_text(extract_text(tmp_jd))
        tmp_jd.unlink(missing_ok=True)

    # NLP & scoring
    skills = extract_skills(resume_text)
    jd_keywords: List[str] = keywords_tfidf(jd_text) if jd_text else []
    scores = aggregate_scores(resume_text, jd_text, skills, jd_keywords)
    suggestions = generate_suggestions(resume_text, jd_text, scores, jd_keywords)

    # Persist basic artifacts
    dbm.init_db()
    with dbm.SessionLocal() as sess:
        r = dbm.Resume(filename=resume_file.filename, text=resume_text)
        sess.add(r)
        jd_id = None
        if jd_text:
            jd = dbm.JobDescription(title=None, text=jd_text)
            sess.add(jd)
            sess.flush()
            jd_id = jd.id
        sess.flush()
        ar = dbm.AnalysisResult(
            resume_id=r.id,
            jd_id=jd_id,
            similarity=scores.similarity,
            skill_match=scores.skill_match,
            keyword_coverage=scores.keyword_coverage,
            readability=scores.readability,
            ats_compliance=scores.ats_compliance,
            suggestions="\n".join(suggestions),
        )
        sess.add(ar)
        sess.commit()

    return jsonify({
        "skills": skills,
        "jd_keywords": jd_keywords,
        "scores": scores.__dict__,
        "suggestions": suggestions,
    })


@app.route("/rank", methods=["POST"])
def rank_bulk():
    """Recruiter flow: one JD and multiple resumes -> ranked list."""
    files = request.files
    jd_file = files.get("jd")
    if not jd_file:
        return jsonify({"error": "JD file is required"}), 400

    jd_name = Path(jd_file.filename or "jd").name
    tmp_jd = Path(f"tmp_{jd_name}")
    tmp_jd.write_bytes(jd_file.read())
    jd_text = clean_text(extract_text(tmp_jd))
    tmp_jd.unlink(missing_ok=True)
    jd_keywords: List[str] = keywords_tfidf(jd_text)

    results = []
    for key in files:
        if key.startswith("resume_"):
            f = files[key]
            tmp = Path(f"tmp_{key}")
            tmp.write_bytes(f.read())
            resume_text = clean_text(extract_text(tmp))
            tmp.unlink(missing_ok=True)
            skills = extract_skills(resume_text)
            scores = aggregate_scores(resume_text, jd_text, skills, jd_keywords)
            suggestions = generate_suggestions(resume_text, jd_text, scores, jd_keywords)
            results.append({
                "filename": f.filename,
                "scores": scores.__dict__,
                "skills": skills,
                "suggestions": suggestions,
            })

    results.sort(key=lambda r: (
        r["scores"]["similarity"] * 0.5 +
        r["scores"]["skill_match"] * 0.3 +
        r["scores"]["ats_compliance"] * 0.2
    ), reverse=True)

    return jsonify({"jd_keywords": jd_keywords, "results": results})


if __name__ == "__main__":
    dbm.init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
