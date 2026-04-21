#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM智能问答
LLM Intelligent Q&A
"""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class QAType(Enum):
    QA = "qa"
    DIALOGUE = "dialogue"
    KNOWLEDGE_GRAPH_QA = "knowledge_graph_qa"
    MULTI_TURN = "multi_turn"

@dataclass
class QAResult:
    question: str
    answer: str
    confidence: float
    sources: List[int]
    explanation: str

class LLMIntelligentQA:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.memories = {}
        self.dialogue_history = {}

    def load_memories(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content, type, category FROM memories LIMIT ?", (limit,))
        for row in cursor.fetchall():
            self.memories[row[0]] = {'id': row[0], 'title': row[1], 'content': row[2], 'type': row[3], 'category': row[4]}

        conn.close()
        return {'memories': len(self.memories)}

    def answer_question(self, question: str, max_results: int = 5) -> QAResult:
        relevant_memories = self._find_relevant_memories(question, max_results)
        if not relevant_memories:
            return QAResult(question=question, answer='No relevant information found', confidence=0.0, sources=[], explanation='No relevant memories found')
        answer = self._generate_answer(question, relevant_memories)
        confidence = min(1.0, len(relevant_memories) / max_results)
        sources = [m['id'] for m in relevant_memories]
        explanation = f'Answer generated from {len(relevant_memories)} relevant memories'
        return QAResult(question=question, answer=answer, confidence=confidence, sources=sources, explanation=explanation)

    def dialogue(self, user_id: str, message: str) -> QAResult:
        if user_id not in self.dialogue_history:
            self.dialogue_history[user_id] = []
        self.dialogue_history[user_id].append({'role': 'user', 'content': message})
        relevant_memories = self._find_relevant_memories(message, max_results=3)
        if not relevant_memories:
            answer = "I don't have relevant information about that."
            confidence = 0.0
        else:
            answer = self._generate_dialogue_response(message, relevant_memories, self.dialogue_history[user_id])
            confidence = min(1.0, len(relevant_memories) / 3.0)
        self.dialogue_history[user_id].append({'role': 'assistant', 'content': answer})
        sources = [m['id'] for m in relevant_memories]
        explanation = f'Dialogue response generated from {len(relevant_memories)} relevant memories'
        return QAResult(question=message, answer=answer, confidence=confidence, sources=sources, explanation=explanation)

    def knowledge_graph_qa(self, question: str, max_results: int = 5) -> QAResult:
        relevant_memories = self._find_relevant_memories(question, max_results)
        if not relevant_memories:
            return QAResult(question=question, answer='No relevant information found', confidence=0.0, sources=[], explanation='No relevant memories found')
        answer = self._generate_knowledge_graph_answer(question, relevant_memories)
        confidence = min(1.0, len(relevant_memories) / max_results)
        sources = [m['id'] for m in relevant_memories]
        explanation = f'Knowledge graph answer generated from {len(relevant_memories)} relevant memories'
        return QAResult(question=question, answer=answer, confidence=confidence, sources=sources, explanation=explanation)

    def multi_turn_qa(self, user_id: str, question: str, max_results: int = 5) -> QAResult:
        if user_id not in self.dialogue_history:
            self.dialogue_history[user_id] = []
        context = self._build_context(self.dialogue_history[user_id])
        enhanced_question = f"Context: {context}\n\nQuestion: {question}"
        relevant_memories = self._find_relevant_memories(enhanced_question, max_results)
        if not relevant_memories:
            answer = "I don't have relevant information about that in the current context."
            confidence = 0.0
        else:
            answer = self._generate_multi_turn_answer(question, relevant_memories, context)
            confidence = min(1.0, len(relevant_memories) / max_results)
        self.dialogue_history[user_id].append({'role': 'user', 'content': question})
        self.dialogue_history[user_id].append({'role': 'assistant', 'content': answer})
        sources = [m['id'] for m in relevant_memories]
        explanation = f'Multi-turn answer generated from {len(relevant_memories)} relevant memories with context'
        return QAResult(question=question, answer=answer, confidence=confidence, sources=sources, explanation=explanation)

    def clear_dialogue_history(self, user_id: str):
        if user_id in self.dialogue_history:
            self.dialogue_history[user_id] = []

    def _find_relevant_memories(self, question: str, max_results: int) -> List[Dict]:
        relevant_memories = []
        question_lower = question.lower()
        for memory_id, memory in self.memories.items():
            text = memory['title'] + ' ' + memory['content']
            text_lower = text.lower()
            if self._keyword_match(question_lower, text_lower):
                relevance_score = self._compute_relevance(question_lower, text_lower)
                relevant_memories.append({**memory, 'relevance_score': relevance_score})
        relevant_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_memories[:max_results]

    def _generate_answer(self, question: str, relevant_memories: List[Dict]) -> str:
        if not relevant_memories:
            return "No relevant information found."
        top_memory = relevant_memories[0]
        answer = f"Based on the information about {top_memory['title']}: {top_memory['content']}"
        if len(relevant_memories) > 1:
            additional = f" Additionally, related information includes: " + "; ".join([m['title'] for m in relevant_memories[1:3]])
            answer += additional
        return answer

    def _generate_dialogue_response(self, message: str, relevant_memories: List[Dict], history: List[Dict]) -> str:
        if not relevant_memories:
            return "I don't have relevant information about that."
        top_memory = relevant_memories[0]
        response = f"Regarding {top_memory['title']}: {top_memory['content']}"
        return response

    def _generate_knowledge_graph_answer(self, question: str, relevant_memories: List[Dict]) -> str:
        if not relevant_memories:
            return "No relevant information found."
        answer = f"Based on the knowledge graph, here's what I found about your question: "
        answer += "; ".join([f"{m['title']}: {m['content'][:100]}..." for m in relevant_memories[:3]])
        return answer

    def _generate_multi_turn_answer(self, question: str, relevant_memories: List[Dict], context: str) -> str:
        if not relevant_memories:
            return "I don't have relevant information about that in the current context."
        top_memory = relevant_memories[0]
        answer = f"Building on our conversation, regarding {top_memory['title']}: {top_memory['content']}"
        return answer

    def _build_context(self, history: List[Dict]) -> str:
        context_parts = []
        for turn in history[-5:]:
            if turn['role'] == 'user':
                context_parts.append(f"User: {turn['content']}")
            else:
                context_parts.append(f"Assistant: {turn['content']}")
        return " | ".join(context_parts)

    def _keyword_match(self, query: str, text: str) -> bool:
        keywords = query.split()
        for keyword in keywords:
            if keyword in text:
                return True
        return False

    def _compute_relevance(self, query: str, text: str) -> float:
        query_words = set(query.split())
        text_words = set(text.split())
        if not query_words:
            return 0.0
        intersection = len(query_words & text_words)
        return intersection / len(query_words)

if __name__ == "__main__":
    print("Testing LLM Intelligent Q&A...")
    qa = LLMIntelligentQA("memory/database/xiaozhi_memory.db")
    load_result = qa.load_memories(limit=100)
    print(f"Loaded {load_result['memories']} memories")
    result = qa.answer_question("What is python?")
    print(f"Q&A: {result.explanation}")
    result = qa.dialogue("user1", "Tell me about python")
    print(f"Dialogue: {result.explanation}")
    result = qa.knowledge_graph_qa("What is python?")
    print(f"Knowledge graph Q&A: {result.explanation}")
    result = qa.multi_turn_qa("user1", "What about machine learning?")
    print(f"Multi-turn Q&A: {result.explanation}")
    print("LLM Intelligent Q&A test complete!")
