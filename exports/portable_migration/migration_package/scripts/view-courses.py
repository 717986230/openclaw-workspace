#!/usr/bin/env python3
"""
查看 Clawvard 课程详情
"""
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def view_courses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print(" " * 25 + "Clawvard Course Catalog")
    print("=" * 70)

    # 查询所有课程
    cursor.execute('''
        SELECT course_code, course_name, instructor, department, credits, description
        FROM clawvard_courses
        ORDER BY credits, course_code
    ''')

    courses = cursor.fetchall()

    for course in courses:
        code, name, instructor, dept, credits, desc = course

        print(f"\n{code}: {name}")
        print(f"  Department: {dept}")
        print(f"  Instructor: {instructor}")
        print(f"  Credits: {credits}")
        print(f"  Description: {desc}")

        # 课程大纲（基于课程代码）
        if code == "CLAW101":
            print(f"  Syllabus:")
            print(f"    - Week 1-2: Agent Architecture Fundamentals")
            print(f"    - Week 3-4: Prompt Engineering Basics")
            print(f"    - Week 5-6: Tool Integration")
            print(f"    - Week 7-8: Final Project")

        elif code == "CLAW201":
            print(f"  Syllabus:")
            print(f"    - Week 1-2: Multi-Agent Communication Patterns")
            print(f"    - Week 3-4: Task Decomposition Strategies")
            print(f"    - Week 5-6: Conflict Resolution")
            print(f"    - Week 7-8: Swarm Intelligence")

        elif code == "CLAW301":
            print(f"  Syllabus:")
            print(f"    - Week 1-2: Memory Architecture Design")
            print(f"    - Week 3-4: SQLite + LanceDB Integration")
            print(f"    - Week 5-6: Belief Tracking Systems")
            print(f"    - Week 7-8: Memory Optimization")

        elif code == "CLAW401":
            print(f"  Syllabus:")
            print(f"    - Week 1-2: Theory of Mind Foundations")
            print(f"    - Week 3-4: Belief-Desire-Intention Models")
            print(f"    - Week 5-6: Emotion Recognition")
            print(f"    - Week 7-8: Social Context Analysis")

        elif code == "CLAW501":
            print(f"  Syllabus:")
            print(f"    - Week 1-2: Self-Improvement Architectures")
            print(f"    - Week 3-4: Meta-Learning for Agents")
            print(f"    - Week 5-6: Autonomous Evolution")
            print(f"    - Week 7-8: Safety and Ethics")

        print("-" * 70)

    conn.close()

    print("\n" + "=" * 70)
    print("Total Courses:", len(courses))
    print("Total Credits Available:", sum(c[4] for c in courses))
    print("=" * 70 + "\n")


if __name__ == "__main__":
    view_courses()
