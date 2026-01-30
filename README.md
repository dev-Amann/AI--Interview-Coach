# 🎯 AI Interview Coach

<div align="center">

![AI Interview Coach](https://img.shields.io/badge/AI-Interview%20Coach-6366f1?style=for-the-badge&logo=robot&logoColor=white)
![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203-orange?style=flat-square)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20AI-brightgreen?style=flat-square)

**An AI-powered interview preparation platform with real-time behavioral analysis, voice interaction, and comprehensive feedback.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](#-api-reference)

</div>

---

## ✨ Features

### 🎤 Real-Time AI Interview Mode
- **Voice-Based Interaction**: Speak naturally with the AI interviewer using speech recognition
- **AI Speech Responses**: The AI responds back audibly using text-to-speech
- **Behavioral Monitoring**: Real-time face detection, gaze tracking, and emotion analysis
- **Multi-Face Detection**: Alerts when multiple people are detected (anti-cheating)
- **Head Pose Tracking**: Monitors if you're looking away from the screen
- **Emotion Detection**: Tracks confidence, nervousness, and engagement levels
- **End Interview Analysis**: Comprehensive AI-powered performance review with scores

### 📝 Text-Based Interview Mode
- **Resume-Based Questions**: AI generates personalized questions from your resume
- **Multiple Categories**: Technical, Behavioral, and HR interview questions
- **Difficulty Levels**: Easy, Medium, and Hard question sets
- **Real-Time Evaluation**: Each answer is scored (0-10) with feedback
- **Ideal Answers**: AI provides model answers for learning
- **PDF Reports**: Download detailed interview performance reports

### 💻 Mock Coding Interview
- **Multi-Language Support**: Python, JavaScript, Java, C++, and more
- **Topic Selection**: Arrays, Strings, Trees, Graphs, Dynamic Programming, etc.
- **AI Code Review**: Get feedback on your code with suggestions
- **Problem Generation**: AI generates coding problems based on difficulty

### 📄 Resume Analysis
- **PDF & Image Support**: Upload resumes in PDF or image format
- **OCR Technology**: Extracts text from image-based resumes using Google Gemini
- **ATS Score**: Get an Applicant Tracking System compatibility score
- **Detailed Feedback**: Strengths, weaknesses, and improvement suggestions
- **Skill Extraction**: Identifies key skills from your resume

### 💬 Chat with Coach
- **Conversational AI**: Have natural conversations with your AI interview coach
- **Interview Guidance**: Get tips on answering common interview questions
- **Resume-Aware Context**: Upload your resume for personalized advice
- **Career Counseling**: Ask about career paths, skills to develop, and more
- **Instant Responses**: Real-time AI-powered responses to your queries
- **Interview-Focused**: Only answers interview-related questions to keep you on track

### 📊 Dashboard & Analytics
- **Performance Tracking**: View your interview history and scores
- **Progress Charts**: Visual representation of improvement over time
- **Session History**: Access past interview sessions and responses
- **User Stats**: Total interviews, average score, best performance

---

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI Framework |
| **Vite** | Build Tool |
| **Tailwind CSS** | Styling |
| **Clerk** | Authentication |
| **React Router** | Navigation |
| **Lucide React** | Icons |
| **React Webcam** | Camera Access |
| **MediaPipe** | Face Detection & Landmarks |
| **Web Speech API** | Voice Recognition & Synthesis |

### Backend
| Technology | Purpose |
|------------|---------|
| **Flask** | Python Web Framework |
| **Groq API** | LLM (LLaMA 3.3 70B) for AI responses |
| **Google Gemini** | OCR for resume images |
| **MySQL** | Database |
| **PyPDF2** | PDF processing |
| **ReportLab** | PDF report generation |

### AI & ML Features
| Feature | Technology |
|---------|------------|
| Question Generation | Groq (LLaMA 3.3 70B) |
| Answer Evaluation | Groq (LLaMA 3.3 70B) |
| Resume OCR | Google Gemini |
| Face Detection | MediaPipe FaceLandmarker |
| Emotion Detection | MediaPipe Face Blendshapes |
| Speech Recognition | Web Speech API |
| Text-to-Speech | Web Speech Synthesis |

---

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.9+
- MySQL 8.0+
- Groq API Key
- Google Gemini API Key
- Clerk Account (for authentication)

### 1. Clone the Repository
```bash
git clone https://github.com/dev-Amann/AI--Interview-Coach.git
cd AI--Interview-Coach
```

### 2. Backend Setup
```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
```

Edit `.env` with your credentials:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=interview_coach
```

### 3. Database Setup
```sql
CREATE DATABASE interview_coach;
```
The tables are auto-created when the server starts.

### 4. Frontend Setup
```bash
cd client

# Install dependencies
npm install

# Create .env file
echo "VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key" > .env
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd server
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

Access the app at: `http://localhost:5173`

---

## 🚀 Usage

### Real AI Interview Mode
1. Navigate to **Interview** from the Dashboard
2. Click **"Start Real AI Interview"**
3. Allow camera and microphone access
4. Complete the setup wizard (resume upload, job role selection)
5. Speak your answers - the AI will ask follow-up questions
6. Click **"End Interview"** for a comprehensive analysis

### Text-Based Interview
1. Navigate to **Interview** from the Dashboard
2. Click **"Start Text-based Interview"**
3. Upload your resume and configure settings
4. Answer questions in the text box
5. View your results with scores and feedback

### Mock Coding
1. Navigate to **Mock Coding** from the Dashboard
2. Select language, topic, and difficulty
3. Read the generated problem
4. Write and submit your code
5. Receive AI-powered code review

### Resume Analysis
1. Navigate to **Resume Analysis**
2. Upload your resume (PDF or Image)
3. View ATS score, strengths, and suggestions

---

## 🔌 API Reference

### Interview Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interview/start` | Start interview, generate questions |
| POST | `/interview/answer` | Submit answer, get evaluation |
| POST | `/interview/chat` | Real-time chat with AI |
| POST | `/interview/chat/resume` | Upload resume for chat context |
| POST | `/interview/analyze` | Get comprehensive interview analysis |
| POST | `/interview/save` | Save interview session |
| GET | `/interview/report/<session_id>` | Download PDF report |

### Coding Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interview/coding/problem` | Generate coding problem |
| POST | `/interview/coding/review` | Review submitted code |

### Resume Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/interview/resume/analyze` | Deep resume analysis |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/stats` | Get user statistics |
| GET | `/user/history` | Get interview history |

---

## 📁 Project Structure

```
AI_Interview_Coach/
├── client/                     # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── VideoPreview.jsx    # Camera + Face Detection
│   │   ├── hooks/
│   │   │   └── useSpeech.js        # Speech Recognition Hook
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # Main Dashboard
│   │   │   ├── Interview.jsx       # Interview Mode Selection
│   │   │   ├── ChatInterview.jsx   # Real-time AI Interview
│   │   │   ├── MockCoding.jsx      # Coding Practice
│   │   │   ├── ResumeAnalysis.jsx  # Resume Analyzer
│   │   │   ├── Results.jsx         # Interview Results
│   │   │   └── Setup.jsx           # Interview Setup Wizard
│   │   ├── services/
│   │   │   └── api.js              # Axios API Client
│   │   └── utils/
│   │       └── MediaPipeHelper.js  # Face Detection Utility
│   └── package.json
│
├── server/                     # Flask Backend
│   ├── routes/
│   │   ├── interview.py            # Interview API Routes
│   │   └── user.py                 # User API Routes
│   ├── services/
│   │   ├── ai_engine.py            # AI/LLM Integration
│   │   ├── database.py             # MySQL Database
│   │   ├── resume_parser.py        # PDF/Image Text Extraction
│   │   └── pdf_generator.py        # Report Generation
│   ├── app.py                      # Flask App Entry
│   └── requirements.txt
│
└── README.md
```

---

## 🗄️ Database Schema

```sql
-- Users table (synced from Clerk)
users (id, email, name, created_at)

-- Interview sessions
sessions (id, user_id, job_role, category, difficulty, avg_score, qualified, created_at)

-- Individual responses
responses (id, session_id, question_number, question, answer, score, feedback, ideal_answer)
```

---

## 🎮 Behavioral Analysis Features

The Real Interview mode includes advanced AI-powered behavioral monitoring:

| Feature | Detection Method | Alerts |
|---------|------------------|--------|
| **Face Presence** | MediaPipe FaceLandmarker | "No face detected" |
| **Multiple Faces** | Multi-face detection (3 faces) | "Multiple people detected" |
| **Gaze Tracking** | Iris landmark analysis | "Looking away from screen" |
| **Head Pose** | Nose-to-center offset | "Turned Left/Right/Up/Down" |
| **Emotions** | Face blendshapes | Confident/Thinking/Concerned/Surprised |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Aman Singh**
- GitHub: [@dev-Amann](https://github.com/dev-Amann)

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ for Infosys Springboard

</div>
