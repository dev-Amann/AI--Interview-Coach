# AI Interview Coach v2.1🎯

An intelligent, AI-powered interview practice application designed to help you master your next interview. Built with a modern tech stack (React, Flask, MySQL) and powered by advanced LLMs (Groq Llama-3 & Google Gemini).

![React](https://img.shields.io/badge/React-19.0-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Groq](https://img.shields.io/badge/AI-Groq-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

## ✨ Features

### 🤖 AI Chat Coach (New!)
- **Conversational Interface**: Chat naturally with the AI Coach.
- **Resume Context**: Upload your resume directly in chat. The AI analyzes it to ask tailored questions (Fresher vs Experienced).
- **Strict Roleplay**: The AI stays in character as a professional interviewer.

### 🏠 Modern Dashboard
- **Analytics**: Track your progress with visual charts and score trends.
- **History**: View past sessions and download detailed PDF reports.
- **Quick Actions**: Start new interviews or jump back into chat.

### � Mock Interview Session
- **Role Specific**: Choose from 12+ job roles and custom difficulty levels.
- **Real-time Feedback**: Get instant scoring (0-10) and feedback on every answer.
- **Ideal Answers**: Learn from AI-generated "Model Answers".

### 🔐 Secure & Fast
- **Authentication**: Powered by Clerk (Sign In/Up, Google Auth).
- **Performance**: Fast backend response times with Flask & connection pooling.

---

## 🛠️ Tech Stack

### Frontend (Client)
- **Framework**: React 19 + Vite
- **Styling**: TailwindCSS 4
- **Auth**: Clerk
- **Icons**: Lucide React
- **HTTP**: Axios

### Backend (Server)
- **Framework**: Flask
- **AI Models**: Groq (Llama-3.3-70b), Google Gemini 1.5 Flash
- **Database**: MySQL (Connector Python)
- **PDF Processing**: pdfplumber (Parsing), ReportLab (Generation)

---

## 📦 Installation

### Prerequisites
- Node.js (v18+)
- Python (3.11+)
- MySQL Server

### 1. Clone the Repository
```bash
git clone https://github.com/dev-Amann/AI--Interview-Coach.git
cd AI_Interview_Coach
```

### 2. Backend Setup
```bash
cd server
# Create virtual environment
python -m venv venv
# Activate (Windows)
..\venv\Scripts\activate
# Activate (Mac/Linux)
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Create `.env` file in `server/` root:**
```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=interview_coach
```

### 3. Frontend Setup
```bash
cd ../client
# Install dependencies
npm install

# Create .env.local in client/ root
echo "VITE_CLERK_PUBLISHABLE_KEY=your_clerk_key" > .env.local
```

### 4. Database Initialization
Import the `init.sql` schema into your MySQL database or run the migration scripts provided in `services/database.py`.

---

## ▶️ Usage

1. **Start Backend**:
   ```bash
   # From root
   python server/app.py
   # Runs on http://localhost:5000
   ```

2. **Start Frontend**:
   ```bash
   # From client/
   npm run dev
   # Runs on http://localhost:5173
   ```

3. **Open App**: Navigate to `http://localhost:5173` in your browser.

---

## 🤝 Contributing

Contributions are welcome!
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
