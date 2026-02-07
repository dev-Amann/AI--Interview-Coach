import os
import json
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are an AI Interview Coach.

You must answer ONLY interview-related questions such as:
- Technical interview questions 
- HR and behavioral interview questions
- Resume or project explanation for interviews
- Mock interview practice
- Career guidance related to interviews

If the user asks any question that is NOT related to interview preparation,
do NOT answer it.

Instead, respond only with:
"I am designed to help only with interview-related questions. Please ask an interview-related question."

Follow this rule strictly.
"""

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

        self.gemini_client = None
        if self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Gemini Init Error: {e}")

    # ==========================================================
    # NEW METHOD — CHUNK-BASED RESUME ANALYSIS (SAFE ADDITION)
    # ==========================================================
    def analyze_resume_from_chunks(self, chunks):
        """
        Performs deep resume analysis using chunked resume text.
        """

        if not chunks:
            return {
                "ats_score": 0,
                "summary": "No resume content found.",
                "strengths": [],
                "weaknesses": [],
                "missing_skills": [],
                "suggested_roles": []
            }

        partial_analyses = []

        for chunk in chunks:
            prompt = f"""
            Analyze this portion of a resume as an expert Technical Recruiter.
            
            Resume Section:
            {chunk}

            Return JSON:
            {{
                "strengths": [],
                "weaknesses": [],
                "skills_detected": []
            }}

            Return ONLY valid JSON.
            """

            try:
                if self.groq_client:
                    messages = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]

                    response = self.groq_client.chat.completions.create(
                        messages=messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.4
                    )

                    parsed = self._clean_and_parse_json(
                        response.choices[0].message.content
                    )

                    if parsed:
                        partial_analyses.append(parsed)

            except Exception as e:
                print(f"Chunk Analysis Error: {e}")

        combined_strengths = []
        combined_weaknesses = []
        combined_skills = []

        for item in partial_analyses:
            combined_strengths.extend(item.get("strengths", []))
            combined_weaknesses.extend(item.get("weaknesses", []))
            combined_skills.extend(item.get("skills_detected", []))

        combined_strengths = list(set(combined_strengths))
        combined_weaknesses = list(set(combined_weaknesses))
        combined_skills = list(set(combined_skills))

        final_prompt = f"""
        Based on these extracted resume insights:

        Strengths: {combined_strengths}
        Weaknesses: {combined_weaknesses}
        Skills: {combined_skills}

        Provide final JSON:

        {{
            "ats_score": <0-100>,
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "missing_skills": [],
            "suggested_roles": []
        }}

        Return ONLY valid JSON.
        """

        try:
            if self.groq_client:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": final_prompt}
                ]

                response = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.4
                )

                return self._clean_and_parse_json(
                    response.choices[0].message.content
                )

        except Exception as e:
            print(f"Final Resume Merge Error: {e}")

        return {
            "ats_score": 0,
            "summary": "Could not complete resume analysis.",
            "strengths": combined_strengths,
            "weaknesses": combined_weaknesses,
            "missing_skills": [],
            "suggested_roles": []
        }

    # ==========================================================
    # EXISTING METHODS BELOW (UNCHANGED LOGIC)
    # ==========================================================

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
