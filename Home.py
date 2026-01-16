import streamlit as st

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from services.components import inject_styles, load_css

inject_styles()
load_css("home.css")



# Navigation
st.markdown("""
<div class="nav-bar">
    <div class="nav-inner">
        <div class="nav-brand">AI Interview Coach</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Prepare for your<br>next interview</h1>
    <p class="hero-subtitle">
        Practice with AI-powered mock interviews. Get instant feedback, 
        personalized questions, and improve your performance.
    </p>
</div>
""", unsafe_allow_html=True)

# CTA Button - centered
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/Sign_In.py")

# Features Section
st.markdown("""
<div class="features-section">
    <h2 class="section-title">How it works</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-number">1</div>
            <div class="feature-title">Upload Resume</div>
            <div class="feature-desc">Upload your PDF resume. Our AI analyzes your experience to generate relevant questions.</div>
        </div>
        <div class="feature-card">
            <div class="feature-number">2</div>
            <div class="feature-title">Practice Interview</div>
            <div class="feature-desc">Answer role-specific questions across technical, behavioral, and HR categories.</div>
        </div>
        <div class="feature-card">
            <div class="feature-number">3</div>
            <div class="feature-title">Get Feedback</div>
            <div class="feature-desc">Receive instant AI scoring, detailed feedback, and ideal answers for improvement.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Stats Section
st.markdown("""
<div class="stats-section">
    <div class="stats-grid">
        <div>
            <div class="stat-value">12+</div>
            <div class="stat-label">Job Roles</div>
        </div>
        <div>
            <div class="stat-value">3</div>
            <div class="stat-label">Interview Types</div>
        </div>
        <div>
            <div class="stat-value">AI</div>
            <div class="stat-label">Powered Feedback</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Additional Features
st.markdown("""
<div class="features-section">
    <h2 class="section-title">Features</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-title">Smart Questions</div>
            <div class="feature-desc">Questions tailored to your resume and target role using advanced language models.</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">Instant Scoring</div>
            <div class="feature-desc">Get real-time scores from 1-10 with detailed feedback on every answer.</div>
        </div>
        <div class="feature-card">
            <div class="feature-title">Progress Tracking</div>
            <div class="feature-desc">Track your performance over time with history and trend charts.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer-section">
    <p>AI Interview Coach</p>
</div>
""", unsafe_allow_html=True)
