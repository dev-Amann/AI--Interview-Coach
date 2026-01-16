import streamlit as st
from services.components import render_navbar, require_auth, load_css, inject_styles
from services.database import get_user_history, Database
from services.auth import get_current_user
from services.pdf_generator import generate_interview_report

st.set_page_config(
    page_title="History - AI Interview Coach",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="collapsed"
)

require_auth()
inject_styles()
load_css("history.css")

render_navbar(active_page="History")

# Page header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="font-size: 28px; font-weight: 600; color: #111827; margin-bottom: 4px;">Interview History</h1>
    <p style="font-size: 15px; color: #6b7280;">Review your past interviews and track your progress</p>
</div>
""", unsafe_allow_html=True)

# Get history
user = get_current_user()
user_id = user.get('id') if user else None
history = get_user_history(user_id) if user_id else []

if history and len(history) > 0:
    for item in history:
        score = float(item.get('score', 0))
        status = "Qualified" if score >= 6.5 else "Needs Practice"
        session_id = item.get('id')
        role = item.get('role', 'Unknown Role')
        date = item.get('date', 'Unknown date')
        
        # Expandable session
        with st.expander(f"{role} - {date} - Score: {score:.1f}/10 ({status})"):
            
            # Get session details
            db = Database()
            session_details = db.get_session_details(session_id)
            
            if session_details and session_details.get('responses'):
                # Overall info
                category = session_details.get('category', 'N/A')
                difficulty = session_details.get('difficulty', 'N/A')
                
                st.info(f"**Category:** {category} | **Difficulty:** {difficulty}")
                
                # PDF Download
                report_data = {
                    'job_role': role,
                    'user_name': user.get('name', 'User'),
                    'category': category,
                    'difficulty': difficulty,
                    'avg_score': score,
                    'qualified': (score >= 6.5),
                    'questions': [r.get('question') for r in session_details.get('responses', [])],
                    'answers': {i: r.get('answer') for i, r in enumerate(session_details.get('responses', []))},
                    'scores': [r.get('score') for r in session_details.get('responses', [])],
                    'feedback_list': [r.get('feedback') for r in session_details.get('responses', [])],
                    'ideal_answers_list': [r.get('ideal_answer') for r in session_details.get('responses', [])]
                }
                
                pdf_bytes = generate_interview_report(report_data)
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Interview_Report_{date.replace(',', '').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"dl_{session_id}"
                )
                
                st.markdown("---")
                
                # Questions and answers
                for resp in session_details.get('responses', []):
                    q_num = resp.get('question_number', 0)
                    question = resp.get('question', 'N/A')
                    answer = resp.get('answer', 'No answer provided')
                    q_score = resp.get('score', 0)
                    feedback = resp.get('feedback', 'No feedback')
                    ideal = resp.get('ideal_answer', 'N/A')
                    
                    st.markdown(f"### Question {q_num} (Score: {q_score}/10)")
                    st.markdown(f"**{question}**")
                    
                    st.markdown("**Your Answer:**")
                    st.text_area("Your Answer", value=answer, height=80, disabled=True, key=f"ans_{session_id}_{q_num}", label_visibility="collapsed")
                    
                    st.success(f"**Feedback:** {feedback}")
                    
                    st.warning(f"**Ideal Answer:** {ideal}")
                    
                    st.markdown("---")
            else:
                st.info("No detailed responses found for this session.")

else:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size: 18px; font-weight: 600; color: #111827; margin-bottom: 8px;">No interview history</div>
        <div style="font-size: 14px; color: #6b7280; margin-bottom: 24px;">Complete your first interview to see it here</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Interview", type="primary", use_container_width=True):
            st.switch_page("pages/Start_Interview.py")
