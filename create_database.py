import os
import sqlite3

os.makedirs("db", exist_ok=True)
DB_PATH = "db/university.db"


def create_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        department TEXT,
        year INTEGER,
        gpa REAL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Professors (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Courses (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        credits INTEGER
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Enrollments (
        id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        semester TEXT,
        grade TEXT,
        FOREIGN KEY(student_id) REFERENCES Students(id),
        FOREIGN KEY(course_id) REFERENCES Courses(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        id INTEGER PRIMARY KEY,
        name TEXT,
        building TEXT
    )""")

    # Sample data
    students = [
        (1, "Rahul Sharma", "rahul@example.com", "Computer Science", 3, 8.2),
        (2, "Priya Singh", "priya@example.com", "Mechanical Engineering", 2, 7.8),
        (3, "Aman Verma", "aman@example.com", "Electrical Engineering", 4, 8.9),
        (4, "Neha Gupta", "neha@example.com", "Computer Science", 1, 9.1),
        (5, "Sanjay Patel", "sanjay@example.com", "Computer Science", 2, 8.5)
    ]

    professors = [
        (1, "Dr. Arvind Kumar", "Computer Science"),
        (2, "Dr. Meera Nair", "Mechanical Engineering"),
        (3, "Dr. Sunil Rao", "Physics")
    ]

    courses = [
        (1, "Data Structures", "Computer Science", 4),
        (2, "Thermodynamics", "Mechanical Engineering", 3),
        (3, "Machine Learning", "Computer Science", 4),
        (4, "Digital Circuits", "Electrical Engineering", 3)
    ]

    departments = [
        (1, "Computer Science", "Block A"),
        (2, "Mechanical Engineering", "Block B"),
        (3, "Electrical Engineering", "Block C"),
        (4, "Physics", "Block D")
    ]

    enrollments = [
        (1, 1, 1, "Fall 2024", "A"),
        (2, 2, 2, "Fall 2024", "B+"),
        (3, 3, 4, "Spring 2024", "A-"),
        (4, 1, 3, "Spring 2025", "A"),
        (5, 4, 1, "Fall 2024", "A+"),
        (6, 5, 1, "Fall 2024", "A")
    ]

    # Insert
    cur.executemany("INSERT OR IGNORE INTO Students VALUES (?, ?, ?, ?, ?, ?)", students)
    cur.executemany("INSERT OR IGNORE INTO Professors VALUES (?, ?, ?)", professors)
    cur.executemany("INSERT OR IGNORE INTO Courses VALUES (?, ?, ?, ?)", courses)
    cur.executemany("INSERT OR IGNORE INTO Departments VALUES (?, ?, ?)", departments)
    cur.executemany("INSERT OR IGNORE INTO Enrollments VALUES (?, ?, ?, ?, ?)", enrollments)

    conn.commit()
    conn.close()
    print("Database created at", DB_PATH)


if __name__ == "__main__":
    create_db()