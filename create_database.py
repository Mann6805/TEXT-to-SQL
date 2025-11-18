import sqlite3

conn = sqlite3.connect("db/university.db")
cur = conn.cursor()

# --- Create tables ---
cur.execute("""
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    department TEXT,
    year INTEGER,
    gpa REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Professors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Courses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    credits INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    semester TEXT,
    grade TEXT,
    FOREIGN KEY(student_id) REFERENCES Students(id),
    FOREIGN KEY(course_id) REFERENCES Courses(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    id INTEGER PRIMARY KEY,
    name TEXT,
    building TEXT
)
""")

# --- Insert sample data ---

students = [
    (1, "Rahul Sharma", "rahul@example.com", "Computer Science", 3, 8.2),
    (2, "Priya Singh", "priya@example.com", "Mechanical Engineering", 2, 7.8),
    (3, "Aman Verma", "aman@example.com", "Electrical Engineering", 4, 8.9),
    (4, "Neha Gupta", "neha@example.com", "Computer Science", 1, 9.1),
]

professors = [
    (1, "Dr. Arvind Kumar", "Computer Science"),
    (2, "Dr. Meera Nair", "Mechanical Engineering"),
    (3, "Dr. Sunil Rao", "Physics"),
]

courses = [
    (1, "Data Structures", "Computer Science", 4),
    (2, "Thermodynamics", "Mechanical Engineering", 3),
    (3, "Machine Learning", "Computer Science", 4),
    (4, "Digital Circuits", "Electrical Engineering", 3),
]

departments = [
    (1, "Computer Science", "Block A"),
    (2, "Mechanical Engineering", "Block B"),
    (3, "Electrical Engineering", "Block C"),
    (4, "Physics", "Block D"),
]

enrollments = [
    (1, 1, 1, "Fall 2024", "A"),
    (2, 2, 2, "Fall 2024", "B+"),
    (3, 3, 4, "Spring 2024", "A-"),
    (4, 1, 3, "Spring 2025", "A"),
    (5, 4, 1, "Fall 2024", "A+"),
]

cur.executemany("INSERT INTO Students VALUES (?, ?, ?, ?, ?, ?)", students)
cur.executemany("INSERT INTO Professors VALUES (?, ?, ?)", professors)
cur.executemany("INSERT INTO Courses VALUES (?, ?, ?, ?)", courses)
cur.executemany("INSERT INTO Departments VALUES (?, ?, ?)", departments)
cur.executemany("INSERT INTO Enrollments VALUES (?, ?, ?, ?, ?)", enrollments)

conn.commit()
conn.close()

print("university.db created successfully!")