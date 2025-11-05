import io
import json
import requests
import streamlit as st
import pandas as pd

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Student Dashboard", page_icon="🎓", layout="wide")
st.title("🎓 Student Dashboard")

with st.sidebar:
    st.markdown("### ATS Templates")
    st.download_button(
        label="Download ATS Template (TXT)",
        data=("""Name\nEmail | Phone | LinkedIn\n\nSummary\n- 2-3 lines describing expertise and impact.\n\nSkills\n- Python, NLP, Machine Learning, Flask, Streamlit, SQL\n\nProjects\n- Project Name — brief description; tech stack; quantified results.\n\nExperience\n- Role @ Company — dates\n  • Achievement with metric; • Responsibility with outcome\n\nEducation\n- Degree, College, Year\n"""),
        file_name="ATS_Template.txt",
    )

st.subheader("Analyze Your Resume")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="resume")
with col2:
    jd_option = st.radio("Provide Job Description", ["Upload JD file", "Paste JD text", "Skip"], horizontal=True)
    jd_file = None
    jd_text = ""
    if jd_option == "Upload JD file":
        jd_file = st.file_uploader("Upload JD (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="jd")
    elif jd_option == "Paste JD text":
        jd_text = st.text_area("Paste JD text", height=200)


if st.button("Analyze", type="primary"):
    if not resume_file:
        st.error("Please upload your resume.")
    else:
        with st.spinner("Analyzing..."):
            files = {"resume": resume_file.getvalue()}
            data = {}
            if jd_file is not None:
                files["jd"] = jd_file.getvalue()
            elif jd_text.strip():
                data["jd_text"] = jd_text

            # Build multipart request properly
            mfiles = {}
            if "resume" in files:
                mfiles["resume"] = (resume_file.name, files["resume"])  # type: ignore
            if "jd" in files:
                mfiles["jd"] = (jd_file.name, files["jd"])  # type: ignore

            try:
                resp = requests.post(f"{API_URL}/analyze", files=mfiles, data=data, timeout=120)
                if resp.status_code != 200:
                    st.error(f"API error: {resp.status_code} {resp.text}")
                else:
                    result = resp.json()
                    st.success("Analysis complete")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    s = result["scores"]
                    c1.metric("Similarity", f"{s['similarity']*100:.0f}%")
                    c2.metric("Skill Match", f"{s['skill_match']*100:.0f}%")
                    c3.metric("Keyword Coverage", f"{s['keyword_coverage']*100:.0f}%")
                    c4.metric("Readability", f"{s['readability']*100:.0f}%")
                    c5.metric("ATS Compliance", f"{s['ats_compliance']*100:.0f}%")

                    st.markdown("### Missing / JD Keywords")
                    jd_kw = set(result.get("jd_keywords", []))
                    skills = set(result.get("skills", []))
                    missing = sorted([k for k in jd_kw if k.lower() not in (kw.lower() for kw in skills)])
                    df = pd.DataFrame({
                        "JD Keywords": list(jd_kw),
                        "Present in Resume": [k.lower() not in (kw.lower() for kw in missing) for k in jd_kw],
                    })
                    st.dataframe(df, use_container_width=True)

                    st.markdown("### Suggestions")
                    for tip in result.get("suggestions", []):
                        st.write("- ", tip)
            except Exception as e:
                st.error(f"Request failed: {e}")
