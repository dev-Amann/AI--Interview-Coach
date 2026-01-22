from flask import Blueprint, request, jsonify, send_file
from services.ai_engine import AIEngine
from services.database import Database
from services.pdf_generator import generate_interview_report
import io

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/start', methods=['POST'])
def start_interview():
    try:
        # Handle Multipart Form Data
        resume_text = ""
        job_role = request.form.get('job_role')
        category = request.form.get('category', 'Technical')
        difficulty = request.form.get('difficulty', 'Medium')
        
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            from services.resume_parser import extract_text_from_pdf
            resume_text = extract_text_from_pdf(file)
        else:
            # Fallback to text if provided in form data
            resume_text = request.form.get('resume_text', '')
            
        if not resume_text or not job_role:
            return jsonify({"error": "Missing resume file/text or job role"}), 400
            
        ai = AIEngine()
        questions = ai.generate_questions(resume_text, job_role, category, difficulty)
        
        # In a real app, we might create a session ID here, but for now we follow the stateless flow 
        # where frontend manages the active session state until save.
        return jsonify({"questions": questions})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/answer', methods=['POST'])
def submit_answer():
    try:
        data = request.json
        question = data.get('question')
        answer = data.get('answer')
        job_role = data.get('job_role')
        
        if not all([question, answer, job_role]):
            return jsonify({"error": "Missing required fields"}), 400
            
        ai = AIEngine()
        result = ai.evaluate_answer(question, answer, job_role)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/save', methods=['POST'])
def save_session():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_email = data.get('email')
        user_name = data.get('name')
        
        db = Database()
        # Ensure user exists
        db.save_user(user_id, user_email, user_name)
        
        session_id = db.save_session(
            user_id=user_id,
            job_role=data.get('job_role'),
            category=data.get('category'),
            difficulty=data.get('difficulty'),
            avg_score=data.get('avg_score'),
            qualified=data.get('qualified'),
            questions=data.get('questions'),
            answers=data.get('answers'), # Dictionary expected by DB service? Need to check logic
            scores=data.get('scores'),
            feedback_list=data.get('feedback_list'),
            ideal_answers_list=data.get('ideal_answers_list')
        )
        
        return jsonify({"session_id": session_id, "message": "Session saved successfully"})
        
    except Exception as e:
        print(f"Save Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        # Expecting the full report data structure
        pdf_bytes = generate_interview_report(data)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='interview_report.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/report/<session_id>', methods=['GET'])
def download_report(session_id):
    try:
        db = Database()
        session = db.get_session_details(session_id)
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
            
        # Format data for report generator (it expects lists)
        responses = session.get('responses', [])
        
        # Structure data as expected by generate_interview_report
        report_data = {
            "user_name": "Reviewer", # We might need to fetch user name if critical, or leaving generic
            "job_role": session.get('job_role'),
            "category": session.get('category'),
            "difficulty": session.get('difficulty'),
            "avg_score": float(session.get('avg_score', 0)),
            "qualified": bool(session.get('qualified')),
            "questions": [r['question'] for r in responses],
            "answers": {i: r['answer'] for i, r in enumerate(responses)},
            "scores": [r['score'] for r in responses],
            "feedback_list": [r['feedback'] for r in responses],
            "ideal_answers_list": [r['ideal_answer'] for r in responses]
        }
        
        pdf_bytes = generate_interview_report(report_data)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'interview_report_{session_id}.pdf'
        )
    except Exception as e:
        print(f"Report Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/chat', methods=['POST'])
def chat_interview():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
            
        ai = AIEngine()
        response_text = ai.chat(messages)
        
        return jsonify({"response": response_text})
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/chat/resume', methods=['POST'])
def chat_resume_upload():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['resume']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        from services.resume_parser import extract_text_from_pdf
        resume_text = extract_text_from_pdf(file)
        
        # Prepare context prompt for the AI
        context_message = f"""
        [SYSTEM: The candidate has uploaded a resume. Resume Content:
        {resume_text[:4000]} 
        
        End of Resume]
        
        INSTRUCTIONS:
        1. Acknowledge the resume.
        2. Ask the candidate if they are a Fresher or Experienced.
        3. Ask how many questions they would like to practice.
        4. Do NOT start the interview yet. Wait for their preferences.
        5. If the candidate is a Fresher, ask for their job role.
        6. If the candidate is Experienced, ask for their job role and experience.
        7. After every answer given by candidate, make sure to give him feedback
        8. Ask question one by one 
        """
        
        return jsonify({"context": context_message, "preview": "Resume uploaded successfully."})
        
    except Exception as e:
        print(f"Resume Upload Error: {e}")
        return jsonify({"error": str(e)}), 500
