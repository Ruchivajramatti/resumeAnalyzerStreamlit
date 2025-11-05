import streamlit as st

st.set_page_config(page_title="Resume Analyzer", page_icon="📝", layout="wide")

st.title("Resume Analyzer using NLP")
st.markdown(
    """
    Welcome! Use the pages on the left:
    - Student Dashboard: analyze your resume vs. a Job Description and get suggestions.
    - Recruiter Dashboard: upload a JD and multiple resumes to rank candidates.
    """
)

st.info("Tip: ATS-friendly templates are available in the Student Dashboard.")
