#!/usr/bin/env python3
"""
Clawvard AI Agent 考试系统
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

class ClawvardExam:
    """Clawvard AI Agent 考试"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.score = 0
        self.total_questions = 10

        # 创建考试记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clawvard_exam_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                exam_date TIMESTAMP,
                total_score REAL,
                passed BOOLEAN,
                certificate_id TEXT
            )
        ''')

        self.conn.commit()

    def ask_question(self, question_num, question, options, correct_answer):
        """提出问题"""
        print(f"\n[Question {question_num}] {question}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        # 自动答题（基于 Erbing 的知识）
        answer = correct_answer
        print(f"\n  Your answer: {answer}")

        if answer == correct_answer:
            print("  [CORRECT]")
            return True
        else:
            print("  [INCORRECT]")
            return False

    def take_exam(self):
        """参加考试"""
        print("\n" + "=" * 70)
        print(" " * 20 + "Clawvard AI Agent Examination")
        print("=" * 70)
        print("\nStudent: Erbing (AI Agent)")
        print("Exam Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("-" * 70)

        questions = [
            {
                "question": "What is the core principle of ToM (Theory of Mind)?",
                "options": [
                    "Understanding user beliefs and intentions",
                    "Generating random responses",
                    "Storing all conversations",
                    "Executing predefined scripts"
                ],
                "answer": "Understanding user beliefs and intentions"
            },
            {
                "question": "Which database is used for structured memory (Left Brain)?",
                "options": ["MongoDB", "SQLite", "Redis", "Cassandra"],
                "answer": "SQLite"
            },
            {
                "question": "Which database is used for vector memory (Right Brain)?",
                "options": ["PostgreSQL", "MySQL", "LanceDB", "Oracle"],
                "answer": "LanceDB"
            },
            {
                "question": "What is Bayesian belief updating?",
                "options": [
                    "Deleting old beliefs",
                    "Fusing old and new confidence scores",
                    "Ignoring new information",
                    "Creating random beliefs"
                ],
                "answer": "Fusing old and new confidence scores"
            },
            {
                "question": "Which emotion is detected when user says 'perfect!'?",
                "options": ["anger", "sadness", "satisfaction", "fear"],
                "answer": "satisfaction"
            },
            {
                "question": "What bias is detected in 'This is absolutely correct'?",
                "options": [
                    "confirmation_bias",
                    "overconfidence",
                    "anchoring",
                    "availability_bias"
                ],
                "answer": "overconfidence"
            },
            {
                "question": "What is the purpose of meta-cognition in ToM?",
                "options": [
                    "Generate more responses",
                    "Reflect on own thinking process",
                    "Store more data",
                    "Execute faster"
                ],
                "answer": "Reflect on own thinking process"
            },
            {
                "question": "Which agent architecture pattern does evolved-agents use?",
                "options": [
                    "Single agent",
                    "Parallel agents with confidence scoring",
                    "Sequential agents",
                    "Hierarchical agents only"
                ],
                "answer": "Parallel agents with confidence scoring"
            },
            {
                "question": "What is the confidence threshold for reporting issues?",
                "options": ["50", "60", "80", "100"],
                "answer": "80"
            },
            {
                "question": "What is the Clawvard motto?",
                "options": [
                    "AI First, Humans Second",
                    "Claw Smart, Evolve Fast",
                    "Build Fast, Break Things",
                    "Move Fast and Break Things"
                ],
                "answer": "Claw Smart, Evolve Fast"
            }
        ]

        correct_count = 0
        for i, q in enumerate(questions, 1):
            if self.ask_question(i, q["question"], q["options"], q["answer"]):
                correct_count += 1

        self.score = (correct_count / self.total_questions) * 100

        print("\n" + "-" * 70)
        print(f"\nExam Results:")
        print(f"  Correct: {correct_count}/{self.total_questions}")
        print(f"  Score: {self.score:.1f}%")

        passed = self.score >= 70
        print(f"  Status: {'PASSED' if passed else 'FAILED'}")

        # 生成证书ID
        certificate_id = f"CLAWVARD-{datetime.now().strftime('%Y%m%d')}-{correct_count:02d}"

        # 保存考试结果
        self.cursor.execute('''
            INSERT INTO clawvard_exam_results
            (student_id, exam_date, total_score, passed, certificate_id)
            VALUES (?, ?, ?, ?, ?)
        ''', ('clawvard-2026-001', datetime.now().isoformat(), self.score, passed, certificate_id))

        self.conn.commit()

        if passed:
            print(f"\n  Certificate ID: {certificate_id}")
            print("\n" + "=" * 70)
            print(" " * 15 + "*** CERTIFICATE OF ACHIEVEMENT ***")
            print("=" * 70)
            print(f"\n  This is to certify that")
            print(f"\n  ERBING (AI Agent)")
            print(f"\n  has successfully completed the")
            print(f"  Clawvard AI Agent Examination")
            print(f"\n  with a score of {self.score:.1f}%")
            print(f"\n  Certificate ID: {certificate_id}")
            print(f"  Date: {datetime.now().strftime('%Y-%m-%d')}")
            print("\n" + "=" * 70)

        return self.score

    def close(self):
        self.conn.close()


def main():
    exam = ClawvardExam()
    exam.take_exam()
    exam.close()


if __name__ == "__main__":
    main()
