# Resume Analyzer using NLP

A dual-dashboard application for Students and Recruiters:
- Students: upload resume (and optional Job Description), get ATS-style score, similarity, missing skills, and improvement suggestions; download ATS templates.
- Recruiters: upload JD and multiple resumes to get ranked shortlist with insights.

Tech stack: Streamlit (UI), Flask (API), SQLite (SQLAlchemy), spaCy + scikit-learn for NLP, PyMuPDF/pdfminer/docx2txt for parsing.

## Features
- Robust text extraction from PDF/DOCX
- NLP parsing (skills, entities), keyword extraction (TF-IDF, RAKE-like simple), similarity via cosine on TF-IDF
- ATS checks (formatting heuristics, keyword density, section presence)
- Suggestions engine
- Dual dashboards in Streamlit
- Simple SQLite persistence

## Local setup (Windows PowerShell)

1) Create a virtual environment and install deps

```powershell
python -m venv .venv ; . .venv/Scripts/Activate.ps1 ; pip install -U pip ; pip install -r requirements.txt
```

2) Download spaCy model (first run only)

```powershell
python -m spacy download en_core_web_sm
```

3) Initialize the database

```powershell
python scripts/init_db.py
```

4) Run the backend API (optional, Streamlit can also call local Python directly; we keep API for separation)

```powershell
python backend/app.py
```

5) Run the Streamlit app

```powershell
streamlit run streamlit_app/Home.py
```

Optional: set API URL for Streamlit
- Default is http://localhost:8000
- You can override via environment variable:

```powershell
$env:API_URL = "http://localhost:8000"
```

Or via Streamlit secrets (create `E:\minor 1\.streamlit\secrets.toml`):

```
API_URL = "http://localhost:8000"
```

## Deploy to Streamlit Cloud
- Push this repo to GitHub
- In Streamlit Cloud, set the main file to `streamlit_app/Home.py`
- Add `requirements.txt`
- For PDFs parsing on cloud, PyMuPDF is included in requirements

## Project Structure

- `resume_analyzer/` core library (parsers, nlp, scoring, suggestions, db)
- `backend/` Flask API to orchestrate analyze endpoints
- `streamlit_app/` Streamlit UI with pages for students and recruiters
- `assets/templates/` ATS-friendly templates and references
- `scripts/` helper scripts (db init, demo data)

## Notes
- This is a reference implementation suitable for academic projects. You can extend the models and add authentication for production.