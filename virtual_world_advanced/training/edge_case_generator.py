"""
Edge Case Generator
"""

import random
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class EdgeCase:
    case_id: str
    category: str
    description: str
    difficulty: int
    parameters: Dict


class EdgeCaseGenerator:
    """
    Generate extreme and boundary test cases
    """
    
    def __init__(self):
        self.categories = {
            'security': self._generate_security_edge,
            'performance': self._generate_performance_edge,
            'data': self._generate_data_edge,
            'network': self._generate_network_edge,
            'concurrency': self._generate_concurrency_edge,
            'error': self._generate_error_edge,
        }
    
    def generate(self, category: str = None, difficulty: int = 3) -> EdgeCase:
        if category and category in self.categories:
            return self.categories[category](difficulty)
        
        # Random category
        cat = random.choice(list(self.categories.keys()))
        return self.categories[cat](difficulty)
    
    def _generate_security_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'SQL injection with encoded characters', 'params': {'type': 'sqli_encoded'}},
            {'description': 'XSS via DOM clobbering', 'params': {'type': 'xss_dom'}},
            {'description': 'Path traversal with null bytes', 'params': {'type': 'traversal_null'}},
            {'description': 'SSRF via IPv6 localhost', 'params': {'type': 'ssrf_ipv6'}},
            {'description': 'ReDoS attack pattern', 'params': {'type': 'redos'}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"SEC-{random.randint(1000,9999)}",
            category='security',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def _generate_performance_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'Process 1 billion records', 'params': {'records': 1_000_000_000}},
            {'description': 'Handle 100k concurrent connections', 'params': {'connections': 100000}},
            {'description': 'Query 100TB database', 'params': {'data_size_tb': 100}},
            {'description': 'Memory limit 8MB', 'params': {'memory_mb': 8}},
            {'description': 'Response time < 1ms', 'params': {'max_ms': 1}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"PERF-{random.randint(1000,9999)}",
            category='performance',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def _generate_data_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'Empty dataset handling', 'params': {'size': 0}},
            {'description': 'Maximum integer overflow', 'params': {'type': 'int_overflow'}},
            {'description': 'Unicode boundary strings', 'params': {'type': 'unicode_edge'}},
            {'description': 'Deeply nested JSON (100 levels)', 'params': {'depth': 100}},
            {'description': 'Circular reference data', 'params': {'type': 'circular'}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"DATA-{random.randint(1000,9999)}",
            category='data',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def _generate_network_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'Packet loss 50%', 'params': {'loss_rate': 0.5}},
            {'description': 'Latency 10 seconds', 'params': {'latency_ms': 10000}},
            {'description': 'Connection reset mid-transfer', 'params': {'type': 'reset'}},
            {'description': 'DNS timeout', 'params': {'type': 'dns_timeout'}},
            {'description': 'SSL certificate expired', 'params': {'type': 'ssl_expired'}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"NET-{random.randint(1000,9999)}",
            category='network',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def _generate_concurrency_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'Race condition in transaction', 'params': {'type': 'race'}},
            {'description': 'Deadlock scenario', 'params': {'type': 'deadlock'}},
            {'description': 'Thundering herd problem', 'params': {'type': 'thundering_herd'}},
            {'description': 'Producer-consumer imbalance', 'params': {'type': 'imbalance'}},
            {'description': 'Lock starvation', 'params': {'type': 'starvation'}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"CONC-{random.randint(1000,9999)}",
            category='concurrency',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def _generate_error_edge(self, difficulty: int) -> EdgeCase:
        cases = [
            {'description': 'Stack overflow recursion', 'params': {'type': 'stack_overflow'}},
            {'description': 'Out of memory recovery', 'params': {'type': 'oom'}},
            {'description': 'Disk full scenario', 'params': {'type': 'disk_full'}},
            {'description': 'Corrupted database', 'params': {'type': 'corrupted_db'}},
            {'description': 'Power failure simulation', 'params': {'type': 'power_fail'}},
        ]
        case = random.choice(cases)
        return EdgeCase(
            case_id=f"ERR-{random.randint(1000,9999)}",
            category='error',
            description=case['description'],
            difficulty=difficulty,
            parameters=case['params']
        )
    
    def generate_batch(self, count: int = 10) -> List[EdgeCase]:
        return [self.generate() for _ in range(count)]
