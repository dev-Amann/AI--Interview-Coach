import os
import json
from google import genai
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

        self.gemini_client = None
        if self.gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            except Exception as e:
                print(f"Gemini Init Error: {e}")

    def generate_questions(self, resume_text, job_role, category="Technical", difficulty="Medium"):
        difficulty_guidance = {
            "Easy": "Focus on fundamental concepts and basic knowledge. Questions should be suitable for freshers or entry-level candidates.",
            "Medium": "Include intermediate-level questions that test both theory and practical application. Suitable for candidates with 1-3 years experience.",
            "Hard": "Ask advanced questions involving system design, optimization, edge cases, and deep technical knowledge. Suitable for senior positions."
        }
        
        category_guidance = {
            "Technical": f"Generate strictly technical interview questions specific to the {job_role} role. Focus on coding, tools, frameworks, and technical problem-solving.",
            "Behavioral": "Generate behavioral interview questions using the STAR method (Situation, Task, Action, Result). Focus on teamwork, leadership, conflict resolution, and past experiences.",
            "HR": "Generate HR interview questions about career goals, salary expectations, company culture fit, strengths/weaknesses, and work preferences."
        }
        
        prompt = f"""
        You are an expert interviewer conducting a {category.lower()} interview.
        
        Context:
        - Job Role: {job_role}
        - Interview Type: {category}
        - Difficulty: {difficulty}
        - Candidate Resume Snippet: {resume_text[:3000]}...

        {category_guidance.get(category, category_guidance["Technical"])}
        
        Difficulty Level: {difficulty}
        {difficulty_guidance.get(difficulty, difficulty_guidance["Medium"])}

        Task:
        Generate strictly 5 interview questions for this {category.lower()} interview.
        The questions should be relevant to both the role and the candidate's background.
        
        Output Format: Return ONLY a raw JSON list of 5 strings. Do not use Markdown blocks.
        Example: ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        """
        
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7
                )
                content = chat_completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"Groq Generation Error: {e}")
        
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"Gemini Generation Error: {e}")

        return ["Could not generate questions. Please check your API keys.", "", "", "", ""]

    def evaluate_answer(self, question, answer, job_role):
        prompt = f"""
        Act as an experienced Interviewer for a {job_role} position.
        
        Question: "{question}"
        Candidate Answer: "{answer}"

        Evaluate the answer thoroughly.
        
        Return ONLY a JSON object with these exact keys:
        - "score": A number between 0 and 10 (be fair but critical).
        - "feedback": A constructive feedback sentence explaining what was good and what can be improved (max 40 words).
        - "ideal_answer": A high-quality, comprehensive answer that demonstrates best practices and expertise (max 120 words).
        
        Scoring Guide:
        - 0-3: Poor answer, missing key concepts or incorrect
        - 4-6: Average answer, partially correct with room for improvement
        - 7-8: Good answer, mostly correct with minor improvements needed
        - 9-10: Excellent answer, comprehensive and demonstrates expertise
        
        Do not include markdown formatting. Return only valid JSON.
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
        
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"Gemini Eval Error: {e}")

        return {"score": 0, "feedback": "Error evaluating answer.", "ideal_answer": "Unable to generate."}

    def generate_skill_analysis(self, scores, questions, answers):
        prompt = f"""
        Analyze this interview performance and provide skill recommendations.
        
        Questions and Scores:
        {json.dumps([{"question": q, "score": s} for q, s in zip(questions, scores)], indent=2)}
        
        Based on the scores, identify:
        1. Top 2 strengths (areas with highest scores)
        2. Top 2 areas needing improvement (areas with lowest scores)
        3. 3 specific actionable recommendations to improve
        
        Return ONLY a JSON object:
        {{
            "strengths": ["strength 1", "strength 2"],
            "improvements": ["area 1", "area 2"],
            "recommendations": ["tip 1", "tip 2", "tip 3"]
        }}
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
                print(f"Skill Analysis Error: {e}")
        
        return {
            "strengths": ["Technical fundamentals", "Problem approach"],
            "improvements": ["Depth of explanation", "Practical examples"],
            "recommendations": [
                "Practice explaining concepts step by step",
                "Include real-world examples from your experience",
                "Review core concepts in weaker areas"
            ]
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
