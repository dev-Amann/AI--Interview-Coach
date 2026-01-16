-- Database Initialization Script for AI Interview Coach

CREATE DATABASE IF NOT EXISTS interview_coach;
USE interview_coach;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interview Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    job_role VARCHAR(100),
    category ENUM('Technical', 'Behavioral', 'HR') DEFAULT 'Technical',
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    avg_score DECIMAL(3,1),
    qualified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Responses Table
CREATE TABLE IF NOT EXISTS responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    question_number INT,
    question TEXT,
    answer TEXT,
    score INT,
    feedback TEXT,
    ideal_answer TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_responses_session ON responses(session_id);
