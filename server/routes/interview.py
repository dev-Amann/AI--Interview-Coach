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
            from services.resume_parser import extract_text
            resume_text = extract_text(file)
        else:
            # Fallback to text if provided in form data
            resume_text = request.form.get('resume_text', '')
            
        if not resume_text or not job_role:
            return jsonify({"error": "Missing resume file/text or job role"}), 400
            
        ai = AIEngine()
        questions = ai.generate_questions(resume_text, job_role, category, difficulty)
        user_name = ai.extract_name(resume_text)
        
        return jsonify({
            "questions": questions,
            "user_name": user_name
        })
        
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
        print("DEBUG: chat_resume_upload called")
        if 'resume' not in request.files:
            print("DEBUG: No 'resume' key in request.files")
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['resume']
        print(f"DEBUG: File received: {file.filename}")
        
        if file.filename == '':
            print("DEBUG: Empty filename")
            return jsonify({"error": "No selected file"}), 400
            
        from services.resume_parser import extract_text
        print("DEBUG: Calling extract_text...")
        resume_text = extract_text(file)
        print(f"DEBUG: extract_text returned {len(resume_text)} characters")
        
        if resume_text.startswith("Error:"):
            print(f"DEBUG: extract_text returned error: {resume_text}")
            return jsonify({"error": resume_text}), 400
            
        ai = AIEngine()
        user_name = ai.extract_name(resume_text)
        
        job_role = request.form.get('job_role', 'Any Role')
        difficulty = request.form.get('difficulty', 'Medium')
        
        print(f"DEBUG: Extracted user name: {user_name}, Role: {job_role}")

        # Prepare context prompt for the AI
        context_message = f"""
        [SYSTEM: The candidate has uploaded a resume for a Mock Interview.
        Candidate Name: {user_name}
        Target Job Role: {job_role}
        Difficulty Level: {difficulty}
        Resume Content:
        {resume_text[:4000]} 
        
        End of Resume]
        
        INSTRUCTIONS:
        1. Greet the candidate by name (e.g., "Hello {user_name}!").
        2. Acknowledge their application for the {job_role} position.
        3. Do NOT ask if they are fresher/experienced if it's clear from resume, just start the interview.
        4. Ask Technical or Behavioral questions relevant to {job_role} at {difficulty} level.
        5. Provide short, constructive feedback after every answer.
        6. Keep the conversation friendly and professional. 
        7. Limit your response to 150 words.
        8. Always refer to the candidate as "{user_name}" or "Candidate".
        9. Do NOT reveal that you are an AI model.
        END OF INSTRUCTIONS.
        """
        
        print("DEBUG: Returning success context")
        return jsonify({"context": context_message, "preview": f"Resume uploaded successfully. Hello {user_name}!"})
        
    except Exception as e:
        import traceback
        print(f"CRITICAL ERROR in chat_resume_upload: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/resume/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['resume']
        from services.resume_parser import extract_text
        resume_text = extract_text(file)
        
        if resume_text.startswith("Error"):
            return jsonify({"error": resume_text}), 400
            
        ai = AIEngine()
        analysis = ai.analyze_resume_deep(resume_text)
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Analyze Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/coding/problem', methods=['POST'])
def generate_coding_problem():
    try:
        data = request.json
        language = data.get('language', 'Python')
        topic = data.get('topic', 'Arrays')
        difficulty = data.get('difficulty', 'Easy')
        
        ai = AIEngine()
        problem = ai.generate_coding_problem(language, topic, difficulty)
        return jsonify(problem)
    except Exception as e:
        print(f"Gen Problem Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/coding/review', methods=['POST'])
def review_coding_submission():
    try:
        data = request.json
        code = data.get('code')
        problem_description = data.get('problem_description')
        language = data.get('language')
        
        ai = AIEngine()
        review = ai.review_code(code, problem_description, language)
        return jsonify(review)
    except Exception as e:
        print(f"Review Error: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/analyze', methods=['POST'])
def analyze_interview():
    """
    Analyze the complete interview session and provide detailed feedback.
    Expects: conversation_history, behavioral_alerts, job_role, difficulty
    Returns: detailed analysis with scores and recommendations
    """
    try:
        data = request.json
        conversation = data.get('conversation', [])
        behavioral_alerts = data.get('behavioral_alerts', [])
        job_role = data.get('job_role', 'Software Developer')
        difficulty = data.get('difficulty', 'Medium')
        user_name = data.get('user_name', 'Candidate')
        
        # Build the analysis prompt
        conversation_text = ""
        for msg in conversation:
            role = "Interviewer" if msg.get('role') == 'assistant' else "Candidate"
            conversation_text += f"{role}: {msg.get('content', '')}\n\n"
        
        alerts_text = ""
        if behavioral_alerts:
            alerts_text = "Behavioral Observations:\n"
            for alert in behavioral_alerts:
                alerts_text += f"- {alert.get('message', alert)}\n"
        
        analysis_prompt = f"""You are an expert interview coach analyzing a mock interview session.

**Interview Details:**
- Job Role: {job_role}
- Difficulty Level: {difficulty}
- Candidate Name: {user_name}

**Interview Transcript:**
{conversation_text}

**Behavioral Analysis (from AI monitoring):**
{alerts_text if alerts_text else "No significant behavioral alerts detected."}

Please provide a comprehensive interview analysis in the following JSON format:
{{
    "overall_score": <number 1-100>,
    "communication_score": <number 1-100>,
    "technical_score": <number 1-100>,
    "confidence_score": <number 1-100>,
    "body_language_score": <number 1-100>,
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "areas_for_improvement": ["<area 1>", "<area 2>", ...],
    "detailed_feedback": "<2-3 paragraphs of personalized feedback>",
    "recommendations": ["<actionable recommendation 1>", "<actionable recommendation 2>", ...],
    "verdict": "<READY FOR INTERVIEWS | NEEDS PRACTICE | EXCELLENT PERFORMANCE>"
}}

Be encouraging but honest. Focus on actionable improvements.
"""
        
        ai = AIEngine()
        response = ai.chat([{"role": "user", "content": analysis_prompt}])
        
        # Try to parse JSON from response
        import json
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            analysis = json.loads(json_match.group())
            return jsonify({"success": True, "analysis": analysis})
        else:
            # Return raw text if JSON parsing fails
            return jsonify({
                "success": True, 
                "analysis": {
                    "overall_score": 75,
                    "detailed_feedback": response,
                    "verdict": "NEEDS REVIEW"
                }
            })
            
    except Exception as e:
        print(f"Analysis Error: {e}")
        return jsonify({"error": str(e)}), 500
