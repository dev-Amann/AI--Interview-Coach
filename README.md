# AI Interview Coach 🤖

An intelligent, AI-powered interview practice application built with Streamlit. This tool helps candidates prepare for technical interviews by generating personalized questions based on their resume and providing real-time feedback on their answers.

## 🚀 Features

-   **Resume Analysis**: Extracts text from PDF resumes to understand the candidate's background.
-   **Dynamic Question Generation**: Creates 5 relevant technical questions tailored to the selected job role and resume content.
-   **Real-time AI Feedback**: Evaluates answers instantly, providing a score (0-10), constructive feedback, and an ideal answer.
-   **Dual AI Engine Support**:
    -   Primary: **Groq** (Llama-3.3-70b-versatile) for ultra-fast performance.
    -   Fallback: **Google Gemini** (Gemini-1.5-Flash) ensures reliability if Groq is unavailable.
-   **Comprehensive Summary**: Displays a detailed performance report with average score and qualification status (Qualified/Not Qualified) at the end of the session.
-   **Interactive UI**: Clean and user-friendly interface built with Streamlit.

## 🛠️ Tech Stack

-   **Python 3.x**
-   **Streamlit**: Frontend framework
-   **pdfplumber**: PDF text extraction
-   **Groq API**: High-speed LLM inference
-   **Google Gemini API**: Generative AI model
-   **Python-dotenv**: Environment variable management

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

-   Python 3.8 or higher
-   API Keys:
    -   [Groq Cloud API Key](https://console.groq.com/keys)
    -   [Google AI Studio (Gemini) API Key](https://aistudio.google.com/app/apikey)

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/dev-Amann/AI--Interview-Coach.git
    cd AI--Interview-Coach
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
    *Note: You can provide either one or both. The app prioritizes Groq.*

## ▶️ Usage

1.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

2.  **Start the Interview**:
    -   Open the provided local URL (usually `http://localhost:8501`).
    -   Upload your **Resume (PDF)** in the sidebar.
    -   Select your desired **Job Role** (e.g., Python Developer, Data Analyst).
    -   Click **"Start Interview"**.

3.  **During the Interview**:
    -   Answer each question in the text area provided.
    -   Click **"Submit Answer"** to get instant scores and feedback.
    -   Proceed to the next question until finished.

4.  **Review Results**:
    -   At the end, view your **Average Score** and **Qualification Status**.
    -   Review the full summary of questions, your answers, and ideal responses.

## 📂 Project Structure

```
AI_Interview_Coach/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not pushed to git)
└── services/
    ├── ai_engine.py        # Logic for interacting with Groq/Gemini APIs
    └── resume_parser.py    # PDF text extraction logic
```

## 🤝 Contributing

Contributions are welcome! Please feel free to fork the repository and submit pull requests.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
