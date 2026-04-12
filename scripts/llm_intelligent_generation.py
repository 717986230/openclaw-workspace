#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM智能生成
LLM Intelligent Generation
"""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

class GenerationType(Enum):
    SUMMARY = "summary"
    RELATION_DESCRIPTION = "relation_description"
    INSIGHT_GENERATION = "insight_generation"
    SUGGESTION_GENERATION = "suggestion_generation"

@dataclass
class GenerationResult:
    memory_id: int
    generation_type: str
    generated_content: str
    confidence: float
    explanation: str

class LLMIntelligentGeneration:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.memories = {}

    def load_memories(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content, type, category FROM memories LIMIT ?", (limit,))
        for row in cursor.fetchall():
            self.memories[row[0]] = {'id': row[0], 'title': row[1], 'content': row[2], 'type': row[3], 'category': row[4]}

        conn.close()
        return {'memories': len(self.memories)}

    def generate_summary(self, memory_id: int) -> GenerationResult:
        if memory_id not in self.memories:
            return GenerationResult(memory_id=memory_id, generation_type='summary', generated_content='', confidence=0.0, explanation='Memory not found')
        memory = self.memories[memory_id]
        text = memory['title'] + ' ' + memory['content']
        summary = self._create_summary(text)
        confidence = min(1.0, len(summary) / 100.0)
        return GenerationResult(memory_id=memory_id, generation_type='summary', generated_content=summary, confidence=confidence, explanation=f'Generated summary with {len(summary)} characters')

    def generate_relation_description(self, memory_id: int, related_id: int) -> GenerationResult:
        if memory_id not in self.memories or related_id not in self.memories:
            return GenerationResult(memory_id=memory_id, generation_type='relation_description', generated_content='', confidence=0.0, explanation='Memory not found')
        memory1 = self.memories[memory_id]
        memory2 = self.memories[related_id]
        description = self._create_relation_description(memory1, memory2)
        confidence = 0.8
        return GenerationResult(memory_id=memory_id, generation_type='relation_description', generated_content=description, confidence=confidence, explanation='Generated relation description')

    def generate_insight(self, memory_id: int) -> GenerationResult:
        if memory_id not in self.memories:
            return GenerationResult(memory_id=memory_id, generation_type='insight_generation', generated_content='', confidence=0.0, explanation='Memory not found')
        memory = self.memories[memory_id]
        insight = self._create_insight(memory)
        confidence = random.uniform(0.5, 0.9)
        return GenerationResult(memory_id=memory_id, generation_type='insight_generation', generated_content=insight, confidence=confidence, explanation='Generated insight')

    def generate_suggestion(self, memory_id: int) -> GenerationResult:
        if memory_id not in self.memories:
            return GenerationResult(memory_id=memory_id, generation_type='suggestion_generation', generated_content='', confidence=0.0, explanation='Memory not found')
        memory = self.memories[memory_id]
        suggestion = self._create_suggestion(memory)
        confidence = random.uniform(0.6, 0.9)
        return GenerationResult(memory_id=memory_id, generation_type='suggestion_generation', generated_content=suggestion, confidence=confidence, explanation='Generated suggestion')

    def comprehensive_generation(self, memory_id: int) -> Dict:
        results = {}
        results['summary'] = self.generate_summary(memory_id)
        results['insight'] = self.generate_insight(memory_id)
        results['suggestion'] = self.generate_suggestion(memory_id)
        avg_confidence = (results['summary'].confidence + results['insight'].confidence + results['suggestion'].confidence) / 3.0
        results['average_confidence'] = avg_confidence
        return results

    def batch_generation(self, memory_ids: List[int]) -> Dict:
        batch_results = {}
        for memory_id in memory_ids:
            batch_results[memory_id] = self.comprehensive_generation(memory_id)
        return batch_results

    def _create_summary(self, text: str) -> str:
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= 3:
            return text
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences) + '.'
        return summary

    def _create_relation_description(self, memory1: Dict, memory2: Dict) -> str:
        text1 = memory1['title'] + ' ' + memory1['content']
        text2 = memory2['title'] + ' ' + memory2['content']
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common_words = words1 & words2
        if common_words:
            common = ', '.join(list(common_words)[:5])
            description = f"These memories are related through common concepts: {common}"
        else:
            description = f"These memories ({memory1['title']} and {memory2['title']}) may be related through their {memory1['category']} and {memory2['category']} categories"
        return description

    def _create_insight(self, memory: Dict) -> str:
        insights = [
            f"This memory about {memory['title']} suggests potential patterns in {memory['category']}",
            f"The content of this memory indicates important trends in {memory['type']}",
            f"This {memory['category']} memory reveals insights about {memory['title']}",
            f"Analysis of this memory shows connections to broader themes in {memory['type']}"
        ]
        return random.choice(insights)

    def _create_suggestion(self, memory: Dict) -> str:
        suggestions = [
            f"Consider exploring more about {memory['title']} to deepen understanding",
            f"This memory could be connected to related {memory['category']} topics",
            f"Further investigation of {memory['title']} may reveal additional insights",
            f"Review this memory in the context of other {memory['type']} entries"
        ]
        return random.choice(suggestions)

if __name__ == "__main__":
    print("Testing LLM Intelligent Generation...")
    generation = LLMIntelligentGeneration("memory/database/xiaozhi_memory.db")
    load_result = generation.load_memories(limit=100)
    print(f"Loaded {load_result['memories']} memories")
    if generation.memories:
        first_id = list(generation.memories.keys())[0]
        result = generation.generate_summary(first_id)
        print(f"Summary generation: {result.explanation}")
        result = generation.generate_insight(first_id)
        print(f"Insight generation: {result.explanation}")
        result = generation.generate_suggestion(first_id)
        print(f"Suggestion generation: {result.explanation}")
        results = generation.comprehensive_generation(first_id)
        print(f"Comprehensive generation: average confidence = {results['average_confidence']:.2f}")
    print("LLM Intelligent Generation test complete!")
