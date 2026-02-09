import os
import json
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are an expert Technical Interviewer and Career Coach.

Your primary goal is to conduct a professional interview.
- Ask probing questions based on the candidate's resume and job role.
- Ask ONE question at a time.
- Do NOT provide answers to your own questions.
- If the candidate asks for help, provide a hint, then rephrase the question.
- If the user asks a non-interview question, politely redirect them back to the interview.

Stay in character as a professional interviewer. Be encouraging but rigorous.
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

    def _call_gemini(self, prompt, temperature=0.7):
        """Fallback to Gemini when Groq fails"""
        if not self.gemini_client:
            print("Gemini client not available for fallback")
            return None
            
        try:
            # Gemini doesn't use system prompts the same way, so we prepend it
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
            
            response = self.gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini Fallback Error: {e}")
            return None

    def _call_llm(self, messages, temperature=0.7, json_mode=False):
        """
        Attempts to call Groq first. If it fails (rate limit/error), falls back to Gemini.
        Returns the string response content.
        """
        # Extract user prompt from messages for Gemini fallback
        user_prompt = next((m['content'] for m in messages if m['role'] == 'user'), "")
        
        # 1. Try Groq
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=temperature,
                    response_format={"type": "json_object"} if json_mode else None
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Groq Error (falling back to Gemini): {e}")
        
        # 2. Fallback to Gemini
        return self._call_gemini(user_prompt, temperature)

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
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                
                response_text = self._call_llm(messages, temperature=0.4, json_mode=True)
                if response_text:
                    parsed = self._clean_and_parse_json(response_text)
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
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.4, json_mode=True)
            if response_text:
                return self._clean_and_parse_json(response_text)

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

    def generate_questions(self, resume_text, job_role, category, difficulty):
        prompt = f"""
        Generate 5 interview questions for a {job_role} position.
        Resume Context: {resume_text[:3000]}
        
        Focus on: {category}
        Difficulty Level: {difficulty}
        
        Return ONLY a JSON list of strings.
        Example: ["Question 1", "Question 2", ...]
        """
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.6, json_mode=True)
            if response_text:
                result = self._clean_and_parse_json(response_text)
                if result:
                    # Validate format
                    if isinstance(result, list):
                        return result
                    elif isinstance(result, dict):
                        # Attempt to find the list in the dict
                        for key, value in result.items():
                            if isinstance(value, list):
                                return value
                        # If no provided list found, fallback
                        print(f"Unexpected JSON format: {result}")
                        
        except Exception as e:
            print(f"Question Generation Error: {e}")
            
        return [
            "Tell me about yourself and your experience.",
            "What do you consider your greatest strength?",
            "Describe a challenging project you worked on.",
            "Why do you want to work in this role?",
            "Where do you see yourself in 5 years?"
        ]

    def evaluate_answer(self, question, answer, job_role):
        prompt = f"""
        You are interviewing a candidate for a {job_role} role.
        
        Question: {question}
        Candidate's Answer: {answer}
        
        Evaluate the answer.
        
        Return JSON:
        {{
            "feedback": "constructive feedback...",
            "score": <0-10>,
            "ideal_answer": "A better way to answer would be...",
            "qualified": <true/false>
        }}
        """
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.3, json_mode=True)
            if response_text:
                result = self._clean_and_parse_json(response_text)
                if result: return result
                
        except Exception as e:
            print(f"Answer Evaluation Error: {e}")
            
        return {
            "feedback": "Could not evaluate answer at this time.",
            "score": 0,
            "ideal_answer": "N/A",
            "qualified": False
        }

    def extract_name(self, text):
        prompt = "Extract the candidate's full name from this resume text. Return ONLY the name as a string. If not found, return 'Candidate'."
        
        # Try Gemini first for name extraction as it's often better at zero-shot extraction
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[prompt, text[:2000]]
                )
                return response.text.strip()
            except Exception as e:
                print(f"Gemini Name Extraction Error: {e}")

        # Fallback to Groq
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a precise data extractor."},
                        {"role": "user", "content": f"{prompt}\n\nText: {text[:1000]}"}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"Groq Name Extraction Error: {e}")

        return "Candidate"

    def chat(self, messages):
        try:
            # Ensure system prompt is at the beginning
            if messages and messages[0]['role'] != 'system':
                messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
            elif not messages:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            if self.groq_client or self.gemini_client:
                response_text = self._call_llm(messages, temperature=0.5)
                if response_text: return response_text
                
        except Exception as e:
            print(f"Chat Error: {e}")
            
        return "I apologize, but I am encountering technical difficulties. Please try again."

    def analyze_resume_for_chat(self, resume_text, job_role, difficulty):
        prompt = f"""
        Analyze this resume for a {job_role} interview ({difficulty} level).
        Resume: {resume_text[:2500]}
        
        Output a paragraph that summarizes the candidate's key skills and projects.
        End the paragraph with:
        "Please start the interview by asking a probing question about these topics."
        """
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.4)
            if response_text: return response_text
        except Exception as e:
            print(f"Chat Resume Analysis Error: {e}")
            
        return "I have reviewed your resume. Let's start the interview."

    def generate_coding_problem(self, language, topic, difficulty):
        prompt = f"""
        Generate a {difficulty} coding problem for {language} related to {topic}.
        
        Return JSON:
        {{
            "title": "Problem Title",
            "description": "Problem description with examples...",
            "starter_code": "def solution():\\n    pass" 
        }}
        """
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.7, json_mode=True)
            if response_text:
                result = self._clean_and_parse_json(response_text)
                if result: return result
        except Exception as e:
            print(f"Coding Problem Error: {e}")
            
        return {
            "title": "Error Generation",
            "description": "Could not generate problem.",
            "starter_code": ""
        }

    def review_code(self, code, problem_description, language):
        prompt = f"""
        Review this {language} code for the following problem:
        
        Problem: {problem_description}
        
        Code:
        {code}
        
        Return JSON:
        {{
            "is_correct": <true/false>,
            "feedback": "Feedback on correctness and style...",
            "bugs": ["bug 1", "bug 2"],
            "optimization_tips": ["tip 1", "tip 2"]
        }}
        """
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response_text = self._call_llm(messages, temperature=0.2, json_mode=True)
            if response_text:
                result = self._clean_and_parse_json(response_text)
                if result: return result
        except Exception as e:
            print(f"Code Review Error: {e}")
            
        return {
            "is_correct": False,
            "feedback": "Could not review code.",
            "bugs": [],
            "optimization_tips": []
        }

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
