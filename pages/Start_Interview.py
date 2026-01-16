import streamlit as st
from services.components import render_navbar, require_auth, load_css, inject_styles
from services.interview_manager import (
    initialize_session_state,
    render_setup_phase,
    render_interview_phase,
    render_results_phase
)

st.set_page_config(
    page_title="New Interview - AI Interview Coach",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

require_auth()
inject_styles()
load_css("interview.css")

render_navbar(active_page="Interview")

# Initialize session state
initialize_session_state()

# Page header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 28px; font-weight: 600; color: #111827; margin-bottom: 4px;">New Interview</h1>
    <p style="font-size: 15px; color: #6b7280;">Practice with AI-generated questions based on your resume</p>
</div>
""", unsafe_allow_html=True)

# Main Logic Flow
if not st.session_state.questions and not st.session_state.interview_complete:
    render_setup_phase()

elif st.session_state.questions and not st.session_state.interview_complete:
    render_interview_phase()

elif st.session_state.interview_complete:
    render_results_phase()
