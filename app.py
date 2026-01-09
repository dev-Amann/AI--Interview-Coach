import streamlit as st
import os
from services.resume_parser import extract_text_from_pdf
from services.ai_engine import AIEngine

st.set_page_config(page_title="AI Interview Coach", layout="wide")

if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'scores' not in st.session_state:
    st.session_state.scores = []
if 'feedback_list' not in st.session_state:
    st.session_state.feedback_list = []
if 'ideal_answers_list' not in st.session_state:
    st.session_state.ideal_answers_list = []
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

st.sidebar.title("AI Interview Coach 🤖")
st.sidebar.markdown("Upload your resume and select a role to start.")

uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_role = st.sidebar.selectbox("Select Job Role", [
    "Python Developer", 
    "Web Developer", 
    "Tester", 
    "AI Engineer", 
    "Data Analyst"
])

start_btn = st.sidebar.button("Start Interview")

if start_btn:
    if uploaded_file is None:
        st.sidebar.error("Please upload a resume first!")
    else:
        with st.spinner("Analyzing Resume & Generating Questions..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            st.session_state.resume_text = resume_text
            
            ai = AIEngine()
            questions = ai.generate_questions(resume_text, job_role)
            
            if questions and isinstance(questions, list) and len(questions) > 0:
                st.session_state.questions = questions
                st.session_state.current_question_index = 0
                st.session_state.answers = {}
                st.session_state.scores = []
                st.session_state.feedback_list = []
                st.session_state.ideal_answers_list = []
                st.session_state.interview_complete = False
                st.rerun()
            else:
                st.error("Failed to generate questions. Please try again.")

st.title("AI Interview Coach")

if st.session_state.questions and not st.session_state.interview_complete:
    current_idx = st.session_state.current_question_index
    total_q = len(st.session_state.questions)
    q_text = st.session_state.questions[current_idx]

    st.progress((current_idx) / total_q)
    st.markdown(f"### Question {current_idx + 1} of {total_q}")
    st.info(q_text)

    answer_input = st.text_area("Your Answer:", height=150, key=f"q_{current_idx}")

    if st.button("Submit Answer"):
        if not answer_input.strip():
            st.warning("Please write an answer.")
        else:
            with st.spinner("Evaluating..."):
                ai = AIEngine()
                eval_result = ai.evaluate_answer(q_text, answer_input, job_role)
                
                score = eval_result.get("score", 0)
                feedback = eval_result.get("feedback", "No feedback.")
                ideal_answer = eval_result.get("ideal_answer", "No ideal answer provided.")

                st.session_state.answers[current_idx] = answer_input
                st.session_state.scores.append(score)
                st.session_state.feedback_list.append(feedback)
                st.session_state.ideal_answers_list.append(ideal_answer)

                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"Score: {score}/10")
                with col2:
                    st.markdown(f"**Feedback:** {feedback}")
                
                st.info(f"**Ideal Answer:** {ideal_answer}")

                if current_idx < total_q - 1:
                    st.session_state.current_question_index += 1
                    if st.button("Next Question"):
                         st.rerun()
                else:
                    st.session_state.interview_complete = True
                    st.rerun()

if st.session_state.interview_complete:
    st.balloons()
    st.header("Interview Completed! 🎉")
    
    avg_score = sum(st.session_state.scores) / len(st.session_state.scores) if st.session_state.scores else 0
    st.metric("Average Score", f"{avg_score:.1f} / 10")

    if avg_score >= 6.5:
        st.success("✅ QUALIFIED for Actual Interview")
    else:
        st.error("❌ NOT QUALIFIED for Actual Interview")
    
    st.markdown("---")
    st.subheader("Summary & Improvements")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"#### Q{i+1}: {q}")
        st.markdown(f"**Your Answer:** {st.session_state.answers.get(i, '')}")
        st.markdown(f"**Score:** {st.session_state.scores[i]}/10")
        st.markdown(f"**Feedback:** {st.session_state.feedback_list[i]}")
        
        ideal = st.session_state.ideal_answers_list[i] if i < len(st.session_state.ideal_answers_list) else "N/A"
        st.success(f"💡 **Ideal Answer / Tip:** {ideal}")
        
        st.markdown("---")

    if st.button("Restart Interview"):
        st.session_state.clear()
        st.rerun()

elif not st.session_state.questions:
    st.info("👈 Upload your resume and click 'Start Interview' from the sidebar to begin.")
