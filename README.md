# AI Interview Coach 🎯

An intelligent, AI-powered interview practice application with multiple pages, analytics, PDF reports, and authentication. Built with Streamlit and powered by Groq/Gemini AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 🏠 Landing Page
- **Modern UI**: Animated hero section with statistics and feature highlights.
- **User Flow**: Clear call-to-action for immediate start.

### 📝 Interview Page
- **Resume Parsing**: Upload your PDF resume for personalized questions.
- **Customizable Sessions**: Select from 12+ job roles, 3 categories (Technical, Behavioral, HR), and 3 difficulty levels.
- **AI-Powered Questions**: Dynamic questions generated using Groq/Gemini models.
- **Real-time Evaluation**: Instant feedback and scoring for every answer.
- **Ideal Answers**: Learn from model answers provided for each question.

### 📊 Analytics Dashboard
- **Performance Overview**: Summary cards for quick insights.
- **Visual Charts**: Score trends and skill distribution using Plotly.
- **AI Recommendations**: Personalized tips to improve your interview skills.

### 📄 Interview History
- **Session Tracking**: View complete history of past interviews.
- **Detailed Reviews**: Expandable views to see questions, your answers, scores, and feedback.
- **PDF Reports**: Download professional reports of your sessions.

### 🔐 Authentication
- **Secure Access**: Sign-in and Sign-up functionality.
- **User Management**: Session-based user tracking with MySQL integration.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit 1.31+ |
| **AI Models** | Groq (Llama-3.3-70b), Google Gemini |
| **Data Viz** | Plotly |
| **PDF** | ReportLab |
| **Database** | MySQL |
| **Authentication** | Custom Logic with MySQL |

## 📋 Prerequisites

- Python 3.8+
- MySQL Server (for user and history data)
- API Keys:
  - [Groq API Key](https://console.groq.com/keys)
  - [Google Gemini API Key](https://aistudio.google.com/app/apikey)

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dev-Amann/AI--Interview-Coach.git
   cd AI--Interview-Coach
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # AI API Keys
   GROQ_API_KEY=your_groq_key
   GEMINI_API_KEY=your_gemini_key
   
   # MySQL Database Configuration
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=interview_coach
   ```

5. **Setup Database**:
   Import the `init.sql` file into your MySQL database or run the query:
   ```sql
   CREATE DATABASE interview_coach;
   -- Run contents of init.sql
   ```

## ▶️ Usage

1. **Run the application**:
   ```bash
   streamlit run Home.py
   ```

2. **Open in browser**: App usually runs at `http://localhost:8501`.

3. **Workflow**:
   - **Sign Up/In**: Create an account to save your progress.
   - **Start Interview**: Upload resume -> Configure session -> Generate questions.
   - **Practice**: Answer questions and get instant feedback.
   - **Review**: Check your Dashboard for analytics and History for past sessions.

## 📂 Project Structure

```
AI_Interview_Coach/
├── Home.py                      # Main landing page
├── assets/                      # CSS and images
├── pages/
│   ├── Sign_In.py               # Authentication page
│   ├── Dashboard.py             # User analytics
│   ├── Start_Interview.py       # Main interview interface
│   └── History.py               # Session history & reports
├── services/
│   ├── ai_engine.py             # LLM integration (Groq/Gemini)
│   ├── auth.py                  # Authentication logic
│   ├── components.py            # Reusable UI components
│   ├── database.py              # MySQL database interactions
│   ├── interview_manager.py     # Interview session logic
│   ├── pdf_generator.py         # PDF report generation
│   └── resume_parser.py         # PDF resume parsing
├── init.sql                     # Database schema
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is open-source under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com) and [Google Gemini](https://ai.google.dev)
- Built with [Streamlit](https://streamlit.io)
