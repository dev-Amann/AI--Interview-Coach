import os
import sys

# Add the current directory (server/) to sys.path to resolve 'services' imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from routes.interview import interview_bp
from routes.user import user_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.register_blueprint(interview_bp, url_prefix='/api/interview')
app.register_blueprint(user_bp, url_prefix='/api/user')

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "service": "AI Interview Coach API"})

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    print("!!! GLOBAL ERROR CAUGHT !!!")
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
