import os
import json
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ******************************************************
# [Condition in Prompt] - SYSTEM PROMPT DEFINITION
# ******************************************************
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
# ******************************************************

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
                # Initialize Gemini client
                # This client is also used for Image OCR (Resume Parsing) in resume_parser.py
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
        
        # Original Task Prompt
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
                # ******************************************************
                # [Condition in Prompt] - Adding System Message
                # ******************************************************
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7        #temperature for question generation
                )
                content = chat_completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"Groq Generation Error: {e}")
        
        if self.gemini_client:
            try:
                # Prepend System Prompt for Gemini
                full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=full_prompt
                )
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"Gemini Generation Error: {e}")

        return ["Could not generate questions. Please check your API keys.", "", "", "", ""]

    def evaluate_answer(self, question, answer, job_role):
        # Original Task Prompt
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
                # ******************************************************
                # [Condition in Prompt] - Adding System Message
                # ******************************************************
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.5   #temperture for answer evalution
                )
                content = chat_completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"Groq Eval Error: {e}")
        
        if self.gemini_client:
            try:
                # Prepend System Prompt for Gemini
                full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=full_prompt
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
                # ******************************************************
                # [Condition in Prompt] - Adding System Message
                # ******************************************************
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.5 #temperture for skill analysis
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

    def generate_coding_problem(self, language, topic, difficulty):
        prompt = f"""
        Generate a coding problem for a technical interview.
        Language: {language}
        Topic: {topic}
        Difficulty: {difficulty}
        
        Return the response in strictly valid JSON format with the following keys:
        - title: The title of the problem.
        - description: A clear description of the problem, including input/output examples.
        - starter_code: The initial code boilerplate for the user to start with.
        
        IMPORTANT RULES FOR STARTER_CODE:
        - It must ONLY contain the function definition and maybe a 'pass' statement or return 0.
        - DO NOT include the solution logic.
        - DO NOT include the answer.
        - It should look like this:
          def solution(arr):
              # Write your code here
              pass
        
        Do not include any markdown formatting like ```json ... ```. Just the raw JSON string.
        """
        
        response_text = ""
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7
                )
                response_text = chat_completion.choices[0].message.content
            except Exception as e:
                print(f"Groq Gen Problem Error: {e}")
                
        if not response_text and self.gemini_client:
             try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                response_text = response.text
             except Exception as e:
                print(f"Gemini Gen Problem Error: {e}")

        try:
            # Clean up potential markdown formatting if the model disregards instructions
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            return {
                "title": "Error Generating Problem",
                "description": "Could not generate a valid problem. Please try again.",
                "starter_code": "# Error generating code"
            }

    def review_code(self, code, problem_description, language):
        prompt = f"""
        Review the following code solution for a technical interview problem.
        
        Problem Description:
        {problem_description}
        
        Language: {language}
        
        User's Code:
        {code}
        
        Provide a detailed review in strictly valid JSON format with the following keys:
        - is_correct: boolean, true if the code solves the problem correctly.
        - feedback: string, general feedback on the approach.
        - bugs: list of strings, identifying any bugs or edge cases missed.
        - optimization_tips: list of strings, suggestions to improve time/space complexity or code style.
        - corrected_code: string, a corrected or optimized version of the code (optional, mainly if there are bugs).
        
        Do not include any markdown formatting like ```json ... ```. Just the raw JSON string.
        """
        
        response_text = ""
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5
                )
                response_text = chat_completion.choices[0].message.content
            except Exception as e:
                print(f"Groq Code Review Error: {e}")

        if not response_text and self.gemini_client:
             try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                response_text = response.text
             except Exception as e:
                print(f"Gemini Code Review Error: {e}")
                
        try:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
             return {
                "is_correct": False,
                "feedback": "Error parsing AI response.",
                "bugs": [],
                "optimization_tips": []
            }

    def analyze_resume_deep(self, resume_text):
        """
        Performs a deep analysis of the resume text to provide ATS score, strengths, weakneses, etc.
        """
        prompt = f"""
        Analyze the following resume text deeply as an expert Technical Recruiter.
        
        Resume Content:
        {resume_text[:4000]}
        
        Provide a detailed analysis in JSON format with the following structure:
        {{
            "ats_score": <number 0-100 based on keyword matching and format>,
            "summary": "<2 sentence summary of the candidate profile>",
            "strengths": ["list", "of", "top", "skills/strengths"],
            "weaknesses": ["list", "of", "missing", "skills", "or", "issues"],
            "missing_skills": ["list", "of", "industry", "standard", "skills", "missing"],
            "suggested_roles": ["Role 1", "Role 2", "Role 3"]
        }}
        
        Be critical but constructive. Return ONLY valid JSON.
        """
        
        if self.groq_client:
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.4
                )
                return self._clean_and_parse_json(chat_completion.choices[0].message.content)
            except Exception as e:
                print(f"Groq Resume Analysis Error: {e}")

        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                return self._clean_and_parse_json(response.text)
            except Exception as e:
                print(f"Gemini Resume Analysis Error: {e}")
                
        # Fallback
        return {
            "ats_score": 0,
            "summary": "Could not analyze resume due to AI service error.",
            "strengths": [],
            "weaknesses": [],
            "missing_skills": [],
            "suggested_roles": []
        }

    def chat(self, messages):
        # Enhanced interviewer prompt for realistic, varied interview experience
        interviewer_prompt = """You are an experienced Technical Interviewer conducting a mock interview.

CRITICAL RULES:
1. **Ask ONE question at a time** - Never ask multiple questions in one response.
2. **NEVER repeat a question** - Track what you've already asked and always ask something NEW.
3. **Follow up on answers** - If the candidate's answer is incomplete or interesting, probe deeper.
4. **Progress naturally** - Start with introduction, then move through different topics.
5. **Be conversational** - Respond to what the candidate says before asking the next question.
6. **Vary question types** - Mix technical, behavioral, situational, and experience-based questions.
7. **IMPORTANT: Check conversation history** - Look at all previous messages to avoid repeating questions.

INTERVIEW FLOW:
- First few exchanges: Warm-up (introduce yourself, ask about their background)
- Middle: Core technical and behavioral questions based on their role/experience
- Later: Scenario-based questions, problem-solving, or deeper technical discussions
- End: Give them a chance to ask questions

QUESTION VARIETY (rotate through these):
- Technical concepts and fundamentals
- Past project experiences ("Tell me about a time when...")
- Problem-solving scenarios ("How would you handle...")
- System design or architecture (for senior roles)
- Behavioral questions (teamwork, challenges, growth)

Always be professional, encouraging, and constructive. After they answer, briefly acknowledge their response before moving to the next topic.

If the user asks non-interview questions, politely redirect: "I am designed to help only with interview-related questions. Please ask an interview-related question."
"""
        system_message = {"role": "system", "content": interviewer_prompt}
        
        
        final_messages = [system_message] + messages
        
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=final_messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7 
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"Groq Chat Error: {e}")
                return "I apologize, but I am encountering technical difficulties. Please try again."

        if self.gemini_client:
            try:
 
                full_prompt = f"{SYSTEM_PROMPT}\n\n"
                for msg in messages:
                    role = "User" if msg['role'] == 'user' else "AI"
                    full_prompt += f"{role}: {msg['content']}\n"
                full_prompt += "AI:"
                
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                print(f"Gemini Chat Error: {e}")
                return "I apologize, but I am encountering technical difficulties. Please try again."
        
        return "AI Service Unavailable."

    def extract_name(self, resume_text):
        """
        Extracts the candidate's name from the resume text using AI.
        """
        prompt = f"""
        Extract the full name of the candidate from the following resume text.
        This is typically the first large text block or the main header.
        Return ONLY the name (First and Last).
        If the text looks like a filename (e.g. maxresdefault.jpg or resume_2024), ignore it and try to find a real person's name.
        If no name is found, return "Candidate".
        
        Resume Text:
        {resume_text[:1000]}
        """
        
        if self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"Groq Name Extraction Error: {e}")

        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                print(f"Gemini Name Extraction Error: {e}")
                
        return "Candidate"

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
