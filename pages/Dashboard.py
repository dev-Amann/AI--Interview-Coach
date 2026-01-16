import streamlit as st
from services.components import render_navbar, require_auth, load_css, inject_styles
from services.database import get_user_stats

st.set_page_config(
    page_title="Dashboard - AI Interview Coach",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

require_auth()
inject_styles()
load_css("dashboard.css")

render_navbar(active_page="Dashboard")

# Page header
from services.auth import get_current_user
user = get_current_user()
user_name = user.get('name', 'there') if user else 'there'

st.markdown(f"""
<div style="margin-bottom: 32px;">
    <h1 style="font-size: 28px; font-weight: 600; color: #111827; margin-bottom: 4px;">Dashboard</h1>
    <p style="font-size: 15px; color: #6b7280;">Welcome back, {user_name}</p>
</div>
""", unsafe_allow_html=True)

# Get stats
user_id = user.get('id') if user else None
stats = get_user_stats(user_id) if user_id else None

# Metrics
if stats and stats.get('total_interviews', 0) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('total_interviews', 0)}</div>
            <div class="metric-label">Interviews</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg = stats.get('average_score', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg:.1f}</div>
            <div class="metric-label">Avg Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        role = stats.get('top_role', 'N/A') or 'N/A'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="font-size: 18px;">{role}</div>
            <div class="metric-label">Top Role</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 8px;">No interviews yet</div>
        <div style="font-size: 14px; color: #6b7280;">Complete your first interview to see stats here</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick actions
st.markdown("""
<h2 style="font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 16px;">Quick Actions</h2>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">New Interview</div>
        <div class="action-desc">Start a practice interview with AI-generated questions tailored to your resume and target role.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Interview", type="primary", use_container_width=True, key="start_int"):
        st.switch_page("pages/Start_Interview.py")

with col2:
    st.markdown("""
    <div class="action-card">
        <div class="action-title">View History</div>
        <div class="action-desc">Review your past interviews, scores, and feedback. Download reports for your records.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View History", use_container_width=True, key="view_hist"):
        st.switch_page("pages/History.py")
