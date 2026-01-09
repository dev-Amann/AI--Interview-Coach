import os
import json
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Groq Init Error: {e}")

        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Gemini Init Error: {e}")

    def generate_questions(self, resume_text, job_role):
        prompt = f"""
        You are an expert technical interviewer.
        Context:
        - Job Role: {job_role}
        - Candidate Resume Snippet: {resume_text[:3000]}...

        Task:
        Generate strictly 5 technical interview questions relevant to the role and resume.
        Difficulty: Beginner to Advance.
        Output Format: return ONLY a raw JSON list of strings. Do not use Markdown blocks.
        Example: ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        """
        
        print(f"DEBUG: Groq Key Present: {bool(self.groq_api_key)}")
        print(f"DEBUG: Gemini Key Present: {bool(self.gemini_api_key)}")

        if self.groq_client:
            print("DEBUG: Attempting Groq...")
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7
                )
                print("DEBUG: Groq Success")
                content = chat_completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"ERROR: Groq Generation Error: {e}")
        
        if self.gemini_api_key:
            print("DEBUG: Attempting Gemini...")
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                print("DEBUG: Gemini Success")
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"ERROR: Gemini Generation Error: {e}")

        return ["Could not generate questions. Please check your API keys.", "", "", "", ""]

    def evaluate_answer(self, question, answer, job_role):
        prompt = f"""
        Act as an Interviewer for a {job_role} position.
        Question: "{question}"
        Candidate Answer: "{answer}"

        Evaluate the answer. 
        Return ONLY a JSON object with these exact keys:
        - "score": A number between 0 and 10.
        - "feedback": A short constructive feedback sentence (max 30 words).
        - "ideal_answer": A specific, high-quality answer to the question (max 100 words) that demonstrates best practices.
        
        Do not include markdown formatting.
        """

        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5
                )
                content = chat_completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"Groq Eval Error: {e}")
        
        if self.gemini_api_key:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"Gemini Eval Error: {e}")

        return {"score": 0, "feedback": "Error evaluating answer."}

    def _clean_and_parse_json(self, text):
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines)
            return json.loads(cleaned)
        except Exception as e:
            print(f"JSON Parsing Error: {e} | Text: {text}")
            return None
