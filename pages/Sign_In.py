import streamlit as st
from services.auth import render_auth_form, render_user_profile, check_auth

st.set_page_config(
    page_title="Sign In - AI Interview Coach",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from services.components import inject_styles, load_css

inject_styles()
load_css("auth.css")


# Auth container
st.markdown("""
<div style="text-align: center; margin-top: 40px; margin-bottom: 24px;">
    <div style="font-size: 18px; font-weight: 600; color: #111827;">AI Interview Coach</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if check_auth():
        render_user_profile()
    else:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <h2 style="font-size: 24px; font-weight: 600; color: #111827; margin-bottom: 8px;">Welcome back</h2>
            <p style="font-size: 14px; color: #6b7280;">Sign in to continue to your dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        render_auth_form()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("Back to Home", use_container_width=True):
            st.switch_page("Home.py")
