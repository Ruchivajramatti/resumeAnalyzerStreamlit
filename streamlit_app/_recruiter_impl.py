import io
import os
import requests
import streamlit as st
import pandas as pd


def get_api_url() -> str:
    try:
        return st.secrets["API_URL"]  # type: ignore[index]
    except Exception:
        return os.environ.get("API_URL", "http://localhost:8000")


def run():
    st.set_page_config(page_title="Recruiter Dashboard", page_icon="🏢", layout="wide")
    st.title("🏢 Recruiter Dashboard")

    jd_file = st.file_uploader("Upload Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="jd")
    resumes = st.file_uploader("Upload Candidate Resumes (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if st.button("Rank Candidates", type="primary"):
        if not jd_file or not resumes:
            st.error("Please upload a JD and at least one resume.")
        else:
            with st.spinner("Ranking..."):
                files = {"jd": (jd_file.name, jd_file.getvalue())}
                for i, f in enumerate(resumes):
                    files[f"resume_{i}"] = (f.name, f.getvalue())
                try:
                    resp = requests.post(f"{get_api_url()}/rank", files=files, timeout=180)
                    if resp.status_code != 200:
                        st.error(f"API error: {resp.status_code} {resp.text}")
                    else:
                        data = resp.json()
                        rows = []
                        for idx, r in enumerate(data["results"], start=1):
                            s = r["scores"]
                            score = s["similarity"] * 0.5 + s["skill_match"] * 0.3 + s["ats_compliance"] * 0.2
                            rows.append({
                                "Rank": idx,
                                "Filename": r["filename"],
                                "Composite Score": round(score*100, 1),
                                "Similarity %": round(s["similarity"]*100, 1),
                                "Skill Match %": round(s["skill_match"]*100, 1),
                                "ATS %": round(s["ats_compliance"]*100, 1),
                            })
                        df = pd.DataFrame(rows)
                        st.dataframe(df, use_container_width=True)

                        csv_buf = io.StringIO()
                        df.to_csv(csv_buf, index=False)
                        st.download_button("Download CSV", data=csv_buf.getvalue(), file_name="ranked_candidates.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"Request failed: {e}")
