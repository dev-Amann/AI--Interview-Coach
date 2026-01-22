import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def test_health():
    try:
        r = requests.get("http://127.0.0.1:5000/")
        print(f"Health Check: {r.status_code} - {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def test_interview_flow():
    print("\nTesting Interview Flow...")
    
    # 1. Start Interview (Mock)
    payload = {
        "resume_text": "Experienced Python Developer with 5 years in Flask and AWS.",
        "job_role": "Python Developer",
        "category": "Technical",
        "difficulty": "Medium"
    }
    
    try:
        # Note: This might fail if API keys are not valid/set, but we check for response structure
        r = requests.post(f"{BASE_URL}/interview/start", json=payload)
        
        if r.status_code == 200:
            print("✅ Start Interview: Success")
            questions = r.json().get("questions", [])
            print(f"   Generated {len(questions)} questions.")
            
            if questions:
                # 2. Answer Question
                q1 = questions[0]
                ans_payload = {
                    "question": q1,
                    "answer": "I use Flask blueprints for modularity and SQLAlchemy for ORM.",
                    "job_role": "Python Developer"
                }
                r_ans = requests.post(f"{BASE_URL}/interview/answer", json=ans_payload)
                if r_ans.status_code == 200:
                    print("✅ Answer Question: Success")
                    print(f"   Score: {r_ans.json().get('score')}/10")
                else:
                    print(f"❌ Answer Question Failed: {r_ans.status_code} - {r_ans.text}")
        else:
             print(f"❌ Start Interview Failed: {r.status_code} - {r.text}")
             if "API key" in r.text:
                 print("   (This is expected if API keys are missing in .env)")

    except Exception as e:
        print(f"Interview Flow Error: {e}")

def test_user_routes():
    print("\nTesting User Routes...")
    # Mock user ID (need valid ID if database is empty, but endpoint handles empty)
    user_id = "test_user_123" 
    
    try:
        r = requests.get(f"{BASE_URL}/user/stats/{user_id}")
        if r.status_code == 200:
             print("✅ Get Stats: Success")
        else:
             print(f"❌ Get Stats Failed: {r.status_code}")
             
    except Exception as e:
        print(f"User Routes Error: {e}")

if __name__ == "__main__":
    if test_health():
        test_interview_flow()
        test_user_routes()
    else:
        print("Skipping tests due to health check failure.")
