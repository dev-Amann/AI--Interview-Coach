import streamlit as st
from services.ai_engine import AIEngine
from services.resume_parser import extract_text_from_pdf
from services.database import Database
from services.auth import get_current_user
from services.pdf_generator import generate_interview_report

def initialize_session_state():
    """Initialize all session state variables needed for the interview"""
    defaults = {
        'questions': [],
        'current_question_index': 0,
        'answers': {},
        'scores': [],
        'feedback_list': [],
        'ideal_answers_list': [],
        'interview_complete': False,
        'show_feedback': False,
        'current_feedback': None,
        'session_saved': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_interview_state():
    """Reset the interview state for a new session"""
    st.session_state.questions = []
    st.session_state.current_question_index = 0
    st.session_state.answers = {}
    st.session_state.scores = []
    st.session_state.feedback_list = []
    st.session_state.ideal_answers_list = []
    st.session_state.interview_complete = False
    st.session_state.show_feedback = False
    st.session_state.current_feedback = None
    st.session_state.session_saved = False

def render_setup_phase():
    """Render the initial setup phase (Resume Upload & Configuration)"""
    st.markdown("""
    <div class="config-card">
        <h3 style="font-size: 16px; font-weight: 600; color: #111827; margin: 0;">Interview Setup</h3>
        <p style="font-size: 14px; color: #6b7280; margin-top: 4px;">Configure your practice session</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        job_role = st.selectbox("Target Role", [
            "Python Developer", 
            "Data Scientist", 
            "Web Developer", 
            "DevOps Engineer",
            "Full Stack Developer",
            "AI Engineer"
        ])
    
    with col2:
        category = st.selectbox("Interview Type", ["Technical", "Behavioral", "HR"])
        difficulty = st.select_slider("Difficulty Level", options=["Easy", "Medium", "Hard"], value="Medium")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Generate Questions", type="primary", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload a resume first")
            else:
                with st.spinner("Analyzing resume and generating questions..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    st.success("Resume uploaded successfully!")
                    st.session_state.resume_text = resume_text
                    st.session_state.job_role = job_role
                    st.session_state.interview_category = category
                    st.session_state.difficulty_level = difficulty
                    
                    ai = AIEngine()
                    questions = ai.generate_questions(resume_text, job_role, category, difficulty)
                    
                    if questions:
                        st.session_state.questions = questions
                        st.rerun()

def render_interview_phase():
    """Render the active interview phase (Questions & Feedback)"""
    current_idx = st.session_state.current_question_index
    total_q = len(st.session_state.questions)
    q_text = st.session_state.questions[current_idx]
    
    # Progress
    st.progress((current_idx + 1) / total_q)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Question
    st.markdown(f"""
    <div class="question-box">
        <div class="question-number">Question {current_idx + 1} of {total_q}</div>
        <div class="question-text">{q_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show feedback if available
    if st.session_state.show_feedback and st.session_state.current_feedback:
        _render_feedback_view(current_idx, total_q)
    else:
        _render_answer_input(current_idx, q_text)

def _render_feedback_view(current_idx, total_q):
    """Render the immediate feedback after answering"""
    fb = st.session_state.current_feedback
    
    st.markdown(f"""
    <div class="score-display">
        <span class="score-value">Score: {fb['score']}/10</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="feedback-box">
        <div class="feedback-title">Feedback</div>
        <div class="feedback-text">{fb['feedback']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="ideal-box">
        <div class="ideal-title">Ideal Answer</div>
        <div class="ideal-text">{fb['ideal_answer']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if current_idx < total_q - 1:
            if st.button("Next Question", type="primary", use_container_width=True):
                st.session_state.current_question_index += 1
                st.session_state.show_feedback = False
                st.session_state.current_feedback = None
                st.rerun()
        else:
            if st.button("View Results", type="primary", use_container_width=True):
                st.session_state.interview_complete = True
                st.session_state.show_feedback = False
                st.session_state.current_feedback = None
                st.rerun()

def _render_answer_input(current_idx, q_text):
    """Render the text area for user input"""
    answer = st.text_area("Your Answer", height=180, placeholder="Type your answer here...")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Answer", type="primary", use_container_width=True):
            if not answer:
                st.warning("Please enter an answer")
            else:
                with st.spinner("Evaluating your answer..."):
                    ai = AIEngine()
                    result = ai.evaluate_answer(q_text, answer, st.session_state.job_role)
                    
                    st.session_state.answers[current_idx] = answer
                    st.session_state.scores.append(result['score'])
                    st.session_state.feedback_list.append(result['feedback'])
                    st.session_state.ideal_answers_list.append(result['ideal_answer'])
                    
                    # Show feedback before moving to next question
                    st.session_state.show_feedback = True
                    st.session_state.current_feedback = result
                    st.rerun()

def render_results_phase():
    """Render the final results summary"""
    avg_score = sum(st.session_state.scores) / len(st.session_state.scores) if st.session_state.scores else 0
    status = "Qualified" if avg_score >= 6.5 else "Needs Improvement"
    status_color = "#047857" if avg_score >= 6.5 else "#d97706"
    
    # Save to database (only once)
    if not st.session_state.get('session_saved', False):
        user = get_current_user()
        if user:
            db = Database()
            db.save_user(user.get('id'), user.get('email', ''), user.get('name', ''))
            
            db.save_session(
                user_id=user.get('id'),
                job_role=st.session_state.get('job_role', 'Unknown'),
                category=st.session_state.get('interview_category', 'Technical'),
                difficulty=st.session_state.get('difficulty_level', 'Medium'),
                avg_score=avg_score,
                qualified=(avg_score >= 6.5),
                questions=st.session_state.questions,
                answers=st.session_state.answers,
                scores=st.session_state.scores,
                feedback_list=st.session_state.feedback_list,
                ideal_answers_list=st.session_state.ideal_answers_list
            )
            st.session_state.session_saved = True
    
    st.markdown(f"""
    <div class="result-card">
        <h2 style="font-size: 24px; font-weight: 600; color: #111827; margin-bottom: 16px;">Interview Complete</h2>
        <div style="font-size: 48px; font-weight: 700; color: #111827; margin-bottom: 8px;">{avg_score:.1f}/10</div>
        <div style="font-size: 14px; color: {status_color}; font-weight: 600; margin-bottom: 24px;">{status}</div>
    </div>
    """, unsafe_allow_html=True)
    
    _render_pdf_download(avg_score)
    _render_question_summary()
    _render_action_buttons()

def _render_pdf_download(avg_score):
    """Render PDF download button"""
    user = get_current_user()
    report_data = {
        'job_role': st.session_state.get('job_role', 'Unknown'),
        'user_name': user.get('name', 'User') if user else 'User',
        'category': st.session_state.get('interview_category', 'Technical'),
        'difficulty': st.session_state.get('difficulty_level', 'Medium'),
        'avg_score': avg_score,
        'qualified': (avg_score >= 6.5),
        'questions': st.session_state.questions,
        'answers': st.session_state.answers,
        'scores': st.session_state.scores,
        'feedback_list': st.session_state.feedback_list,
        'ideal_answers_list': st.session_state.ideal_answers_list
    }
    
    pdf_bytes = generate_interview_report(report_data)
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
    with col_d2:
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name="Interview_Report.pdf",
            mime="application/pdf",
            key="dl_report_final",
            use_container_width=True
        )

def _render_question_summary():
    """Render the detailed question summary loops"""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Question Summary")
    
    for i, q in enumerate(st.session_state.questions):
        with st.expander(f"Question {i+1}: {q}"):
            # Full Question
            st.markdown(f"**{q}**")
            st.markdown("<br>", unsafe_allow_html=True)
            # Your Answer
            st.markdown(f"""
            <div class="answer-box">
                <div class="box-label">Your Answer</div>
                <div class="box-text">{st.session_state.answers.get(i, 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Score
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span class="box-label">Score:</span> 
                <span style="font-weight: 600; color: #111827;">{st.session_state.scores[i]}/10</span>
            </div>
            """, unsafe_allow_html=True)

            # Feedback
            st.markdown(f"""
            <div class="feedback-box">
                <div class="feedback-title">Feedback</div>
                <div class="feedback-text">{st.session_state.feedback_list[i]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Ideal Answer
            st.markdown(f"""
            <div class="ideal-box">
                <div class="ideal-title">Ideal Answer</div>
                <div class="ideal-text">{st.session_state.ideal_answers_list[i]}</div>
            </div>
            """, unsafe_allow_html=True)

def _render_action_buttons():
    """Render final action buttons (Dashboard / New Interview)"""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("View Dashboard", use_container_width=True):
            st.switch_page("pages/Dashboard.py")
    
    with col3:
        if st.button("New Interview", type="primary", use_container_width=True):
            reset_interview_state()
            st.rerun()
