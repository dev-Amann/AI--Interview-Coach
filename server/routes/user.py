from flask import Blueprint, request, jsonify
from services.database import Database

user_bp = Blueprint('user', __name__)

@user_bp.route('/stats/<user_id>', methods=['GET'])
def get_stats(user_id):
    try:
        db = Database()
        # Reusing the logic from legacy `get_user_stats` but interacting with class directly
        # We need to check if we can reuse the `get_user_analytics` method from Database class
        analytics = db.get_user_analytics(user_id)
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        limit = request.args.get('limit', 20, type=int)
        db = Database()
        sessions = db.get_user_sessions(user_id, limit=limit)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    try:
        db = Database()
        session = db.get_session_details(session_id)
        if session:
            return jsonify(session)
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
