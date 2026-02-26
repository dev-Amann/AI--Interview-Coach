from flask import Blueprint, request, jsonify, send_file
import uuid
import io

from services.resume_parser import extract_text
from services.chunker import extract_text_from_json, chunk_text
from services.temp_store import save_ocr, get_ocr
from services.ai_engine import AIEngine
from services.database import Database
from services.pdf_generator import generate_interview_report

interview_bp = Blueprint('interview', __name__)


# ==========================================================
# START INTERVIEW (UPDATED WITH TEMP STORE + CHUNKING)
# ==========================================================
@interview_bp.route('/start', methods=['POST'])
def start_interview():
    try:
        session_id = str(uuid.uuid4())

        job_role = request.form.get('job_role')
        category = request.form.get('category', 'Technical')
        difficulty = request.form.get('difficulty', 'Medium')

        if not job_role:
            return jsonify({"error": "Job role is required"}), 400

        if 'resume_file' not in request.files:
            return jsonify({"error": "Resume file is required"}), 400

        file = request.files['resume_file']

        # ✅ STEP 1 — OCR → JSON
        ocr_json = extract_text(file)

        # ✅ STEP 2 — Save to Temporary Store
        save_ocr(session_id, ocr_json)

        # ✅ STEP 3 — Extract + Chunk
        full_text = extract_text_from_json(ocr_json)
        chunks = chunk_text(full_text)
        print("DEBUG: Total words:", len(full_text.split()))
        print("DEBUG: Number of chunks:", len(chunks))
        print("DEBUG: First chunk preview:", chunks[0][:200])

        ai = AIEngine()

        # ✅ STEP 4 — Deep Resume Analysis (Chunk-Based)
        resume_analysis = ai.analyze_resume_from_chunks(chunks)

        # ✅ STEP 5 — Generate Interview Questions (using text)
        questions = ai.generate_questions(full_text, job_role, category, difficulty)

        user_name = ai.extract_name(full_text)

        return jsonify({
            "session_id": session_id,
            "questions": questions,
            "user_name": user_name,
            "resume_analysis": resume_analysis
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# SUBMIT ANSWER 
# ==========================================================
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


# ==========================================================
# SAVE SESSION 
# ==========================================================
@interview_bp.route('/save', methods=['POST'])
def save_session():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_email = data.get('email')
        user_name = data.get('name')

        db = Database()
        db.save_user(user_id, user_email, user_name)

        session_id = db.save_session(
            user_id=user_id,
            job_role=data.get('job_role'),
            category=data.get('category'),
            difficulty=data.get('difficulty'),
            avg_score=data.get('avg_score'),
            qualified=data.get('qualified'),
            questions=data.get('questions'),
            answers=data.get('answers'),
            scores=data.get('scores'),
            feedback_list=data.get('feedback_list'),
            ideal_answers_list=data.get('ideal_answers_list')
        )

        return jsonify({"session_id": session_id, "message": "Session saved successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# REPORT GENERATION 
# ==========================================================
@interview_bp.route('/report', methods=['POST'])
def generate_report():
    try:
        data = request.json
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

        responses = session.get('responses', [])

        report_data = {
            "user_name": "Reviewer",
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
        return jsonify({"error": str(e)}), 500
    
# ==========================================================
# CHAT INTERVIEW (RESTORED)
# ==========================================================
@interview_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        ai = AIEngine()
        response = ai.chat(messages)
        
        return jsonify({"response": response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route('/chat/resume', methods=['POST'])
def chat_resume_upload():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['resume']
        job_role = request.form.get('job_role', 'Software Developer')
        difficulty = request.form.get('difficulty', 'Medium')
        
        # OCR
        ocr_json = extract_text(file)
        full_text = extract_text_from_json(ocr_json)
        
        ai = AIEngine()
        context = ai.analyze_resume_for_chat(full_text, job_role, difficulty)
        
        return jsonify({"context": context})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route('/analyze', methods=['POST'])
def analyze_interview_session():
    try:
        data = request.json
        conversation = data.get('conversation', [])
        behavioral_alerts = data.get('behavioral_alerts', [])
        job_role = data.get('job_role', 'Software Developer')
        difficulty = data.get('difficulty', 'Medium')
        user_name = data.get('user_name', 'Candidate')
        
        ai = AIEngine()
        analysis = ai.analyze_interview(
            conversation, 
            behavioral_alerts, 
            job_role, 
            difficulty, 
            user_name
        )
        
        # Check if we got an error dictionary back
        if not analysis or analysis.get("verdict") == "ERROR":
            return jsonify({
                "success": False, 
                "error": analysis.get("detailed_feedback", "Failed to analyze interview.")
            }), 500
            
        return jsonify({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        print(f"Error in /analyze: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
# ==========================================================
# RESUME ANALYSIS 
# ==========================================================
@interview_bp.route('/resume/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['resume']

        # STEP 1 — OCR → JSON
        ocr_json = extract_text(file)

        # STEP 2 — Extract text from JSON
        full_text = extract_text_from_json(ocr_json)

        # STEP 3 — Chunk text
        chunks = chunk_text(full_text)

        print("DEBUG: Resume Analyze - Total words:", len(full_text.split()))
        print("DEBUG: Resume Analyze - Number of chunks:", len(chunks))
        chunk_previews = []
        for i, chunk in enumerate(chunks):
            preview = chunk[:300]  # first 300 characters
            print(f"\n--- Chunk {i+1} Preview ---")
            print(preview)
            print("---------------------------")

            chunk_previews.append({
                "chunk_number": i + 1,
                "word_count": len(chunk.split()),
                "preview": preview
            })


        ai = AIEngine()

        # STEP 4 — Analyze using chunk-based method
        analysis = ai.analyze_resume_from_chunks(chunks)

       # return jsonify(analysis)
        
        return jsonify({
           **analysis,
           "chunk_count": len(chunks),
           "chunk_previews": chunk_previews
})


    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================================================
# MOCK CODING INTERVIEW
# ==========================================================
@interview_bp.route('/coding/problem', methods=['POST'])
def generate_problem():
    try:
        data = request.json
        language = data.get('language', 'Python')
        topic = data.get('topic', 'Arrays')
        difficulty = data.get('difficulty', 'Easy')
        
        ai = AIEngine()
        problem = ai.generate_coding_problem(language, topic, difficulty)
        
        return jsonify(problem)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route('/coding/review', methods=['POST'])
def review_code():
    try:
        data = request.json
        code = data.get('code')
        problem_description = data.get('problem_description')
        language = data.get('language')
        
        if not all([code, problem_description, language]):
            return jsonify({"error": "Missing required fields"}), 400
            
        ai = AIEngine()
        review = ai.review_code(code, problem_description, language)
        
        return jsonify(review)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
