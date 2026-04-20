"""
Stress Test Pool
"""

import random
import time
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class StressTest:
    test_id: str
    category: str
    intensity: int
    description: str
    duration_seconds: int
    parameters: Dict


class StressTestPool:
    """
    Stress testing scenarios
    """
    
    def __init__(self):
        self.test_categories = {
            'cpu': {
                'light': {'usage': 50, 'duration': 60},
                'medium': {'usage': 75, 'duration': 300},
                'heavy': {'usage': 95, 'duration': 600},
                'extreme': {'usage': 100, 'duration': 1800}
            },
            'memory': {
                'light': {'usage_mb': 512, 'duration': 60},
                'medium': {'usage_mb': 1024, 'duration': 300},
                'heavy': {'usage_mb': 4096, 'duration': 600},
                'extreme': {'usage_mb': 8192, 'duration': 1800}
            },
            'io': {
                'light': {'ops_per_sec': 100, 'duration': 60},
                'medium': {'ops_per_sec': 1000, 'duration': 300},
                'heavy': {'ops_per_sec': 10000, 'duration': 600},
                'extreme': {'ops_per_sec': 100000, 'duration': 1800}
            },
            'network': {
                'light': {'requests_per_sec': 100, 'duration': 60},
                'medium': {'requests_per_sec': 1000, 'duration': 300},
                'heavy': {'requests_per_sec': 10000, 'duration': 600},
                'extreme': {'requests_per_sec': 100000, 'duration': 1800}
            },
            'concurrent': {
                'light': {'connections': 100, 'duration': 60},
                'medium': {'connections': 1000, 'duration': 300},
                'heavy': {'connections': 10000, 'duration': 600},
                'extreme': {'connections': 100000, 'duration': 1800}
            },
            'combined': {
                'light': {'cpu': 30, 'mem': 256, 'io': 50, 'duration': 60},
                'medium': {'cpu': 60, 'mem': 512, 'io': 500, 'duration': 300},
                'heavy': {'cpu': 80, 'mem': 2048, 'io': 5000, 'duration': 600},
                'extreme': {'cpu': 95, 'mem': 4096, 'io': 50000, 'duration': 1800}
            }
        }
    
    def get_test(self, category: str = None, intensity: str = None) -> StressTest:
        if category is None:
            category = random.choice(list(self.test_categories.keys()))
        
        if intensity is None:
            intensity = random.choice(['light', 'medium', 'heavy', 'extreme'])
        
        if category not in self.test_categories:
            category = 'combined'
        
        params = self.test_categories[category].get(intensity, 
                   self.test_categories[category]['medium'])
        
        intensity_map = {'light': 1, 'medium': 2, 'heavy': 3, 'extreme': 4}
        
        return StressTest(
            test_id=f"STRESS-{category[:3].upper()}-{random.randint(1000,9999)}",
            category=category,
            intensity=intensity_map[intensity],
            description=f"{intensity.capitalize()} {category} stress test",
            duration_seconds=params['duration'],
            parameters=params
        )
    
    def get_suite(self, intensity: str = 'medium') -> List[StressTest]:
        return [self.get_test(cat, intensity) 
                for cat in self.test_categories.keys()]
    
    def get_full_suite(self) -> List[StressTest]:
        suite = []
        for cat in self.test_categories:
            for intensity in ['light', 'medium', 'heavy', 'extreme']:
                suite.append(self.get_test(cat, intensity))
        return suite
    
    def get_random_tests(self, count: int = 5) -> List[StressTest]:
        return [self.get_test() for _ in range(count)]
