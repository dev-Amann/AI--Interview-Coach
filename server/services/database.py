import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.database = os.getenv("MYSQL_DATABASE", "interview_coach")
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Database Connection Error: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255),
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
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
            )
            """,
            """
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
            )
            """
        ]
        
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            for query in queries:
                cursor.execute(query)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Create Tables Error: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_user(self, user_id, email, name):
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO users (id, email, name) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE email = %s, name = %s
            """
            cursor.execute(query, (user_id, email, name, email, name))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Save User Error: {e}")
            return False
        finally:
            self.disconnect()
    
    def save_session(self, user_id, job_role, category, difficulty, avg_score, qualified, questions, answers, scores, feedback_list, ideal_answers_list):
        if not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor()
            
            session_query = """
                INSERT INTO sessions (user_id, job_role, category, difficulty, avg_score, qualified)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(session_query, (user_id, job_role, category, difficulty, avg_score, qualified))
            session_id = cursor.lastrowid
            
            for i, question in enumerate(questions):
                response_query = """
                    INSERT INTO responses (session_id, question_number, question, answer, score, feedback, ideal_answer)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                answer = answers.get(i, '')
                score = scores[i] if i < len(scores) else 0
                feedback = feedback_list[i] if i < len(feedback_list) else ''
                ideal = ideal_answers_list[i] if i < len(ideal_answers_list) else ''
                
                cursor.execute(response_query, (session_id, i + 1, question, answer, score, feedback, ideal))
            
            self.connection.commit()
            return session_id
        except Error as e:
            print(f"Save Session Error: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_user_sessions(self, user_id, limit=10):
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, job_role, category, difficulty, avg_score, qualified, created_at
                FROM sessions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            sessions = cursor.fetchall()
            return sessions
        except Error as e:
            print(f"Get Sessions Error: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_session_details(self, session_id):
        if not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            session_query = """
                SELECT id, user_id, job_role, category, difficulty, avg_score, qualified, created_at
                FROM sessions
                WHERE id = %s
            """
            cursor.execute(session_query, (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return None
            
            responses_query = """
                SELECT question_number, question, answer, score, feedback, ideal_answer
                FROM responses
                WHERE session_id = %s
                ORDER BY question_number
            """
            cursor.execute(responses_query, (session_id,))
            responses = cursor.fetchall()
            
            session['responses'] = responses
            return session
        except Error as e:
            print(f"Get Session Details Error: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_user_analytics(self, user_id):
        if not self.connect():
            return None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            stats_query = """
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(avg_score) as overall_avg_score,
                    MAX(avg_score) as best_score,
                    SUM(CASE WHEN qualified = 1 THEN 1 ELSE 0 END) as qualified_count
                FROM sessions
                WHERE user_id = %s
            """
            cursor.execute(stats_query, (user_id,))
            stats = cursor.fetchone()
            
            category_query = """
                SELECT category, AVG(avg_score) as avg_score, COUNT(*) as count
                FROM sessions
                WHERE user_id = %s
                GROUP BY category
            """
            cursor.execute(category_query, (user_id,))
            category_stats = cursor.fetchall()
            
            trend_query = """
                SELECT DATE(created_at) as date, AVG(avg_score) as avg_score
                FROM sessions
                WHERE user_id = %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """
            cursor.execute(trend_query, (user_id,))
            trend_data = cursor.fetchall()
            
            return {
                'stats': stats,
                'category_stats': category_stats,
                'trend_data': trend_data
            }
        except Error as e:
            print(f"Get Analytics Error: {e}")
            return None
        finally:
            self.disconnect()
    
    def delete_session(self, session_id, user_id):
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM sessions WHERE id = %s AND user_id = %s"
            cursor.execute(query, (session_id, user_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Delete Session Error: {e}")
            return False
        finally:
            self.disconnect()


def init_database():
    db = Database()
    return db.create_tables()


def get_user_stats(user_id):
    """Get user stats for Dashboard"""
    if not user_id:
        return None
    
    db = Database()
    if not db.connect():
        return None
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                COUNT(*) as total_interviews,
                COALESCE(AVG(avg_score), 0) as average_score,
                (SELECT job_role FROM sessions WHERE user_id = %s 
                 GROUP BY job_role ORDER BY COUNT(*) DESC LIMIT 1) as top_role
            FROM sessions
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id, user_id))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Get User Stats Error: {e}")
        return None
    finally:
        db.disconnect()


def get_user_history(user_id, limit=20):
    """Get user interview history for History page"""
    if not user_id:
        return []
    
    db = Database()
    if not db.connect():
        return []
    
    try:
        cursor = db.connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                id,
                job_role as role,
                DATE_FORMAT(created_at, '%M %d, %Y') as date,
                avg_score as score,
                qualified
            FROM sessions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Get User History Error: {e}")
        return []
    finally:
        db.disconnect()
