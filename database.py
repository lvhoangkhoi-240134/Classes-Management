import sqlite3
from datetime import datetime

def get_connection():
    return sqlite3.connect('learnloop.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS classes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, invite_code TEXT, teacher_name TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, invite_code TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT, session_date TEXT, 
                  accuracy REAL, score INTEGER, total INTEGER, time_taken TEXT)''')
    
    conn.commit()
    conn.close()

def check_code_exists(code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM classes WHERE invite_code=?", (code,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def create_class(name, teacher_name, code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO classes (name, invite_code, teacher_name) VALUES (?, ?, ?)", (name, code, teacher_name))
    conn.commit()
    conn.close()

def get_teacher_classes(teacher_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, invite_code FROM classes WHERE teacher_name=?", (teacher_name,))
    classes = [{"name": row[0], "code": row[1]} for row in c.fetchall()]
    conn.close()
    return classes

def enroll_student(student_name, invite_code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM enrollments WHERE student_name=? AND invite_code=?", (student_name, invite_code))
    if not c.fetchone():
        c.execute("INSERT INTO enrollments (student_name, invite_code) VALUES (?, ?)", (student_name, invite_code))
        conn.commit()
    conn.close()

def get_students_in_class(invite_code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT student_name FROM enrollments WHERE invite_code=?", (invite_code,))
    students = [row[0] for row in c.fetchall()]
    conn.close()
    return students

def save_session(student_name, accuracy, score, total, time_taken):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO sessions (student_name, session_date, accuracy, score, total, time_taken)
                 VALUES (?, ?, ?, ?, ?, ?)''', (student_name, date_str, accuracy, score, total, time_taken))
    conn.commit()
    conn.close()

def get_student_sessions(student_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT session_date, score, total, accuracy, time_taken FROM sessions WHERE student_name=?", (student_name,))
    sessions = [{"session_date": row[0], "score": row[1], "total": row[2], "accuracy": row[3], "time_taken": row[4]} 
                for row in c.fetchall()]
    conn.close()
    return sessions
