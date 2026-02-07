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
# RESUME ANALYSIS 
# ==========================================================
@interview_bp.route('/resume/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['resume']

        ocr_json = extract_text(file)

        full_text = extract_text_from_json(ocr_json)

    
        chunks = chunk_text(full_text)

        print("DEBUG: Resume Analyze - Total words:", len(full_text.split()))
        print("DEBUG: Resume Analyze - Number of chunks:", len(chunks))

        ai = AIEngine()

        analysis = ai.analyze_resume_from_chunks(chunks)

        return jsonify(analysis)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
