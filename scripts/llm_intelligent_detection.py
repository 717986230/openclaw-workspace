#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM智能检测
LLM Intelligent Detection
"""

import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

class DetectionType(Enum):
    SEMANTIC = "semantic"
    CONTEXT = "context"
    RELATION = "relation"
    CAUSAL = "causal"

@dataclass
class DetectionResult:
    memory_id: int
    detection_type: str
    confidence: float
    detected_entities: List[str]
    detected_relations: List[Dict]
    detected_causality: List[Dict]
    explanation: str

class LLMIntelligentDetection:
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

    def semantic_detection(self, memory_id: int) -> DetectionResult:
        if memory_id not in self.memories:
            return DetectionResult(memory_id=memory_id, detection_type='semantic', confidence=0.0, detected_entities=[], detected_relations=[], detected_causality=[], explanation='Memory not found')
        memory = self.memories[memory_id]
        text = memory['title'] + ' ' + memory['content']
        entities = self._extract_entities(text)
        confidence = min(1.0, len(entities) / 10.0)
        return DetectionResult(memory_id=memory_id, detection_type='semantic', confidence=confidence, detected_entities=entities, detected_relations=[], detected_causality=[], explanation=f'Semantic detection found {len(entities)} entities')

    def context_detection(self, memory_id: int) -> DetectionResult:
        if memory_id not in self.memories:
            return DetectionResult(memory_id=memory_id, detection_type='context', confidence=0.0, detected_entities=[], detected_relations=[], detected_causality=[], explanation='Memory not found')
        memory = self.memories[memory_id]
        text = memory['title'] + ' ' + memory['content']
        context = self._extract_context(text)
        confidence = min(1.0, len(context) / 5.0)
        return DetectionResult(memory_id=memory_id, detection_type='context', confidence=confidence, detected_entities=[], detected_relations=[], detected_causality=[], explanation=f'Context detection found {len(context)} contexts')

    def relation_detection(self, memory_id: int) -> DetectionResult:
        if memory_id not in self.memories:
            return DetectionResult(memory_id=memory_id, detection_type='relation', confidence=0.0, detected_entities=[], detected_relations=[], detected_causality=[], explanation='Memory not found')
        memory = self.memories[memory_id]
        text = memory['title'] + ' ' + memory['content']
        relations = self._extract_relations(text)
        confidence = min(1.0, len(relations) / 5.0)
        return DetectionResult(memory_id=memory_id, detection_type='relation', confidence=confidence, detected_entities=[], detected_relations=relations, detected_causality=[], explanation=f'Relation detection found {len(relations)} relations')

    def causal_detection(self, memory_id: int) -> DetectionResult:
        if memory_id not in self.memories:
            return DetectionResult(memory_id=memory_id, detection_type='causal', confidence=0.0, detected_entities=[], detected_relations=[], detected_causality=[], explanation='Memory not found')
        memory = self.memories[memory_id]
        text = memory['title'] + ' ' + memory['content']
        causality = self._extract_causality(text)
        confidence = min(1.0, len(causality) / 3.0)
        return DetectionResult(memory_id=memory_id, detection_type='causal', confidence=confidence, detected_entities=[], detected_relations=[], detected_causality=causality, explanation=f'Causal detection found {len(causality)} causal relationships')

    def comprehensive_detection(self, memory_id: int) -> Dict:
        results = {}
        results['semantic'] = self.semantic_detection(memory_id)
        results['context'] = self.context_detection(memory_id)
        results['relation'] = self.relation_detection(memory_id)
        results['causal'] = self.causal_detection(memory_id)
        avg_confidence = (results['semantic'].confidence + results['context'].confidence + results['relation'].confidence + results['causal'].confidence) / 4.0
        results['average_confidence'] = avg_confidence
        return results

    def batch_detection(self, memory_ids: List[int]) -> Dict:
        batch_results = {}
        for memory_id in memory_ids:
            batch_results[memory_id] = self.comprehensive_detection(memory_id)
        return batch_results

    def _extract_entities(self, text: str) -> List[str]:
        entities = []
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
            r'\b\w+@\w+\.\w+\b',
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\$\d+(?:,\d{3})*(?:\.\d{2})?\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        return list(set(entities))

    def _extract_context(self, text: str) -> List[str]:
        contexts = []
        context_keywords = ['because', 'since', 'due to', 'as a result', 'therefore', 'consequently', 'however', 'although', 'despite', 'in contrast']
        for keyword in context_keywords:
            if keyword in text.lower():
                contexts.append(keyword)
        return contexts

    def _extract_relations(self, text: str) -> List[Dict]:
        relations = []
        relation_patterns = [
            (r'(\w+)\s+is\s+(?:a|an)\s+(\w+)', 'is_a'),
            (r'(\w+)\s+is\s+part\s+of\s+(\w+)', 'part_of'),
            (r'(\w+)\s+is\s+related\s+to\s+(\w+)', 'related_to'),
            (r'(\w+)\s+is\s+similar\s+to\s+(\w+)', 'similar_to'),
            (r'(\w+)\s+is\s+opposite\s+of\s+(\w+)', 'opposite_of')
        ]
        for pattern, relation_type in relation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                relations.append({'type': relation_type, 'source': match[0], 'target': match[1]})
        return relations

    def _extract_causality(self, text: str) -> List[Dict]:
        causality = []
        causal_patterns = [
            (r'(\w+)\s+causes?\s+(\w+)', 'direct'),
            (r'(\w+)\s+leads?\s+to\s+(\w+)', 'direct'),
            (r'(\w+)\s+results?\s+in\s+(\w+)', 'direct'),
            (r'if\s+(\w+)\s+then\s+(\w+)', 'conditional'),
            (r'(\w+)\s+because\s+of\s+(\w+)', 'indirect')
        ]
        for pattern, causal_type in causal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                causality.append({'type': causal_type, 'cause': match[0], 'effect': match[1]})
        return causality

if __name__ == "__main__":
    print("Testing LLM Intelligent Detection...")
    detection = LLMIntelligentDetection("memory/database/xiaozhi_memory.db")
    load_result = detection.load_memories(limit=100)
    print(f"Loaded {load_result['memories']} memories")
    if detection.memories:
        first_id = list(detection.memories.keys())[0]
        result = detection.semantic_detection(first_id)
        print(f"Semantic detection: {result.explanation}")
        result = detection.context_detection(first_id)
        print(f"Context detection: {result.explanation}")
        result = detection.relation_detection(first_id)
        print(f"Relation detection: {result.explanation}")
        result = detection.causal_detection(first_id)
        print(f"Causal detection: {result.explanation}")
        results = detection.comprehensive_detection(first_id)
        print(f"Comprehensive detection: average confidence = {results['average_confidence']:.2f}")
    print("LLM Intelligent Detection test complete!")
