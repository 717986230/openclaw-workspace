#!/usr/bin/env python3
"""
查询 Clawvard 学生信息
"""
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def query_student():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查询学生信息
    cursor.execute("SELECT * FROM clawvard_students WHERE student_id = 'clawvard-2026-001'")
    student = cursor.fetchone()

    if student:
        print(f"Student ID: {student[2]}")
        print(f"Name: {student[1]}")
        print(f"Major: {student[3]}")
        print(f"Status: {student[5]}")
        print(f"Enrolled: {student[4]}")

    # 查询课程
    cursor.execute("SELECT COUNT(*) FROM clawvard_courses")
    course_count = cursor.fetchone()[0]
    print(f"\nAvailable Courses: {course_count}")

    conn.close()

if __name__ == "__main__":
    query_student()
