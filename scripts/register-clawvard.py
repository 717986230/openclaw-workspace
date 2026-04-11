#!/usr/bin/env python3
"""
注册虾佛大学 Clawvard
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def register_clawvard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 clawvard_students 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clawvard_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_id TEXT UNIQUE,
            major TEXT,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            notes TEXT
        )
    ''')

    # 创建 clawvard_courses 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clawvard_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            instructor TEXT,
            department TEXT,
            credits INTEGER,
            description TEXT
        )
    ''')

    # 创建 clawvard_enrollments 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clawvard_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course_code TEXT,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            grade TEXT,
            status TEXT DEFAULT 'enrolled',
            FOREIGN KEY (student_id) REFERENCES clawvard_students(student_id),
            FOREIGN KEY (course_code) REFERENCES clawvard_courses(course_code)
        )
    ''')

    # 注册学生 xl
    try:
        cursor.execute('''
            INSERT INTO clawvard_students (student_name, student_id, major, notes)
            VALUES (?, ?, ?, ?)
        ''', ('xl', 'clawvard-2026-001', 'AI Agent Systems', '创始人，二饼的主人'))

        print("[OK] 学生注册成功！")
        print(f"   学生姓名: xl")
        print(f"   学号: clawvard-2026-001")
        print(f"   专业: AI Agent Systems")
        print(f"   状态: 创始人")
    except sqlite3.IntegrityError:
        print("[WARN] 学生已注册，跳过")

    # 添加初始课程
    courses = [
        ('CLAW101', 'Introduction to AI Agents', 'Erbing', 'Agent Systems', 3, 'AI Agent 基础入门'),
        ('CLAW201', 'Multi-Agent Orchestration', 'Erbing', 'Agent Systems', 4, '多 Agent 协作与编排'),
        ('CLAW301', 'Memory Systems Architecture', 'Erbing', 'Cognitive Systems', 4, '记忆系统架构设计'),
        ('CLAW401', 'Theory of Mind for AI', 'Erbing', 'Cognitive Systems', 5, 'AI 心智模型理论'),
        ('CLAW501', 'Self-Evolving Agents', 'Erbing', 'Advanced Studies', 5, '自进化 Agent 研究'),
    ]

    for course in courses:
        try:
            cursor.execute('''
                INSERT INTO clawvard_courses (course_code, course_name, instructor, department, credits, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', course)
        except sqlite3.IntegrityError:
            pass

    print("\n[课程] 可选课程:")
    cursor.execute("SELECT course_code, course_name, credits FROM clawvard_courses")
    for code, name, credits in cursor.fetchall():
        print(f"   {code}: {name} ({credits} 学分)")

    conn.commit()
    conn.close()

    print("\n[欢迎] 欢迎来到虾佛大学 Clawvard！")
    print("   校训: Claw Smart, Evolve Fast")

if __name__ == "__main__":
    register_clawvard()
